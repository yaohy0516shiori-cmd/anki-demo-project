# Question in software

## 1. High-Level Architecture (Simplified)

Anki is built as a **layered system** with multiple languages:

```
Frontend UI (TypeScript / Svelte)
        │
        │  Web UI rendered in Qt WebView
        ▼
Desktop UI Layer (Python - aqt)
        │
        ▼
Application Layer (Python - pylib)
        │
        │  Bridge (FFI + protobuf)
        ▼
Core Engine (Rust - rslib)
        │
        ▼
Database (SQLite)
```

Each layer has a specific responsibility.

------

## 2. Responsibilities of Each Layer

### 2.1 Frontend UI — `ts/`

Technology:

```
TypeScript
Svelte
Vite
```

Responsibilities:

- Rendering the **user interface**
- Card review screen
- Card editor
- Deck browser
- UI interactions

Important detail:

Anki is **not a typical web app**.
 The frontend runs inside a **Qt WebView**, which is an embedded browser inside the desktop application.

So the UI is **HTML/CSS/JS**, but the application itself is still a **desktop program**.

------

### 2.2 Desktop UI Layer — `qt/aqt`

Technology:

```
Python
Qt (GUI framework)
```

Responsibilities:

- Windows and dialogs
- Menu system
- Connecting UI events to backend logic
- Managing the embedded WebView

This layer acts as the **presentation layer** of the desktop application.

------

### 2.3 Application Layer — `pylib/`

Technology:

```
Python
```

Responsibilities:

- Coordinating application logic
- Calling the core engine
- Handling plugins/add-ons
- Managing workflows
- Data loading and saving
- Import/export
- Communicating with the UI

Example responsibilities:

```
UI requests review card
        ↓
Application layer loads card
        ↓
Calls scheduler in core engine
        ↓
Updates database
        ↓
Returns result to UI
```

This layer contains **application orchestration**, not the core algorithms.

------

### 2.4 Core Engine — `rslib/`

Technology:

```
Rust
```

The core engine contains the **core domain logic** of the system.

Its responsibilities include:

### 1. Domain Logic

Business rules of the system.

Example:

```
How spaced repetition works
How card states change
How review intervals are calculated
```

------

### 2. Data Model

Internal data structures representing the domain.

Examples:

```
Card
Deck
Note
Review
Collection
```

Example structure:

```
Card
  id
  interval
  due
  ease_factor
  queue
```

These structures represent the **state of the system**.

------

### 3. Algorithms

Concrete implementations of domain logic.

Example:

```
SM-2 spaced repetition algorithm
```

Algorithm determines:

```
next interval
next review date
ease factor
learning steps
```

------

### 4. State Transitions

How objects move between states.

Example card states:

```
new
learning
review
relearning
```

A review action changes the state.

Example:

```
learning → review
review → relearning
```

This is essentially a **state machine**.

------

### 5. Invariants

Rules that must **always remain true**.

Examples:

```
interval ≥ 0
card must belong to a deck
due date cannot be invalid
```

These rules protect the integrity of the system.

## 3. Language Communication Layer

Between Python and Rust there are two important technologies.

------

### 3.1 FFI (Foreign Function Interface)

FFI allows **one programming language to call functions written in another language**.

Example:

```
Python → Rust function
```

This works because:

1. Rust code is compiled into a **shared library**

```
librslib.so
rslib.dll
```

1. Python loads the library and calls its exported functions.

The reason this works is that **all languages ultimately compile to machine code**, which the CPU can execute.

However, languages differ in how they generate and manage machine code.

------

### 3.2 Protocol Buffers (`proto/`)

Protocol Buffers (protobuf) is a **data serialization format** created by Google.

It is used to define **structured messages shared between languages**.

Example schema:

```
message Card {
  int64 id = 1;
  int32 interval = 2;
  int32 due = 3;
}
```

From this schema, code can be generated for:

```
Rust
Python
Java
Go
TypeScript
```

Purpose:

- Define **data structures shared between languages**
- Provide **fast binary serialization**
- Ensure **type safety**

Important distinction:

```
HTTP = network communication protocol
protobuf = data format / serialization protocol
```

------

## 4. Data Structures vs Data Formats

These are different concepts.

### Data Structures

Used **inside programs**.

Examples:

```
Card object
Deck object
Review state
```

These live in **memory (RAM)**.

------

### Data Formats

Used for **storage or transmission**.

Examples:

```
JSON
CSV
Excel
SQLite
protobuf
```

When data is loaded:

```
JSON → Card object
protobuf → Card object
```

------

## 5. Why Systems Use Multiple Languages

Large systems often combine languages because each language has strengths.

Example:

Rust is good for:

```
performance
memory safety
system-level logic
```

Python is good for:

```
rapid development
application logic
plugins
integration
```

TypeScript is good for:

```
interactive UI
web technologies
```

So the architecture becomes:

```
UI → Python → Rust
```

------

## 6. Embedded Web vs Web Applications

### Web Application

Runs inside a browser.

Example:

```
Gmail
Notion
Google Docs
```

Architecture:

```
Browser → Server
```

------

### Embedded Web UI

Runs inside a **desktop application**.

Example:

```
VS Code
Figma Desktop
Anki
```

Architecture:

```
Desktop app
   ↓
Embedded browser (WebView)
   ↓
HTML/JS UI
```

------

## 7. Frameworks

A **framework** is a pre-built structure for building applications.

Examples:

```
FastAPI
Django
Spring
React
Qt
```

Difference from libraries:

```
Library:
    your code calls the library

Framework:
    the framework calls your code
```

Example:

```
@app.get("/cards")
def get_cards():
```

FastAPI calls your function when a request arrives.

------

## 8. Performance Differences Between Languages

Even though CPUs only execute machine code, languages differ because of:

### Compilation Strategy

Compiled languages:

```
C
C++
Rust
Go
```

Compile directly to machine code.

------

Interpreted languages:

```
Python
JavaScript
```

Use a runtime interpreter or virtual machine.

Execution path:

```
source → bytecode → interpreter → machine code
```

------

### Memory Management

Rust / C:

```
manual memory control
```

Python / Java:

```
garbage collection
```

Garbage collection introduces runtime overhead.

# Rust basic reading(not for teaching, simple understanding)

## 1. 变量：`let`

Rust 里最常见的是：

```
let x = 5;
```

相当于 Python：

```
x = 5
```

但 Rust 默认**不可变**。

```
let x = 5;
// x = 6;  // 报错
```

如果要可变：

```
let mut x = 5;
x = 6;
```

相当于 Python 里没有这个限制，但 Rust 会强制你写清楚是不是允许改。

------

## 2. 类型标注

Rust 经常写类型：

```
let x: i32 = 5;
let name: String = "abc".to_string();
```

Python 对照：

```
x: int = 5
name: str = "abc"
```

只是 Rust 的类型是真正强约束，不只是提示。

常见类型：

- `i32`：32位整数
- `i64`：64位整数
- `u32`：无符号整数
- `f64`：浮点数
- `bool`
- `String`：可变字符串对象
- `&str`：字符串切片，类似“借用的字符串视图”

------

## 3. 函数：`fn`

```
fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

Python：

```
def add(a: int, b: int) -> int:
    return a + b
```

注意两点：

第一，参数类型必须写

Rust 必须写类型，Python 通常不用。

第二，最后一行**不加分号**时，会作为返回值

```
fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

等价于：

```
fn add(a: i32, b: i32) -> i32 {
    return a + b;
}
```

如果写成：

```
fn add(a: i32, b: i32) -> i32 {
    a + b;
}
```

就不对了，因为加了分号，变成“执行语句，不返回这个值”。

这个点你读 Rust 时一定要习惯。

------

## 4. `if` 和 Python 很像，但条件必须是布尔值

```
if x > 0 {
    println!("positive");
} else {
    println!("not positive");
}
```

Python：

```
if x > 0:
    print("positive")
else:
    print("not positive")
```

Rust 没有 Python 那种“空字符串算 False、0 算 False”的宽松规则。
 条件必须真的是 `bool`。

------

## 5. `if` 也是表达式

```
let x = if flag { 1 } else { 2 };
```

Python 可以勉强类比成：

```
x = 1 if flag else 2
```

Rust 里很多东西都“既能控制流程，也能产出值”。

------

## 6. 循环

## `for`

```
for i in 0..5 {
    println!("{}", i);
}
```

表示 `0,1,2,3,4`

Python：

```
for i in range(5):
    print(i)
```

如果是 `0..=5`，表示包含 5。

------

## `while`

```
while x < 10 {
    x += 1;
}
```

Python：

```
while x < 10:
    x += 1
```

------

## `loop`

Rust 还有无限循环：

```
loop {
    break;
}
```

类似：

```
while True:
    break
```

------

## 7. 注释

```
// 单行注释

/*
多行注释
*/
```

和 C/C++/Java 一样。

------

## 8. 结构体 `struct`

这是你读业务代码时最常见的东西之一。

```
struct Card {
    id: i64,
    front: String,
    back: String,
}
```

Python 类比：

```
class Card:
    def __init__(self, id: int, front: str, back: str):
        self.id = id
        self.front = front
        self.back = back
```

或者更像 dataclass：

```
from dataclasses import dataclass

@dataclass
class Card:
    id: int
    front: str
    back: str
```

Rust 的 `struct` 很常用来表示数据对象。

创建实例：

```
let card = Card {
    id: 1,
    front: "hello".to_string(),
    back: "world".to_string(),
};
```

------

## 9. `impl`：给结构体加方法

```
struct Card {
    id: i64,
    front: String,
}

impl Card {
    fn new(id: i64, front: String) -> Self {
        Self { id, front }
    }

    fn show(&self) {
        println!("{}", self.front);
    }
}
```

Python：

```
class Card:
    def __init__(self, id: int, front: str):
        self.id = id
        self.front = front

    def show(self):
        print(self.front)
```

你可以把：

- `struct` 理解成“数据定义”
- `impl` 理解成“给这个类写方法”

------

## 10. `Self` 和 `self`

这个很常见。

## `Self`

表示“当前这个类型本身”。

```
fn new(id: i64, front: String) -> Self
```

意思就是返回 `Card`。

## `self`

表示实例本身，类似 Python 里的 `self`。

```
fn show(&self)
```

就像：

```
def show(self):
```

------

## 11. `enum`：枚举，非常重要

Rust 的 `enum` 比很多语言强很多。

```
enum Rating {
    Again,
    Good,
    Easy,
}
```

Python 可以粗略类比：

```
from enum import Enum

class Rating(Enum):
    AGAIN = 1
    GOOD = 2
    EASY = 3
```

Anki 这类项目里，状态、类型、结果，常常会用 `enum` 表示。

------

## 12. `match`：模式匹配

```
match rating {
    Rating::Again => 1,
    Rating::Good => 3,
    Rating::Easy => 7,
}
```

Python 对照可以理解成：

```
if rating == Rating.AGAIN:
    days = 1
elif rating == Rating.GOOD:
    days = 3
else:
    days = 7
```

但 Rust 的 `match` 更强、更严格。
 你看到它时，可以先把它当成“更安全的 if-elif”。

------

## 13. `Option<T>`：可能有值，也可能没有

这个超级常见。

```
let x: Option<i32> = Some(5);
let y: Option<i32> = None;
```

Python 类比：

```
x: int | None = 5
y: int | None = None
```

Rust 不喜欢随便给你 `null`，所以专门用 `Option` 表示“可能为空”。

常见处理方式：

```
match x {
    Some(v) => println!("{}", v),
    None => println!("no value"),
}
```

意思就是：

- `Some(v)`：有值
- `None`：没值

------

## 14. `Result<T, E>`：可能成功，也可能失败

也非常常见。

```
fn parse_num(s: &str) -> Result<i32, String> {
    // ...
}
```

Python 类比可以理解为两种可能：

- 成功：返回值
- 失败：抛异常

但 Rust 不喜欢到处直接抛异常，它更喜欢显式写：

- `Ok(value)`
- `Err(error)`

例如：

```
match result {
    Ok(v) => println!("success: {}", v),
    Err(e) => println!("error: {}", e),
}
```

你读源码时看到 `Result<..., ...>`，就知道：
 **这个函数可能失败。**

------

## 15. `?`：错误快速向上传递

这在 Rust 里非常高频。

```
let card = load_card(id)?;
```

意思近似于：

- 如果成功，拿到值继续
- 如果失败，当前函数直接返回错误

Python 粗略类比：

```
card = load_card(id)  # 如果报错就往外抛
```

Rust 只是把这种逻辑写得很紧凑。

------

## 16. 引用 `&`：不是复制，而是借用

这是 Rust 最难但也最核心的部分之一。

```
fn show(s: &String) {
    println!("{}", s);
}
```

这里 `&String` 表示：
 **我不拿走这个字符串的所有权，我只是借来看一下。**

Python 里变量本来就是引用语义，所以你通常不会特别注意这个。
 但 Rust 非常在意“谁拥有这个值、谁能修改、什么时候释放”。

你现在读源码时，先这样记就够了：

- `String`：我拥有它
- `&String`：我借来看
- `&mut String`：我借来，并且要改它

------

## 17. 所有权：先用直觉理解，不要一开始钻太深

```
let s1 = String::from("hello");
let s2 = s1;
// println!("{}", s1); // 报错
```

为什么？
 因为 `String` 这种类型在 Rust 里默认是“移动”而不是“复制”。

Python 不会这样：

```
s1 = "hello"
s2 = s1
print(s1)  # 没问题
```

Rust 这样设计是为了内存安全和性能。

你现在读代码时，只要先知道：

- 有些值赋给别人后，原变量不能再用
- 除非这个类型支持复制，或者你显式 `.clone()`

------

## 18. `clone()`：复制一份

```
let s1 = String::from("hello");
let s2 = s1.clone();
println!("{}", s1);
```

Python 里很多时候你不在意这件事；
 Rust 里你要更明确地区分“借用 / 移动 / 深复制”。

------

## 19. `Vec<T>`：动态数组

```
let nums = vec![1, 2, 3];
```

Python：

```
nums = [1, 2, 3]
```

访问：

```
let first = nums[0];
```

追加：

```
let mut nums = vec![1, 2];
nums.push(3);
```

Python：

```
nums = [1, 2]
nums.append(3)
```

------

## 20. `HashMap<K, V>`

```
use std::collections::HashMap;

let mut map = HashMap::new();
map.insert("a", 1);
```

Python：

```
map = {}
map["a"] = 1
```

------

## 21. `String` vs `&str`

这个你看源码时会经常遇到。

## `String`

拥有数据，可增长，可修改。

## `&str`

字符串切片，借用的只读视图。

先粗略理解成：

- `String` 更像真正持有内容的字符串对象
- `&str` 更像“指向字符串的一段引用”

Python 没有这么明显的区分，所以你一开始只要知道：
 **看到 `&str`，通常表示函数只是读这个字符串，不打算拥有它。**

------

## 22. 可见性：`pub`

```
pub struct Card {
    pub id: i64,
}
```

Python 没有真正严格的 public/private。
 Rust 里 `pub` 表示“对外可见”。

没有 `pub`，通常就是模块内部使用。

------

## 23. 模块：`mod` / `use`

Rust 项目会拆很多模块。

```
mod scheduler;
use crate::card::Card;
```

你可以大概理解成 Python 的：

```
import scheduler
from card import Card
```

只是 Rust 的模块系统更严格一些。

------

## 24. trait：有点像“接口”

这个你读 Anki 源码时可能会见到。

```
trait Drawable {
    fn draw(&self);
}
```

像 Python 的抽象协议 / 接口思想，也像 Java 的 interface。

实现：

```
impl Drawable for Card {
    fn draw(&self) {
        println!("draw");
    }
}
```

你现阶段不用深挖，只要知道：
 **trait = 一组行为规范。**

------

## 25. 常见派生：`#[derive(...)]`

```
#[derive(Debug, Clone)]
struct Card {
    id: i64,
}
```

这表示自动给结构体生成一些常用能力。

常见的：

- `Debug`：可以打印调试
- `Clone`：可以 `.clone()`
- `PartialEq`：可以比较相等
- `Default`：支持默认值

这有点像“自动生成一些标准方法”。

------

## 26. 一个你读业务代码时最常见的综合例子

```
enum Rating {
    Again,
    Good,
    Easy,
}

struct Card {
    id: i64,
    interval: i32,
}

impl Card {
    fn update_interval(&mut self, rating: Rating) {
        self.interval = match rating {
            Rating::Again => 1,
            Rating::Good => self.interval * 2,
            Rating::Easy => self.interval * 3,
        };
    }
}
```

Python 对照：

```
from enum import Enum
from dataclasses import dataclass

class Rating(Enum):
    AGAIN = 1
    GOOD = 2
    EASY = 3

@dataclass
class Card:
    id: int
    interval: int

    def update_interval(self, rating: Rating):
        if rating == Rating.AGAIN:
            self.interval = 1
        elif rating == Rating.GOOD:
            self.interval = self.interval * 2
        else:
            self.interval = self.interval * 3
```

# python 类问题（note类提问总结）

### 1. Python 类基础

**问题**：Python 中如何定义一个类？
**答案**：使用 `class` 关键字，类名通常采用驼峰命名。`__init__` 是构造方法，用于初始化实例属性。方法的第一个参数必须是 `self`，代表实例本身。

**问题**：类属性和实例属性有什么区别？
**答案**：类属性定义在类内部、方法外部，属于类本身，所有实例共享；实例属性在 `__init__` 等方法中通过 `self.属性` 定义，每个实例独立拥有。修改类属性会影响所有实例，而修改实例属性只影响当前实例。

------

### 2. 特殊方法（魔法方法）

**问题**：`__str__`、`__repr__`、`__len__` 等特殊方法有什么用？如何调用？
**答案**：这些方法定义了对象与内置函数或操作符交互时的行为。`__str__` 在 `print(obj)` 或 `str(obj)` 时调用；`__repr__` 在交互环境直接输入对象或 `repr(obj)` 时调用；`__len__` 在 `len(obj)` 时调用。它们由 Python 自动触发，不应手动调用。

------

### 3. 继承与多态

**问题**：如何实现父类和子类？
**答案**：子类在定义时在括号内指定父类名。子类自动继承父类的属性和方法，可重写（override）父类方法。使用 `super()` 可以调用父类的方法（如在重写的方法中保留父类功能）。

**问题**：多继承时方法查找顺序是怎样的？
**答案**：Python 按照方法解析顺序（MRO）从左到右查找方法，可通过 `类名.__mro__` 查看。`super()` 也遵循 MRO 顺序。

------

### 4. 记录创建时间和更新时间

**问题**：如何在类中自动记录对象的创建和最后修改时间？
**答案**：可以在 `__init__` 中设置 `created_at` 和 `updated_at`。要实现自动更新，可以采用：① 手动在修改方法中更新时间；② 使用 `@property` 的 setter 在属性赋值时触发；③ 重写 `__setattr__` 全局捕获属性修改；④ 使用描述符。数据库 ORM（如 SQLAlchemy、Django）通常有内置的 `auto_now_add` 和 `auto_now` 选项。

------

### 5. Checksum 的概念与用途

**问题**：什么是 checksum？有什么用？
**答案**：Checksum 是根据数据计算出的简短数值，用于验证数据完整性，检测传输或存储中的错误。常见用途包括网络通信（如 TCP）、文件下载校验（MD5/SHA）、存储系统错误检测等。

**问题**：在类中如何用 checksum 判断内容是否更新？
**答案**：可基于关键属性计算哈希（如 `hashlib.sha256`）或使用版本号（整数递增）。哈希方法准确但可能耗时，版本号方法高效但需确保所有修改操作都更新版本号。可结合两者：用版本号判断是否需要重新计算哈希，实现惰性更新。

------

### 6. `hash()` 与 `hashlib` 的区别

**问题**：`hash()` 和 `hashlib` 生成的哈希值有什么不同？为什么说 `hashlib` 更稳定？
**答案**：`hash()` 是内置函数，用于字典等数据结构，其值受随机化种子影响，不同 Python 进程可能不同，不能持久化。`hashlib` 提供标准密码学哈希函数（如 SHA-256），结果确定且跨平台一致，适合持久化存储和跨系统校验。

------

### 7. `@property` 装饰器

**问题**：`@property` 有什么用？如何使用？
**答案**：`@property` 将方法伪装成属性，调用时无需加括号。可用于实现只读属性、数据验证、计算属性、延迟加载等。可通过 `@属性名.setter` 定义赋值行为，`@属性名.deleter` 定义删除行为。

------

### 8. 针对用户提供的 `Note` 类代码的优化建议

**问题**：用户代码中的 `__calculate_checksum` 方法调用错误在哪里？如何修复？
**答案**：`__init__` 中调用 `self.__calculate_checksum()` 时未传参，而方法定义需要 `fields` 参数。应改为 `self.__calculate_checksum(self.fields)`。

**问题**：`update` 方法中比较与赋值分开是否合理？
**答案**：合理。先比较新旧 checksum 可以避免内容未变时进行不必要的更新（如更新时间戳）。这是“仅在变化时更新”的典型设计。

**问题**：`sort_field` 为何用第一个字段？如何保持同步？
**答案**：在许多笔记应用中，第一个字段常作为主字段用于排序。但若 `fields` 可能变化，应在访问时动态获取，例如使用 `@property` 返回 `self.fields[0]`，而不是在 `__init__` 中固定赋值。

**问题**：时间戳的微秒是否需要？
**答案**：视需求而定。`isoformat()` 包含微秒，若觉得冗余，可用 `strftime` 自定义格式（如 `"%Y-%m-%d %H:%M:%S"`），仍可排序。

**问题**：`id` 应如何生成？
**答案**：若由外部存储（如数据库）生成，可允许传入 `None` 并在保存时赋值；若需自动生成唯一 ID，可使用 `uuid.uuid4().hex`。

**问题**：`strip()` 在计算 checksum 时的使用是否正确？
**答案**：`field.strip()` 去除字段首尾空白，返回字符串，因此 `new_fields += field.strip()` 正确。但需注意是否真的需要去除空白，若字段内容本身需保留空格（如填空题），则不应 strip。

**问题**：为何在 `update` 方法中需要重新计算 checksum？
**答案**：因为传入的新字段可能与当前内容不同，需要基于新字段计算新 checksum，并与旧 checksum 比较。如果相同，则跳过更新；如果不同，则更新字段、checksum 和修改时间。

------

### 9. 实例化时自动初始化 checksum

**问题**：建立实例时，`self.__checksum = self.__calculate_checksum(self.fields)` 会自动执行吗？
**答案**：是的。当创建实例时，`__init__` 方法自动被调用，其中的所有初始化代码（包括对 `__checksum` 的赋值）都会执行一次。因此每个新实例都会拥有基于其初始字段计算出的校验和。