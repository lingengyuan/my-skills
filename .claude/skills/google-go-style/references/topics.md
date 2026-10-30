# 官方主题索引

按当前问题读取对应章节，结合原文的条件、例外和建议等级作出决策。

## 原则

- [文档等级与范围](index.md#about)：区分核心规范、具体裁决和建议。
- [原则优先级](guide.md#principles)：清晰性、简单性、简洁性、可维护性、一致性。
- [最少机制](guide.md#least-mechanism)：评估新增依赖、封装和抽象是否必要。
- [局部一致性](guide.md#local-consistency)：判断新代码与已有实现的关系。

## 命名、格式与组织

| 问题 | 官方章节 |
| --- | --- |
| 格式与长行 | [Formatting](guide.md#formatting)、[Line length](guide.md#line-length) |
| 包名、接收器、缩写与重复命名 | [Naming](decisions.md#naming)、[Avoid repetition](best-practices.md#function-name-repetition) |
| 注释与导出符号文档 | [Commentary](decisions.md#commentary)、[Documentation](best-practices.md#documentation) |
| 导入、包职责与包大小 | [Imports](decisions.md#imports)、[Util packages](best-practices.md#util-packages)、[Package size](best-practices.md#package-size) |

## 错误与终止

| 问题 | 官方章节 |
| --- | --- |
| 错误返回、字符串与控制流 | [Errors](decisions.md#errors) |
| 错误上下文与是否使用 `%w` | [Adding information to errors](best-practices.md#error-extra-info) |
| `%w` 位置与 sentinel 例外 | [Placement of %w](best-practices.md#error-percent-w) |
| 返回错误与日志责任 | [Logging errors](best-practices.md#error-logging) |
| panic、Must 函数与程序退出 | [Don't panic](decisions.md#dont-panic)、[Must functions](decisions.md#must-functions)、[Program initialization](best-practices.md#program-init) |

## API、并发与数据

| 问题 | 官方章节 |
| --- | --- |
| 接口需求、归属与返回类型 | [Interfaces](decisions.md#interfaces)、[Interface ownership and visibility](best-practices.md#interface-ownership-and-visibility) |
| 是否需要泛型 | [Generics](decisions.md#generics) |
| 参数过多与可选配置 | [Function argument lists](best-practices.md#funcargs) |
| goroutine 的停止与等待 | [Goroutine lifetimes](decisions.md#goroutine-lifetimes)、[Synchronous functions](decisions.md#synchronous-functions) |
| context 与清理契约 | [Contexts](decisions.md#contexts)、[Cleanup](best-practices.md#documentation-conventions-cleanup) |
| 复制、指针与接收器 | [Copying](decisions.md#copying)、[Pass values](decisions.md#pass-values)、[Receiver type](decisions.md#receiver-type) |
| nil 与空切片 | [Nil slices](decisions.md#nil-slices) |
| 变量声明与容量提示 | [Variable declarations](best-practices.md#vardecls) |
| 字符串构造 | [String concatenation](best-practices.md#string-concat) |
| 全局状态与依赖传递 | [Global state](best-practices.md#globals) |

## 测试代码

按项目选定的测试方式查阅。

- [Useful test failures](decisions.md#useful-test-failures)
- [Test structure](decisions.md#test-structure)
- [Tests](best-practices.md#tests)

## 原始 Markdown

需要在较长章节内搜索时，读取对应文件。优先检索具体标题或锚点，再读取相关段落。

- [index.md](index.md)
- [guide.md](guide.md)
- [decisions.md](decisions.md)
- [best-practices.md](best-practices.md)
