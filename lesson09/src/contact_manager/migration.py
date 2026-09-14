# migration.py
# 这个模块定义 Migration 类：负责把「旧版本数据」转换成「当前版本数据」。
#
# 它的职责边界：
#   - 纯数据转换：输入 (version, data)，输出 (version, data)
#   - 不读磁盘、不写磁盘、不产生副作用
#   - 只处理「数据形状」的变化，不关心数据存在 JSON 还是 SQLite
#
# 谁调用它？Storage.load()。当磁盘上的版本 ≠ 当前版本时，
# Storage 把解析出来的数据交给 Migration，拿到当前版本后再原子写回。

from typing import Any
# 用于类型注解：Any 表示「这里的数据是任意结构」。
# 因为 Migration 处理的是「刚解析出来的原始数据」，
# 在真正校验前，它的形状还不确定，用 Any 比 list[dict] 更诚实。

from contact_manager.protocols import (
    ContactIdGenerator,
    ContactIdGenerationError,
)
# 从协议层导入两个东西：
#
#   ContactIdGenerator      —— 端口：生成 ID 的能力。
#                              Migration 依赖它，但不依赖具体实现。
#                              具体用 UUID 还是序列号，由组装层注入。
#
#   ContactIdGenerationError —— 端口契约：ID 生成失败时抛的异常。
#                              Migration 捕获它，转成 MigrationError。
#
# 注意：Migration 只 import 协议，不 import id_generator.py 里的
# 具体实现（UuidContactIdGenerator）。这是依赖倒置：
# 高层（Migration）依赖抽象（Protocol），低层（具体实现）也依赖抽象。

CURRENT_VERSION = 2
# 当前程序支持的数据版本号。
#
# 这个常量是「版本链的终点」：
#   Migration.migrate() 会把任何旧版本数据推进到这个版本为止。
#   Storage.save() 永远写这个版本。
#   Storage.load() 读到这个版本就跳过迁移。
#
# 将来支持 v3 时，改这里为 3，并在 migrate() 里补一条 v2 → v3 的分支。
# 其余代码（Storage、ContactService、UI）一行不改。

class MigrationError(Exception):
    """数据迁移失败。"""
    pass
# Migration 对外暴露的「唯一异常类型」。
#
# 为什么要统一成一种异常？
#   调用方（Storage.load）只需要 catch MigrationError 一种，
#   就能覆盖所有迁移失败的情况：
#     - 不支持的版本（比如数据是 v5，当前程序只到 v2）
#     - 版本高于当前程序
#     - ID 生成失败
#     - 数据结构异常（KeyError、TypeError 等）
#   这些内部差异，都在 migrate() 里被包装成 MigrationError，
#   并通过 `from e` 保留原始异常链，排查时仍能看到根因。

class Migration:
    # 定义迁移器。它的职责是：把某个版本的数据转换成当前版本的数据。
    # 它是「格式转换」的执行者，不碰磁盘、不做 I/O。
    def __init__(self, id_generator: ContactIdGenerator):
        # 构造函数：创建 Migration 实例时，必须传入一个「ID 生成器」。
        #
        # 类型注解 ContactIdGenerator 表示：任何满足这个接口的对象都行，
        # 比如 UuidIdGenerator（生产用）、SeqIdGenerator（测试用）。
        # Migration 不关心它是哪种，只要求它「能生成 ID」。
        #
        # 这就是依赖注入：ID 生成策略不是写死在 Migration 里，
        # 而是由外部在组装时决定，再传进来。
        self._id_generator = id_generator
        # 把外部传进来的生成器存到实例上（下划线前缀表示「内部私有」）。
        #
        # 为什么要存起来？
        # 因为迁移过程中会遇到「v1 的联系人没有 contact_id」这种情况，
        # 那时 Migration 需要调用 self._id_generator.new_id() 来补一个 ID。
        #
        # 注意：Migration 只是「使用」这个生成器，
        # 它不负责决定「用 UUID 还是别的」——那是组装层的事。

    def migrate(
        self,
        version: int,
        data: list[dict[str, Any]],
    ) -> tuple[int, list[dict[str, Any]]]:
        """将指定版本的数据迁移到当前版本。"""
        # 参数：
        #   version —— 传入数据「当前是哪个版本」
        #   data    —— 该版本的数据本体（这里是 contacts 列表）
        #
        # 返回：
        #   (version, data) —— 迁移后的新版本号 + 新数据
        #
        # 为什么把 version 也返回？
        #   因为调用方（Storage）需要知道「现在拿到的是不是当前版本」。
        #   返回元组让「版本号」和「数据」始终成对出现，避免调用方自己去猜。
        try:
            # 用 while 循环实现「版本链」：
            #   只要还没到当前版本，就一步一步往上推。
            #   v1 → v2 → v3 → ... → CURRENT_VERSION
            #
            # 这里目前只实现了 v1 → v2，但结构已经为将来留好：
            #   加 v3 时，只需在这里补一个 `elif version == 2:` 分支。
            while version < CURRENT_VERSION:
                if version == 1:
                    # 执行实际的格式转换：v1 的联系人 → v2 的联系人
                    # 注意：这里只改「数据形状」，不涉及磁盘。
                    data = self._migrate_v1_to_v2(data)
                    # 转换成功，版本号前进一格，循环继续判断
                    version = 2
                else:
                    # 走到这里说明：version < CURRENT_VERSION，
                    # 但没有对应的迁移分支（比如 CURRENT_VERSION=3，
                    # 数据是 v2，却没有 v2→v3 的代码）。
                    # 这是「代码缺陷」，必须显式报错，不能静默返回旧数据
                    raise MigrationError(
                        f"不支持从版本 {version} 迁移"
                    )

            # 循环结束后，version 必然 >= CURRENT_VERSION。
            # 如果 > CURRENT_VERSION，说明数据来自「更新版本的程序」，
            # 当前程序不认识它——不能硬猜，必须报错
            if version > CURRENT_VERSION:
                raise MigrationError(
                    f"数据版本 {version} 高于当前版本 {CURRENT_VERSION}"
                )
            # 到这里：version == CURRENT_VERSION，数据已是当前版本。
            return version, data

        except MigrationError:
            # 迁移错误原样抛出，不做二次包装。
            # 因为它的信息（"不支持从版本 X 迁移"）已经足够具体，
            # 再包一层反而会丢失细节。
            raise
        except ContactIdGenerationError as e:
            # ID 生成失败的原始异常，来自注入的 _id_generator。
            # 在这里转成 MigrationError，并保留原因（`from e`）。
            # 好处：调用方只需捕获 MigrationError 一种异常，
            # 同时通过 __cause__ 仍能追溯到根因。
            raise MigrationError("迁移过程中无法生成联系人 ID") from e
        except Exception as e:
            # 兜底：任何未预期的异常（KeyError、TypeError 等）
            # 统一包装成 MigrationError，并保留原始异常链。
            # 目的：Migration 对外只暴露一种异常类型，
            # 调用方不必逐个 catch 内部可能抛出的各种异常
            raise MigrationError("数据迁移失败") from e

    def _migrate_v1_to_v2(
        self,
        data: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        # 下划线前缀：内部方法，不属于对外契约。
        # 输入 v1 的 contacts 列表，输出 v2 的 contacts 列表。

        migrated_data = []
        # 用新列表承载结果，不原地修改传入的 data。
        # 这是「纯函数」的一部分：不产生副作用，调用方手里的旧数据不受影响。

        for item in data:
            try:
                # 为这条 v1 联系人生成一个新的 contact_id。
                # 注意：这里用的是 self._id_generator，也就是构造时注入进来的。
                contact_id = self._id_generator.generate()
            except ContactIdGenerationError:
                # 原样抛出，交给上层 migrate() 统一包装成 MigrationError。
                # 这里不处理，是为了让「ID 生成失败」的语义保持单一。
                raise

            migrated_data.append(
                {
                    # v2 新增字段：contact_id
                    # 这是 v1 → v2 的核心变化——给原本没有 ID 的联系人补上 ID。
                    "contact_id": contact_id,
                    # 直接搬运的字段（v1 和 v2 都有）
                    "name": item["name"],
                    "phone": item["phone"],
                    # v2 新增的可选字段：
                    # 用 .get() 而不是 ["email"]，
                    # 因为 v1 里可能没有这两个字段，缺失时给 None。
                    "email": item.get("email"),
                    "remark": item.get("remark"),
                }
            )

        return migrated_data