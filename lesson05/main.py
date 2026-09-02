import ui
import contacts
from storage import (
    JsonStorage,                        # 导入JSON文件存储类
    StorageNotFoundError,               # 导入"存储文件未找到"异常类
    StorageDataCorruptedError,          # 导入"存储数据损坏"异常类
    StorageError,                       # 导入"存储操作失败"通用异常类
)

def main():
    # 程序的主入口函数,负责：初始化存储、加载数据、创建通讯录、启动界面、保存数据

    # ==================== 第1步：初始化存储对象 ====================
    # 创建一个JsonStorage对象，指定数据保存的文件名为 "contacts.json"
    # 这个对象负责把联系人数据保存到文件，以及从文件读取数据
    storage = JsonStorage("contacts.json")

    # ==================== 第2步：尝试加载已保存的数据 ====================
    try:                               # 尝试执行可能会出错的代码
        data = storage.load()          # 从 "contacts.json" 文件中读取数据
                                       # 如果文件存在且格式正确，data会是一个列表（list）,列表中的每个元素是一个字典（dict），代表一个联系人
    except StorageNotFoundError:       # 如果文件不存在，触发异常 StorageNotFoundError，执行这里的代码
        print("未找到存储文件，将创建新的通讯录。")
        data = []                      # 将数据初始化为空列表，表示没有任何联系人
    except StorageDataCorruptedError as e:    # 如果文件存在但内容损坏（如JSON格式错误），会触发这个异常
        print(f"数据损坏：{e}")
        return                         # 直接退出程序，因为数据无法恢复

    # ==================== 第3步：创建通讯录对象 ====================
    # ContactBook 是通讯录的核心类，负责管理所有联系人
    # 这里先创建一个空的通讯录对象（还没有任何联系人）
    normal = contacts.ContactBook()

    # ==================== 第4步：将加载的数据恢复到通讯录对象中 ====================
    # from_data() 方法会将前面加载的 data（列表）转换成通讯录中的联系人
    # 如果 data 中的数据格式不符合要求（比如缺少必要字段），会抛出 ValueError
    try:
        normal.from_data(data)
    except ValueError as e:                             # 捕获数据不符合业务规则的异常
        print(f"错误：联系人数据不符合业务规则: {e}")
        return                                          # 直接退出程序，因为数据无法使用

    # ==================== 第5步：启动用户界面 ====================
    # ui.run() 会启动图形界面或命令行界面，让用户操作通讯录
    # 这个函数会一直运行，直到用户选择退出
    # 用户对通讯录的所有操作（增删改）都会反映在 normal 对象中
    ui.run(normal)

    # ==================== 第6步：根据是否需要保存，决定是否写入文件 ====================
    # is_dirty 是一个布尔值（True/False）
    # 如果用户在操作过程中修改了通讯录，is_dirty 会被设为 True
    # 如果没有修改，is_dirty 保持 False，就不需要保存（节省性能）
    if normal.is_dirty:
        try:
            # to_data() 方法将通讯录中的所有联系人转换为列表（适合保存的格式）
            # save() 方法将这个列表保存到 "contacts.json" 文件中
            data = normal.to_data()
            storage.save(data)                             # 先保存到文件 save(data: list[dict]) -> None
            normal.mark_saved()                            # 保存成功后才标记,保存当前状态的快照
            print("退出程序，数据已保存")
        except StorageError as e:                          # 如果保存失败（如磁盘已满、权限不足等）
            print(f"错误：保存失败，数据未保存: {e}")

    else:
         # 如果通讯录没有被修改过，就不需要保存，直接退出
        print("退出程序，数据无变动")

if __name__ == "__main__":
    main()