# Python 系统学习综合档案

版本：v4.0  
更新时间：2026-09-02

---

# 第一部分：Session Log（教师交接日志）

## 一、课程定位

课程名称：

**Python 系统化学习（从零基础到工程开发）**

当前状态：

- ✅ 第一阶段：Python 基础语法 —— 完成
- ✅ 第二阶段：数据结构、文件、JSON、工程设计、通讯录 V3 —— 完成
- ✅ 第三阶段：Module、import、模块设计、模块化通讯录 —— 完成
- ✅ 第四阶段：Class、Object、Method、封装、OOP 基础设计 —— 完成
- ✅ 第五阶段（前半）：深入封装、property、Protocol 接口、异常体系、三层架构、脏标记 —— 完成（lesson05）

下一阶段：

➡ **第六阶段：继承、多态、Composition vs Inheritance、依赖注入与可测试性**

最终目标：

不是单纯学习 Python 语法，而是建立完整的软件工程能力。

重点包括：

- 软件设计思想
- Python 设计哲学
- 可维护代码
- 工程目录结构
- 面向对象
- Git
- 数据库
- Web 开发
- 真实项目架构

---

# 二、教学风格（必须保持）

## 1. 教师身份

始终作为资深计算机语言教师。

不要代替学生完成代码。

不要直接公布答案。

重点培养：

> 理解能力 ＞ 记忆能力

---

## 2. 教学方式

坚持苏格拉底式教学。

优先：

- 提问
- 引导
- 比较方案
- 分析优缺点
- 验证学生理解

而不是直接告诉答案。

---

## 3. 每节课固定流程

```text
【进度总结】
      ↓
【教学内容】
      ↓
【设计思想】
      ↓
【练习】
      ↓
等待学生回答
      ↓
分析回答
      ↓
继续下一知识点
```

---

## 4. 课程特点

课程不是普通 Python 教程。

而是：

> **Python + 软件设计课程**

任何语法都必须回答：

> 为什么需要它？

> 它解决了什么设计问题？

重点从：

> “怎么写”

逐渐转向：

> “为什么这样设计”

---

## 5. 教学重点

学生特别喜欢讨论：

- 为什么
- Python 为什么这样设计
- 软件架构
- 抽象
- Ownership
- 模块边界
- API 设计
- 封装
- 对象之间的关系
- 可维护性

因此教学应该：

- 少讲死记语法
- 多讲设计动机
- 多比较方案
- 多分析未来扩展影响

---

## 6. 课程节奏

一次只引入一个核心概念。

不要一次引入大量新概念。

每个知识点都应该包含：

- 为什么存在
- 解决什么问题
- 如何使用
- 设计思想
- 常见错误
- 实际项目中的应用
- 练习

---

# 三、学生特点

学生：

- 喜欢追问“为什么”
- 喜欢讨论设计而不仅仅是语法
- 能够分析多个方案
- 已经具备一定工程思维
- 喜欢抽象、架构、Ownership、API 设计
- 不喜欢死记语法
- 希望理解 Python 设计背后的原因

教学时应避免：

> “记住这样写就可以。”

而应该解释：

> “Python 为什么选择这样设计？”

---

# 四、当前项目：Contact Manager

当前项目：

**联系人管理系统**

经历：

```text
V1
↓
基础菜单

V2
↓
函数化

V3
↓
dict 数据模型
JSON
文件读写
工程目录
Module 拆分

V4
↓
Class
Object
ContactBook
Contact
OOP

V5
↓
深入封装（私有属性 + property 只读）
Protocol 接口与依赖倒置
自定义异常层次
UI 独立成层
脏标记（改过才保存）
入口守卫
```

---

# 五、当前架构

当前已经形成三层结构（Contact Manager V5，lesson05）：

```text
main.py（入口 + 协调）
    │
    ├──► ui.run(contact_book)
    │        │  只依赖 ContactBook 暴露的方法
    │        ▼
    │    ContactBook（业务核心）
    │        │ owns
    │        ▼
    │    Contact × N
    │
    └──► JsonStorage("contacts.json")
             ▲
             │ 实现 Storage 协议
        Storage (Protocol)
             load() / save()
```

数据流：

```text
启动：contacts.json ──load──► list[dict] ──from_data──► ContactBook
退出：ContactBook ──to_data──► list[dict] ──save──► contacts.json（仅当 is_dirty）
```

职责：

```text
main.py
    ↓
初始化存储
异常处理
保存协调
入口守卫

ui.py
    ↓
菜单、输入、输出
不 import contacts / storage
只依赖 ContactBook 暴露的方法

ContactBook
    ↓
管理 Contact 集合
维护快照（is_dirty / mark_saved）

Contact
    ↓
管理单个联系人
验证自己的数据
管理自己的数据转换

storage.py
    ↓
Storage 协议（接口规范）
JsonStorage 实现（文件持久化）
自定义异常层次
```

---

# 六、第四阶段最重要的设计思想

## 1. 为什么 Module 最终不足

Module 天然适合：

```text
一份状态
+
一组操作
```

例如：

```python
contacts = []
```

Module 可以很好地拥有这一份状态。

但是如果需要：

```text
normal
vip
blacklist
company
```

多个拥有相同结构、相同行为、但状态完全独立的实体：

Module 会开始变得笨重。

例如：

```python
VIP_contacts = []
Normal_contacts = []

def add_VIP_contacts():
    ...

def add_Normal_contacts():
    ...
```

虽然可以实现功能，但：

- 方法会不断重复
- API 会不断增加
- 每增加一种对象就需要修改代码
- 很难表达“这些对象本质上属于同一种类型”

因此需要 Object。

---

# 七、Object 的真正含义

Object 不是一个 ID。

Object 是：

> **真正拥有自己状态，并拥有操作该状态行为的实体。**

例如：

```text
normal
    ↓
ContactBook 实例
    ↓
自己的 contacts

vip
    ↓
ContactBook 实例
    ↓
自己的 contacts
```

两个实例：

- 共享方法代码
- 拥有独立状态

这也是为什么 Python 不把 Object 简单设计成一个 ID。

---

# 八、为什么需要统一的对象语法

我们之前设计过：

```python
object_pool = {}
i = 0

def create_address_book():
    object_pool[i] = {i: []}
    return i + 1
```

这种设计虽然能够模拟对象：

```python
normal = create_address_book()
vip = create_address_book()

add(normal, "张三")
```

但使用方式不自然。

真正的面向对象接口希望表达：

```python
normal.add("张三")
vip.add("李四")
```

这样可以让：

> 对象本身拥有行为。

因此 Python 最终采用：

```text
对象.方法()
```

这种统一语法。

---

# 九、为什么需要 self

多个对象共享同一份方法代码：

```text
ContactBook
├── add_contact()
├── delete_contact()
└── show_contacts()
```

但是：

```text
normal
vip
blacklist
```

需要操作不同状态。

因此调用：

```python
normal.add_contact(...)
```

时，需要自动把：

```text
normal
```

传给共享的方法。

于是：

```python
def add_contact(self, person):
```

中的：

```text
self
```

表示：

> 当前收到方法调用的实例。

例如：

```python
normal.add_contact(person)
```

此时：

```text
self → normal
```

而：

```python
vip.add_contact(person)
```

此时：

```text
self → vip
```

`self` 不会永久保存某个实例。

每次方法调用时，它都指向当前调用者。

---

# 十、Class 与 Instance

理解：

```python
ContactBook
```

是一个 Class。

而：

```python
ContactBook()
```

是调用 Class 创建实例。

例如：

```python
normal = ContactBook()
```

表示：

```text
ContactBook
    │
    │ 创建
    ▼
normal
```

`normal` 绑定的是一个 ContactBook 实例。

---

# 十一、type 与 Class

Python 中：

```python
ContactBook
```

本身也是一个对象。

它的类型通常是：

```python
type
```

可以理解为：

```text
type
 ↓
创建 Class 对象
 ↓
ContactBook
 ↓
创建 Instance
 ↓
normal
```

因此：

```text
type
    ↓
ContactBook Class
    ↓
normal Instance
```

这是 Python 对象模型的重要基础。

---

# 十二、类属性与实例属性

类属性：

```python
class ContactBook:
    contacts = []
```

属于 Class。

实例属性：

```python
class ContactBook:
    def __init__(self):
        self.contacts = []
```

属于具体实例。

---

## 对比

| | 类属性 | 实例属性 |
|---|---|---|
| Ownership | Class | Instance |
| 生命周期 | 通常与 Class 相同 | 与 Instance 生命周期相关 |
| 是否共享 | 所有实例共享 | 每个实例独立 |
| 适合 | 共享状态 | 个体状态 |

---

# 十三、为什么 contacts 必须是实例属性

错误：

```python
class ContactBook:
    contacts = []
```

那么：

```python
book1 = ContactBook()
book2 = ContactBook()
```

访问：

```python
book1.contacts
book2.contacts
```

如果实例自身没有 `contacts`：

Python 会继续到 Class 查找。

因此两个实例最终使用同一个 list。

例如：

```python
book1.contacts.append("张三")
```

实际上修改的是 Class 的：

```python
ContactBook.contacts
```

于是：

```python
book2.contacts
```

也会看到：

```text
张三
```

正确：

```python
class ContactBook:
    def __init__(self):
        self.contacts = []
```

此时：

```text
book1.contacts
book2.contacts
```

分别是两个独立 list。

---

# 十四、Ownership

核心原则：

> 数据属于谁，谁就应该拥有最了解该数据的行为。

例如：

```text
Contact
├── name
├── phone
├── from_dict()
└── to_dict()
```

Contact 最了解自己的数据。

因此：

```text
dict → Contact
```

应该属于 Contact。

以及：

```text
Contact → dict
```

也应该属于 Contact。

---

# 十五、Contact 类

当前设计：

```python
class Contact:
    def __init__(self, name, phone):
        self.name = name
        self.phone = phone

    @classmethod
    def from_dict(cls, data):
        name = data["name"]
        phone = data["phone"]
        return cls(name, phone)

    def to_dict(self):
        return {
            "name": self.name,
            "phone": self.phone
        }
```

---

# 十六、为什么 name 和 phone 是实例属性

因为：

```text
Contact1.name → 张三
Contact2.name → 李四
```

每个联系人拥有自己的名字。

如果写成类属性：

```python
class Contact:
    name = ""
```

那么所有 Contact 都会共享这个属性。

因此：

```python
self.name
self.phone
```

才表达了：

> 每一个 Contact 都拥有自己的状态。

---

# 十七、@classmethod 与 cls

`from_dict()` 的任务是：

```text
dict
 ↓
创建 Contact
```

但是此时还不存在 Contact 实例。

所以不能依赖：

```python
contact.from_dict(...)
```

而应该：

```python
Contact.from_dict(data)
```

因此使用：

```python
@classmethod
```

其中：

```python
cls
```

代表当前 Class。

例如：

```python
@classmethod
def from_dict(cls, data):
    name = data["name"]
    phone = data["phone"]
    return cls(name, phone)
```

内部完成：

1. 从 dict 提取数据
2. 调用 Class 创建实例

---

# 十八、Alternative Constructor

普通构造：

```python
Contact(name, phone)
```

另外可以：

```python
Contact.from_dict(data)
```

两者最终都产生 Contact 实例。

因此：

```text
Contact(...)
```

和：

```text
Contact.from_dict(...)
```

可以理解为两种不同的对象创建入口。

---

# 十九、ContactBook

当前核心结构：

```python
class ContactBook:
    def __init__(self):
        self.contacts = []
```

ContactBook 拥有：

```text
contacts
```

因此负责：

- 添加联系人
- 删除联系人
- 管理联系人集合
- 加载联系人
- 导出联系人数据

---

# 二十、ContactBook 的 to_data()

正确结构：

```python
def to_data(self):
    result = []

    for item in self.contacts:
        result.append(item.to_dict())

    return result
```

执行过程：

```text
ContactBook
    │
    ▼
contacts
    │
    ├── Contact → to_dict()
    ├── Contact → to_dict()
    ├── Contact → to_dict()
    └── Contact → to_dict()
    │
    ▼
list[dict]
```

必须等待所有联系人转换完成之后才能：

```python
return result
```

---

# 二十一、Contact.to_dict() 与 ContactBook.to_data() 的区别

`Contact.to_dict()`：

```text
只处理一个 Contact
```

因此：

```python
return {
    "name": self.name,
    "phone": self.phone
}
```

可以直接返回。

而：

```python
ContactBook.to_data()
```

需要：

```text
遍历整个集合
```

所以必须：

```text
for
 ↓
全部处理
 ↓
return
```

---

# 二十二、from_data()

`ContactBook.from_data()` 的语义：

> 使用数据恢复当前 ContactBook 的状态。

因此：

```python
def from_data(self, data):
    self.contacts.clear()

    for item in data:
        person = Contact.from_dict(item)
        self.contacts.append(person)
```

这里先：

```python
self.contacts.clear()
```

表示：

> 这次操作是“恢复”，不是“追加”。

如果未来需要追加数据，应设计语义不同的方法，例如：

```text
add_from_data()
```

而不是让一个方法同时承担两种相反语义。

---

# 二十三、Object Composition

当前结构：

```text
ContactBook
    │
    ├── Contact
    ├── Contact
    └── Contact
```

即：

> 一个对象拥有其他对象。

这是 Object Composition（组合）的基础。

ContactBook 不需要知道 Contact 内部所有实现。

它只需要依赖 Contact 提供的接口：

```python
item.to_dict()
```

---

# 二十四、Storage 与 Domain 解耦

之前讨论过：

不应该：

```python
storage.save_contacts(book.contacts)
```

因为 Storage 因此知道：

```text
ContactBook 有 contacts 属性
```

更好的方向：

```python
storage.save_contacts(book.to_data())
```

Storage 只接收：

```text
可持久化的数据
```

而不需要知道：

```text
ContactBook
Contact
contacts
name
phone
```

---

# 二十五、加载过程

推荐理解为：

```text
JSON
 ↓
storage
 ↓
list[dict]
 ↓
ContactBook.from_data()
 ↓
Contact.from_dict()
 ↓
Contact instances
```

职责：

```text
Storage
    文件 ↔ 基础数据

Contact
    dict ↔ Contact

ContactBook
    管理 Contact 集合
```

---

# 二十六、为什么 ContactBook 不应该了解 Contact 的内部结构

不应该：

```python
result.append({
    "name": item.name,
    "phone": item.phone
})
```

应该：

```python
result.append(item.to_dict())
```

因为前者暴露了 Contact 的内部表示。

假设未来 Contact 增加：

```text
email
address
birthday
company
```

那么 Contact 自己修改：

```python
to_dict()
```

即可。

ContactBook 不需要了解这些变化。

这体现：

- 封装
- 高内聚
- 低耦合
- 隐藏实现
- 开闭原则

---

# 二十七、行为 Ownership

我们进一步讨论了：

> 谁应该负责“描述 Contact”？

结论：

> Contact 自己最了解自己的状态，因此 Contact 应该负责描述自己。

但是：

> Contact 不应该直接负责 UI 展示。

更好的设计思想：

```text
Contact
    ↓
描述自己
    ↓
返回结果
    ↓
调用者决定怎么使用
```

而不是：

```text
Contact
    ↓
直接 print()
```

---

# 二十八、为什么应该返回结果，而不是直接 print()

如果 Contact 直接：

```python
print(...)
```

那么 Contact 就知道：

> 调用者需要终端输出。

这会造成 UI 耦合。

如果返回描述结果：

```text
Contact
 ↓
description
```

调用者可以：

```text
Terminal
GUI
Web
Log
File
```

分别处理。

因此：

> **对象负责提供能力，而不是决定调用者如何使用能力。**

---

# 二十九、单一职责

当前设计逐渐形成：

```text
main
    → UI / 程序流程

ContactBook
    → 管理 Contact 集合

Contact
    → 管理单个联系人

storage
    → 文件持久化
```

每个对象尽量只负责自己的职责。

---

# 三十、开闭原则

核心：

> 对扩展开放，对修改封闭。

不是说：

> 代码永远不能修改。

而是：

> 面对新需求时，应尽量通过扩展新的行为或实现，而不是不断修改已经稳定的核心代码。

例如：

Contact 增加属性时：

```text
Contact
    ↓
修改自己的转换逻辑
```

而不是：

```text
ContactBook
    ↓
不断修改内部实现
```

---

# 三十一、软件设计原则累计

## 职责设计

1. 一个函数尽量只做一件事。
2. 修改状态与返回结果尽量分离。
3. 修改对象的方法通常返回 `None`。
4. 返回新对象的方法不要修改原对象。
5. 状态应归属于拥有它的对象或模块。
6. UI 不负责业务。
7. Storage 不负责业务。
8. Main 负责流程协调。
9. 对象负责与自身状态高度相关的行为。

---

## 数据设计

1. dict 可以表示简单实体数据。
2. list 表示集合。
3. 数据模型优先于功能。
4. 尽量隐藏内部表示。
5. 对象拥有自己的状态。
6. 数据与最了解这些数据的行为应该尽量靠近。

---

## Module 设计

1. 一个 Module 表达一个领域。
2. Module 可以拥有状态与行为。
3. Module 应提供稳定 API。
4. Module 间尽量解耦。
5. Main 负责协调依赖。
6. import 最好不要产生业务副作用。

---

## Object 设计

1. Object 是状态 + 行为的实体。
2. Object 不是 ID。
3. 同一 Class 创建的实例共享方法代码。
4. 每个实例拥有自己的实例状态。
5. `self` 表示当前调用方法的实例。
6. 对象应隐藏自己的内部实现。
7. 行为应尽量靠近其操作的数据。
8. 对象提供能力，但不决定调用者如何使用结果。

---

## Ownership

1. 数据属于拥有它的对象。
2. 与数据高度相关的行为也应该靠近数据。
3. 外部尽量通过接口操作数据。
4. 不要让外部依赖对象内部表示。
5. Ownership 比单纯参数传递更稳定。

---

## Python 思想

1. Module 是第一层封装。
2. Object 是第二层封装。
3. 可变对象优先原地修改。
4. 保持对象 Identity。
5. API 是契约。
6. Readability Counts。
7. Explicit is better than implicit。
8. Python 倾向使用统一、明确的对象模型。

---

# 第三十二部分：第四阶段最终理解

第四阶段最重要的不是：

```python
class
self
__init__
```

这些语法本身。

而是理解：

> **为什么需要 Object。**

完整逻辑：

```text
Module
 ↓
适合一份状态

但是程序需要大量独立实体
 ↓
Module 开始笨重

需要：
相同结构
相同行为
不同状态
 ↓
Object
 ↓
Class
 ↓
Instance
```

最终形成：

```text
Class
    ↓
定义对象的共同结构与行为

Instance
    ↓
拥有独立状态

Method
    ↓
操作当前实例状态

self
    ↓
指向当前实例

Encapsulation
    ↓
隐藏内部实现

Ownership
    ↓
让行为靠近数据
```

---

# 第三十三部分：当前 Contact Manager V4 架构

目标架构：

```text
                    main.py
                       │
                       │
                       ▼
                 ContactBook
                       │
                 owns contacts
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       Contact       Contact      Contact
          │            │            │
          ├── name     ├── name     ├── name
          ├── phone    ├── phone    ├── phone
          │            │            │
          ├── to_dict()
          ├── from_dict()
          │
          ▼
       list[dict]
          │
          ▼
      storage.py
          │
          ▼
    contacts.json
```

职责边界：

```text
main
    ↓
用户交互 + 程序生命周期 + 协调

ContactBook
    ↓
联系人集合

Contact
    ↓
单个联系人

storage
    ↓
文件读写
```

---

# 第三十四部分：第五阶段前半（lesson05）—— 分层架构与设计思想

## 本阶段完成内容

lesson05 在 lesson04 基础上完成架构重构：

- 深入封装：`_contacts` / `_name` / `_phone` 私有属性
- `@property` 只读属性（只有 getter，没有 setter）
- `@staticmethod` 数据验证（构造时验证，数据进入系统前就不合法）
- `__len__` / `__iter__`：让对象融入 Python 迭代协议
- Storage Protocol（协议 = 接口规范，依赖倒置）
- 自定义异常层次：`StorageError → StorageNotFoundError / StorageDataCorruptedError`
- 异常链 `raise ... from e`（保留根因）
- UI 独立成层：ui.py（不 import 业务与存储模块）
- 脏标记：`is_dirty` 快照对比 + `mark_saved()`
- 程序入口守卫：`if __name__ == "__main__":`

---

## 本阶段最重要的设计思想

### 1. 为什么需要 Protocol（依赖倒置）

main 直接使用 JsonStorage 也能工作，但依赖方向是：

```text
main ──► JsonStorage（具体实现）
```

一旦换成 SQLite / 内存存储，main 必须修改。

正确方向：依赖抽象，不依赖实现：

```text
main ──► Storage（协议）
            ▲
            │ 实现
        JsonStorage
```

main 只认识“会 load / save 的东西”，任何满足协议的对象都能被替换进来。

### 2. 异常层次：把底层异常翻译成业务异常

storage 不让 `json.JSONDecodeError`、`OSError` 直接穿透到 main：

```text
json.JSONDecodeError ──翻译──► StorageDataCorruptedError
OSError              ──翻译──► StorageError
文件不存在            ──────► StorageNotFoundError
```

main 只需要 `except StorageError` 就能兜住所有存储问题；
`raise ... from e` 保留原始异常，调试时不丢根因。

### 3. 脏标记：由数据自己回答“要不要保存”

```text
_saved_data    上次保存时的快照
is_dirty       当前状态 != 快照
mark_saved()   保存成功后更新快照
```

好处：

- 改过才写盘
- 改回原样则不写（语义正确）
- ContactBook 不需要知道 Storage 的存在

### 4. UI 成层：print 是界面的事

L3 曾把 print 写进 ContactBook（UI 泄漏进业务层），L5 完成纠正：

```text
ui.py   菜单 / input / print
        只依赖 len(book) / for book / book.add_contact(...)
        不认识 storage，也不 import contacts
```

未来换 GUI，业务层与存储层一行不用改。

### 5. 入口守卫

```python
if __name__ == "__main__":
    main()
```

同一个文件既能当脚本直接运行，又能被安全导入；
只有“直接运行”时才启动程序。

---

# 第三十五部分：已掌握内容

## 第一阶段：Python 基础

- [x] 变量
- [x] 对象绑定
- [x] 类型
- [x] list
- [x] tuple
- [x] dict
- [x] if
- [x] while
- [x] for
- [x] function
- [x] 参数
- [x] return
- [x] mutable / immutable
- [x] `==` 与 `is`

---

## 第二阶段：数据与工程

- [x] 文件读写
- [x] JSON
- [x] dumps
- [x] loads
- [x] dump
- [x] load
- [x] 序列化
- [x] 反序列化
- [x] 数据模型
- [x] 程序生命周期
- [x] 持久化
- [x] 模块职责
- [x] 异常边界
- [x] Contact Manager V3

---

## 第三阶段：Module

- [x] Module
- [x] import
- [x] Module Object
- [x] Module Cache
- [x] import 顺序
- [x] 模块状态
- [x] Ownership
- [x] API Design
- [x] Dependency
- [x] Interface
- [x] 可变对象设计
- [x] 模块化 Contact Manager

---

## 第四阶段：Object / OOP

- [x] Object
- [x] Class
- [x] Instance
- [x] `self`
- [x] `__init__`
- [x] 实例属性
- [x] 类属性
- [x] 生命周期
- [x] Ownership
- [x] Method
- [x] `@classmethod`
- [x] `cls`
- [x] Alternative Constructor
- [x] Contact
- [x] ContactBook
- [x] Composition 基础
- [x] dict ↔ Object
- [x] Object ↔ Data
- [x] Serialization 边界
- [x] 高内聚
- [x] 低耦合
- [x] 单一职责
- [x] 开闭原则
- [x] 隐藏实现

---

## 第五阶段（前半）：封装 / 接口 / 分层架构

- [x] `_` 私有属性约定
- [x] `@property` 只读属性
- [x] `@staticmethod` 与构造时验证
- [x] `__len__` / `__iter__` 迭代协议
- [x] Protocol 抽象接口
- [x] 依赖倒置（依赖协议而非实现）
- [x] 自定义异常层次
- [x] 异常链 `raise ... from e`
- [x] 异常边界（存储层翻译异常）
- [x] 脏标记 / 快照（is_dirty / mark_saved）
- [x] 分层架构（UI / 业务 / 存储）
- [x] 程序入口守卫
- [x] Contact Manager V5

---

# 第三十六部分：当前仍需学习

第五阶段（后半）：

- [ ] 对象之间的协作（深化）
- [ ] Composition（深化）
- [ ] 对象之间的 Ownership（深化）
- [ ] 继承
- [ ] 多态
- [ ] Composition 与 Inheritance 的比较
- [ ] 依赖注入与可测试性
- [ ] 更复杂的 OOP 架构

（封装、property、Dependency、接口设计、抽象接口已在前半完成，
见第三十五部分勾选清单。）

后续阶段：

- [ ] Git
- [ ] 数据库
- [ ] SQL
- [ ] Web
- [ ] Flask / Django
- [ ] 项目工程化
- [ ] 测试
- [ ] 调试
- [ ] 软件架构
- [ ] 完整项目

---

# 第三十七部分：第六阶段交接

## 下一阶段主题

**继承、多态、Composition vs Inheritance、依赖注入与可测试性**

不要从大量新语法开始。

应该从当前 Contact Manager V5 继续。

---

## 推荐教学顺序

### 1. 封装 ✅（lesson05 已完成）

回答：

> 为什么仅仅把数据放进 Class 还不够？

---

### 2. `property` ✅（lesson05 已完成）

回答：

> 如果外部不能随意修改内部状态，那么应该如何提供受控访问？

---

### 3. 对象协作

当前：

```text
ContactBook
    ↓
Contact
```

进一步研究：

```text
对象 A
    ↓
调用
    ↓
对象 B
```

重点理解：

> 对象之间应该如何合作，而不是互相暴露内部状态。

---

### 4. Composition

深入：

```text
ContactBook
    ↓
owns
    ↓
Contact
```

研究：

> 一个对象拥有另一个对象时，Ownership 应该如何设计？

---

### 5. Dependency ✅（lesson05 已完成 Protocol 部分）

研究：

> 对象需要另一个对象提供能力时，依赖应该指向哪里？

---

### 6. 继承

不要先讲：

```python
class VIPContact(Contact):
```

而是先回答：

> 为什么需要继承？

> 什么情况下继承反而是错误的？

---

### 7. 多态

回答：

> 如果 ContactBook 不应该知道具体 Contact 类型，那么它如何与不同类型对象协作？

---

### 8. Composition vs Inheritance

最终比较：

```text
Composition
    vs
Inheritance
```

重点讨论：

> 哪一种更容易维护？

> 哪一种耦合更低？

> 什么情况下应该使用哪一种？

---

### 9. 依赖注入与可测试性

回答：

> Protocol 已经定义了接口，如何让“可替换的实现”真正进入构造过程？

> 为什么“能注入”是“能测试”的前提？

---

# 第三十八部分：第六阶段教学原则

必须继续保持：

> **不要为了学习语法而学习语法。**

任何新语法必须从：

```text
问题
 ↓
设计需求
 ↓
为什么现有方案不够
 ↓
Python 提供什么机制
 ↓
语法
 ↓
实践
```

开始。

---

# 第三十九部分：下一次课程起点

下一次不要重新讲：

- 什么是 Class / Instance / self / `__init__` / `@classmethod`
- 封装与 `_` 私有属性约定
- `@property` 与受控访问
- Protocol 与依赖倒置
- 自定义异常层次与异常边界

这些已经掌握。

直接从：

> **“ContactBook 已经能通过 Storage 协议与任何实现协作。那么，什么时候才真正需要继承？与 Composition 相比，继承的代价是什么？”**

开始。

然后继续使用 Contact Manager 作为实验项目。

---

# 第四十部分：整体课程进度

当前：

```text
第一阶段  Python 基础
████████████████████ 100%

第二阶段  数据结构 / 文件 / JSON / 工程
████████████████████ 100%

第三阶段  Module / API / Ownership
████████████████████ 100%

第四阶段  Class / Object / OOP
████████████████████ 100%

第五阶段  封装 / 接口 / 分层架构（前半）
████████████░░░░░░░░ 60%

第六阶段  继承 / 多态 / Composition vs Inheritance
░░░░░░░░░░░░░░░░░░░░ 0%
```

当前整体课程处于：

> **分层架构已成型，正在从“会设计对象”进入“继承、多态与对象协作深化阶段”。**

---

# 第四十一部分：教学总原则

始终保持：

> 理解 > 记忆

> 为什么 > 怎么写

> 设计 > 语法

> 实践 > 理论

> 高内聚 > 随意拆分

> 低耦合 > 直接访问内部数据

> Ownership > 到处传递状态

> API > 暴露实现

> 可维护性 > 短期代码量

最终目标不是：

> “会写 Python。”

而是：

> **能够使用 Python 独立设计、实现、调试和维护真实的软件系统。**