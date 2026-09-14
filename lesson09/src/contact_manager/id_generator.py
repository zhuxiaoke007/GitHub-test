# id_generator.py
# 这个模块提供「联系人 ID 生成器」的具体实现。
# 它是一个 Infrastructure 层的组件，被注入给 Migration 使用。
# Migration 只知道「有个能生成 ID 的东西」，不知道这里用的是 UUID。

import uuid
from contact_manager.protocols import ContactIdGenerationError
# 从协议层导入「ID 生成失败」的专用异常类型。
#
# 为什么要专门定义这个异常，而不是直接抛 ValueError？
#   1. 调用方（Migration）可以精确捕获它，转成 MigrationError，
#      而不用去猜底层到底抛了什么。
#   2. 它是「ID 生成」这个契约的一部分——任何实现这个接口的生成器，
#      失败时都应该抛这个异常，调用方的处理逻辑因此统一。
#   3. 把「接口」和「异常」放在 protocols 里，意味着：
#      「生成 ID 可能失败」是这个抽象的一部分，不是某个实现的细节。

# ============ 实现 ============
# 这个文件是「实现」文件，对应的「协议/接口」定义在 protocols 里。

class UuidContactIdGenerator:
    # 一个具体的 ContactIdGenerator 实现。
    # 它满足 protocols 里 ContactIdGenerator 的接口：提供一个 generate() 方法。
    # 之所以要有这个具体类、而不是直接写 uuid.uuid4()，是为了：
    #   - 可替换：测试时换成 SeqContactIdGenerator，生产时用这个。
    #   - 可注入：Migration 通过构造函数接收它，不写死。

    def generate(self) -> str:
        # 接口要求的唯一方法：生成并返回一个联系人 ID。
        # 返回类型是 str——因为 ID 最终要写进 JSON / SQLite，

        try:
            return str(uuid.uuid4())
            # uuid.uuid4() 返回一个 uuid.UUID 对象；
            # str(...) 把它转成标准的 36 字符字符串，形如：
            #   "f47ac10b-58cc-4372-a567-0e02b2c3d479"
            #
            # 转换是必要的：Migration 处理的是纯 dict/list 数据，
            # 里面存 UUID 对象的话，json.dump 会失败（UUID 不可直接序列化）。
            # 所以「在生成器的边界上就转成 str」，让下游拿到的是普通字符串。

        except Exception as e:
            # 理论上 uuid.uuid4() 几乎不会失败（不依赖外部资源），
            # 但这里仍然做兜底捕获，目的是：
            #   1. 把「底层可能抛出的任意异常」统一成 ContactIdGenerationError，
            #      让调用方只需处理一种异常类型。
            #   2. 保留原始异常链（from e），排查时仍能看到根因。
            #
            # 这是「异常归一化」的常见做法：
            #   内部实现可能抛各种异常，对外只暴露契约规定的那个。
            raise ContactIdGenerationError("无法生成联系人 ID") from e