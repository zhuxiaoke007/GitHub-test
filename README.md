# GitHub-test

Python 学习项目 — 命令行通讯录管理程序

## 目录结构

```
.
├── lesson01/          # 第一课：基础版通讯录（单文件实现）
│   └── main.py        #   列表存储联系人，含添加/查看/删除/退出
└── lesson02/          # 第二课：模块化 + JSON 持久化
    ├── main.py        #   程序入口与菜单交互
    ├── contacts.py    #   联系人数据操作（增删查改）
    └── storage.py     #   联系人 JSON 文件读写
```

## 运行方法

```bash
# 第一课：基础版
python lesson01/main.py

# 第二课：模块化版（自动读写 contacts.json）
python lesson02/main.py
```

操作说明：菜单输入 `1` 添加联系人，`2` 查看，`3` 删除，`0` 退出。

## 课程要点

- **lesson01**：函数定义与调用、列表操作、`while` 循环、用户输入
- **lesson02**：模块拆分（入口/业务/存储）、字典数据结构、JSON 序列化与文件读写（`encoding="utf-8"`、`ensure_ascii=False`）

## CI

GitHub Actions 自动执行代码检查（ruff）与功能测试，详见 `.github/workflows/ci.yml`。
