# DEVELOP LOG

# 2026-03-05

**-- complete set up git**

**-- using git to push my code to GitHub**

**-- start understanding the framework of ANKI, plan to use python to rebuild it**

### **-- my stack**

| Layer       | Tech                       |
| :---------- | :------------------------- |
| Web UI      | TypeScript + React/Next.js |
| API         | Python FastAPI             |
| DB          | PostgreSQL                 |
| Cache/Queue | Redis                      |
| Worker      | Celery/RQ                  |
| Engine      | Python + Rust/Go           |

### -- basic plan

Phase 1: Core engine (Python only)

Goal: Implement the spaced repetition logic.

- Cards, decks, scheduling algorithm (SM-2 or similar)
- No web UI, no database yet
- Test with Python scripts or a simple CLI

Why first: This is the heart of Anki. Everything else builds on it.

Phase 2: API + simple persistence

Goal: Expose the engine via HTTP and save data.

- FastAPI endpoints (create deck, add card, review card)
- SQLite instead of PostgreSQL (no separate DB server, easier to start)

Why: You learn API design and basic persistence without extra setup.

Phase 3: Basic web UI

Goal: A minimal UI to use the app.

- React/Next.js + TypeScript
- Simple pages: list decks, add cards, review cards

Why: You get a full local app and learn frontend–backend integration.

Phase 4: Move to PostgreSQL

Goal: Use a real database.

- Replace SQLite with PostgreSQL
- Add migrations (e.g. Alembic)

Phase 5: Redis, Celery, Rust (when needed)

Goal: Add these only when you have a concrete need.

- Redis: caching, sessions, rate limiting
- Celery/RQ: background jobs (sync, exports, etc.)
- Rust: performance-critical parts of the engine

What to start with right now

| Do now                                 | Skip for now                  |
| :------------------------------------- | :---------------------------- |
| Python core engine (spaced repetition) | PostgreSQL → use SQLite first |
| FastAPI (simple endpoints)             | Redis, Celery                 |
| Basic React/Next UI                    | Rust                          |
| Local only                             | Deployment                    |

### -- understanding the basic structure of ANKI

Overall System Architecture

Anki follows a **layered architecture with multiple languages**, where each layer focuses on a different concern.

```bash
┌───────────────────────────────────────────┐
│               Frontend UI                 │
│          (TypeScript / Svelte)            │
└───────────────────────────────────────────┘
                     │
                     │ HTML / JS rendered in WebView
                     ▼
┌───────────────────────────────────────────┐
│             Desktop UI Layer              │
│              (Python + Qt)                │
│                 aqt/                      │
└───────────────────────────────────────────┘
                     │
                     │ Python API calls
                     ▼
┌───────────────────────────────────────────┐
│           Application Layer               │
│              (Python pylib)               │
│        Workflow / orchestration           │
└───────────────────────────────────────────┘
                     │
                     │ FFI + protobuf bridge
                     ▼
┌───────────────────────────────────────────┐
│             Core Engine                   │
│               (Rust rslib)                │
│      Domain logic + scheduling engine     │
└───────────────────────────────────────────┘
                     │
                     │ SQL
                     ▼
┌───────────────────────────────────────────┐
│                Database                   │
│                SQLite                    │
└───────────────────────────────────────────┘
```

Data Flow Through the System

```bash
User reviews card in UI
        ↓
Frontend sends event
        ↓
Qt UI triggers Python handler
        ↓
Application layer loads card
        ↓
Scheduler in core engine computes result
        ↓
Database updated
        ↓
Result returned to UI
        ↓
Next card displayed
```

Each layer focuses on a specific responsibility.

```bash
UI → presentation
application → workflow
core engine → domain logic
database → persistence
```

# **2026-03-06**

### -- core engine function in ANKI

| 模块             | 主要功能                                                              |
| ---------------- | --------------------------------------------------------------------- |
| `collection/`    | 管理整个学习库（collection），协调各模块，处理整体读写、事务、undo 等 |
| `card/`          | 管理 card 数据本身，如卡片属性、状态、生成后的卡片对象                |
| `notes/`         | 管理 note（原始内容），例如正面、背面、字段内容                       |
| `decks/`         | 管理 deck（牌组/卡组），包括创建、删除、层级关系                      |
| `notetype/`      | 管理模板（note type），决定一个 note 如何生成一张或多张 card          |
| `tags/`          | 管理标签，给 note/card 分类和检索                                     |
| `deckconfig/`    | 管理牌组配置，如学习步长、毕业间隔、复习参数                          |
| `scheduler/`     | 学习调度核心：决定先学什么、下一次什么时候复习、评分后如何更新状态    |
| `search/`        | 搜索与过滤，支持按 deck、tag、状态、关键词等查找内容                  |
| `storage/`       | 底层数据库读写，负责和 SQLite 交互，执行增删改查                      |
| `revlog/`        | 记录每次复习日志，如时间、按钮选择、间隔变化                          |
| `stats/`         | 基于复习记录做统计，如今日学习量、保留率、未来 due 数量               |
| `import_export/` | 导入导出学习内容，如牌组包、文本导入等                                |
| `media/`         | 管理媒体文件，如图片、音频、文件引用                                  |
| `sync/`          | 同步相关逻辑，包括账号登录、云端同步、媒体同步                        |
| `config/`        | 全局配置项管理                                                        |
| `backend/`       | 对外暴露给上层调用的后端接口封装                                      |
| `dbcheck/`       | 检查数据库一致性、修复部分异常                                        |
| `undo/`          | 撤销操作支持                                                          |
| `browser_table/` | 支持浏览器（browser）里表格展示、排序、列数据准备                     |

### -- minimum function of my project's core engine

Phase 1 — Mini Core Engine

- Deck / Card 数据模型
- Card CRUD
- Review session
- Next card selection
- Simple spaced repetition
- Review log
- SQLite persistence

用户可以创建卡片、开始复习、评分、自动更新下次复习时间

Phase 2 — Feature Expansion

- User account / login
- Search and filtering
- Study statistics dashboard
- Better scheduling logic
- Import / export
- Tags / organization
- More polished API and frontend interaction

系统支持更完整的学习管理和基础产品体验

Phase 3 — Full Version

- Note / Card separation
- Notetype and templates
- Media support
- Multi-device sync
- Advanced scheduling
- Plugin/extensible architecture

系统具备更强的自定义能力和完整记忆软件框架

### -- design question

开发顺序应该是先把 core engine 全阶段做完，还是先做 mini 版再逐步更新?

应先做 mini 版完整闭环，再逐步迭代。每个 phase 都应该产出一个小而完整、可运行的系统，而不是先把 core engine 单独做到很完整。

开始确定 mini 版的垂直切片范围，也就是第一版到底包含哪些 engine、DB、service 和 UI 功能。

### -- phase 1 core engine reading

```
rslib/src/card/
rslib/src/decks/
rslib/src/scheduler/
rslib/src/storage/
rslib/src/collection/
```

| 模块                  | 核心职责                       | 对应功能                                                                                            |
| --------------------- | ------------------------------ | --------------------------------------------------------------------------------------------------- |
| `note`                | 保存原始学习内容               | 创建 note、编辑 note、删除 note、保存 front/back 等源内容                                           |
| `card`                | 把 note 变成可复习单元         | 关联 `note_id`、定义 card 类型、保存正反面展示关系、维护 card 基本信息                              |
| `scheduler`           | 决定什么时候复习、下一张复习谁 | 取下一张 card、判断是否到期、排序/抽取、根据评分更新 `due_date / interval / status / reps / lapses` |
| `reviewlog`           | 记录每次复习发生了什么         | 保存评分结果、旧状态/新状态、旧 interval/新 interval、复习时间                                      |
| `review_service`      | 串联一次完整复习流程           | 开始复习、提交评分、调用 scheduler 更新 card、写入 reviewlog、保存结果                              |
| `template` / 展示逻辑 | 决定这张卡怎么复习             | 正面显示什么、背面显示什么、basic 或 reversed 形式                                                  |

**问题：**
既然 ranking 结果最终会更新到 `card`，为什么还需要单独的 `reviewlog`。

**结论：**
`card` 负责保存最新状态，`reviewlog` 负责保存每次复习事件的历史。只存 `card` 会丢失评分过程、旧状态和学习轨迹，导致统计、调试和后续分析都很困难，因此 `reviewlog` 仍然有必要保留。

**下一步：**
给 `ReviewLog` 先定一个最小字段集合，例如 `card_id / reviewed_at / rating / old_status / new_status / old_interval / new_interval`，先保证历史事件可以被记录下来。

# **2026-03-07**

### Note Module Design

The `note` module is responsible for storing the original learning content and metadata that can be used to generate one or more review cards.

#### Responsibilities

- manage note content
- define note type
- connect notes to a deck/group
- manage tags
- provide source data for card generation
- support CRUD operations
- persist note data in SQLite

#### Supported note types

- Basic Question and Answer
- Fill in the Blank / Cloze
- Reverse Card (auto-generated)
- Reverse Card (manually created)

#### Main attributes

- `note_id`
- `note_type`
- `group_id` / `deck_id`
- `front_content`
- `back_content`
- `tags`
- `created_at`
- `updated_at`

#### CRUD operations

- `create_note()`
- `get_note_by_id()`
- `list_notes()`
- `update_note()`
- `delete_note()`

#### Storage

The note records should be stored in SQLite.
A note table can be used to store the main content, while tags and groups can either be stored directly or normalized into separate tables depending on project complexity.

# **2026-03-11**

### Note Type

- `id`：该 note type 的唯一标识，用于让 `Note.note_type_id` 引用它
- `name`：给用户和开发者看的类型名称，不是 card front 内容
- `field_names`：定义该类型有哪些字段、字段顺序和字段名称
- `kind`：定义该类型的行为规则，例如 `basic`、`cloze`、`basic_reverse`；生成card用

### Note

- `id`：这条 note 实例自己的唯一标识
- `note_type_id`：指向所属 `NoteType` 的 id，用于解释 `fields`
- `fields`：这条 note 的具体内容
- `tags`：用户自定义标签
- `sort_field`：用于排序/列表显示的主字段，通常由 `fields` 派生
- `checksum`：由内容计算出的校验值，用于比较/查重/检测变化
- `created_at`：创建时间
- `updated_at`：最后更新时间

# **2026-3-12**

--finish class Note and class Note Type

## note 模块职责到底是什么

### **Q：core engine 设计阶段，是不是先不要管 CRUD、SQLite 这些实现？**

**A：对。先分清模块职责，再谈实现。**
昨天一开始把 `note` 想得太大，混进了：

- CRUD
- SQLite
- front/back
- reverse/cloze
- 调度
- review log

后来理清：

- `note`：原始学习内容
- `card`：真正复习的卡
- `scheduler`：决定什么时候复习
- `review_log`：记录复习结果

---

### **Q：`answer question / cloze / reverse` 属于 `note` 吗？**

**A：不直接属于。更接近 `notetype / template`。**
之前把这些当成 `note function`，后来发现更准确的说法是：

- `basic`
- `cloze`
- `reverse`
  这些是 **题型/模板规则**，不是 `note` 本体功能。

---

### **Q：`note` 模块最核心的职责是什么？**

**A：保存原始内容，并为后续生成 card 提供结构化数据。**
也就是说：

- `note` 不是复习展示层
- `note` 不是调度层
- `note` 更像知识源文件

---

## 为什么还需要 Notetype

### **Q：既然 note 已经存了内容，为什么还要 `Notetype`？**

**A：因为 `Note` 只存值，`Notetype` 定义这些值的结构和含义。**

例如：

```python
fields = ["CPU", "Central Processing Unit"]
```

没有 `Notetype`，系统不知道：

- 第一个字段叫 Front 还是 Text
- 第二个字段叫 Back 还是 Extra
- 这是不是 basic / cloze / reverse

所以可以这样理解：

- `Notetype` = 结构定义 / 模板
- `Note` = 一条具体数据

---

### **Q：那 `note_type_id` 的作用到底是什么？**

**A：它是 `Note` 指向 `Notetype` 的引用。**
`Note` 自己不会存整个 `Notetype`，只存一个 `note_type_id`。
之后运行时需要通过这个 id 再找回对应的 `Notetype`。

---

### **Q：我困惑的点是不是中间少了一个 lookup 过程？**

**A：对。关键缺的就是 `note_type_id -> Notetype` 的查找过程。**
第一版不一定非要 SQLite，可以先用：

- dict
- in-memory repository

比如：

```python
note_type = note_type_repo.get(note.note_type_id)
```

---

## NoteType、Note、Card 的关系

### **Q：`Notetype`、`Note`、`Card` 三者关系是什么？**

**A：`Notetype` 定义规则，`Note` 存内容，`Card` 是生成结果。**

流程可以理解成：

- `Notetype` 定义字段和行为
- `Note` 按这个结构保存值
- `Card` 根据 `Note + Notetype` 生成

也就是：

```
Notetype -> Note -> Card
```

---

### **Q：`Note` 和 `Notetype` 是继承关系吗？**

**A：不是。**
这是今天代码里一个很重要的纠正。

错误想法：

- `class Note(Notetype)`

正确关系：

- `Notetype` 是模板/结构
- `Note` 是实例/数据
- 它们不是父子类

---

## 关于字段设计的理解

### **Q：`Notetype` 的几个字段分别干嘛？**

**A：**

- `id`：类型唯一标识
- `name`：给用户/开发者看的类型名字
- `field_names`：定义字段名称和顺序
- `kind`：定义行为规则，例如 `basic`、`cloze`

---

### **Q：`Note` 的几个字段分别干嘛？**

**A：**

- `id`：这条 note 自己的唯一标识
- `note_type_id`：说明它属于哪种 `Notetype`
- `fields`：具体内容
- `tags`：用户标签
- `sort_field`：用于排序/显示的主字段
- `checksum`：内容指纹
- `created_at / updated_at`：时间信息

---

## checksum 到底是什么

### **Q：`checksum` 是不是用来判断 SQL / 数据库损坏？**

**A：不是主要干这个的。**
这里更准确的理解是：

`checksum` = 内容指纹

主要用途：

- 判断内容有没有变化
- 辅助查重
- 快速比较

不是主要用来：

- 检测数据库损坏
- 做 web 专用校验

---

### **Q：为什么不直接对全部内容做 hash？**

**A：可以，但“只 hash 主字段”和“hash 全部内容”解决的是不同问题。**

- 只 hash 主字段：更适合判断“是不是同一个知识点”
- hash 全部内容：更适合判断“整条内容是否完全相同”

你现在第一版先做简单点就行。

---

## 代码实现里踩过的坑

### **Q：为什么 `@property` 写完还是报错？**

**A：因为 `@property` 不能写在 `__init__` 里面，只能写在类体里。**

---

**Q：为什么 property 会无限递归？**
**A：因为内部属性和 property 重名了。**
比如这种写法会坏掉：

```python
self.fields = fields

@property
def fields(self):
    return self.fields
```

这会无限调用自己。

正确做法：

- 内部用 `__fields`
- 外部 property 叫 `fields`

---

### **Q：为什么一直强调统一用 `__fields / __tags / __note_type_id`？**

**A：因为你后来很多 bug 都来自“内部属性”和“外部属性”混用了。**
比如一会儿写：

- `self.fields`
  一会儿写：
- `self.__fields`

这样对象内部状态会乱。

---

### **Q：为什么 `update()` 里还要同步更新 `sort_field / checksum / updated_at`？**

**A：因为这些是依赖 `fields` 的派生数据。**
如果字段变了，这些也必须重算。

---

### **Q：`set_id()` 为什么存在？id 不应该系统自动分配吗？**

**A：对，所以 `set_id()` 不是给用户随便改的，而是给系统/repository 设置一次。**
规则应该是：

- 创建 note 时可以 `id=None`
- 保存时系统分配 id
- 一旦设定，不能再改

---

## copy 和封装

### **Q：为什么 `self.__fields = list(fields)`，不直接 `self.__fields = fields`？**

**A：为了避免外部修改原列表时，内部也被偷偷改掉。**

如果直接引用同一个 list，外部一改，note 内部也会变。
这样会导致：

- checksum 不同步
- updated_at 不更新
- 封装失效

---

### **Q：为什么 property 返回 `list(self.__tags)`，也要再 copy 一次？**

**A：为了防止外部拿到列表后，直接改内部状态。**

如果直接返回内部列表，用户可以这样做：

```python
note.tags.append("xxx")
```

这样会绕过：

- `add_tag()`
- 去重检查
- 时间更新

所以返回副本是为了保护内部状态。

---

### **Q：浅拷贝够吗？**

**A：对你现在的 `List[str]` 设计来说够了。**
因为字符串不可变。
如果以后允许子对象，再考虑：

- `deepcopy`
- 不可变对象
- 单独建模

---

## 校验到底该放哪里

### **Q：为什么 `judge_legal` 不建议直接放在 `Note` 里？不是 import 一下 `Notetype` 就行吗？**

**A：不是不能写，而是职责上不够清楚。**

因为“字段是否合法”依赖的是：

- `Notetype` 的字段数
- `Notetype` 的 kind
- 甚至以后模板规则

所以更适合：

- `service`
- `validator`

但你现在第一版，为了简单，先放在 `Note` 里并传入 `note_type` 也可以。

---

### **Q：`__validate_string_list()` 这段是干嘛的？**

**A：它是在做最基础的输入类型检查。**

检查：

- 是不是 list
- 每个元素是不是 str

因为 Python 的类型标注不会自动帮你拦截错误输入。

---

### **Q：空字符串应该允许吗？**

**A：不要一刀切。**

- `fields`：通常可以允许空字符串，因为有些字段可以为空、或者 note 还没填完
- `tags`：一般不应该允许空字符串

所以“是否允许空”最好按对象类型分别处理。

---

## Conclusion

## **先把 `NoteType` 和 `Note` 两个类写稳，不要急着加太多新层。**

当前最合理的顺序是：

1. 先完成 `NoteType`
2. 先完成 `Note`
3. 测试创建 / 更新 / 加 tag / set_id
4. 再补 `NoteTypeRepository`
5. 再补 `NoteRepository`
6. 最后再考虑 `Service / Validator`

把下面几件事分开了：

- 结构定义
- 实例数据
- 存储
- 校验
- 卡片生成

一旦这几层分开，整个设计就顺很多。

---

**brief recap:** 这两天最核心的问题不是语法，而是职责混淆：先是把 `note` 模块想得太大，后来又混淆了 `Notetype`、`Note`、`Card`、`checksum`、`id`、copy、property 和校验边界。现在已经理清：`Notetype` 定义结构，`Note` 保存内容，`Card` 是生成结果；`checksum` 是内容指纹；`id` 只允许系统设置一次；`fields/tags` 要复制并通过 property 返回副本；依赖 `Notetype` 的合法性判断最终更适合放到 service/validator。

# **2026-3-16**

## 1. 模型边界

**Q：`Note` / `NoteType` 里要不要写 judge？现在这两个类主要补什么？**
A：不要写 judge，放在 `service layer`。这两个类现在补的是模型自身完整性：基础校验、`__touch()`、`to_dict()`、`from_dict()`、tag 基础操作、占位注释。

---

## 2. `tags` / `fields` 的“整体”和“单个元素”

**Q：`tags` 不是 list 吗，为什么 `add_tag()` 只收一个 tag？tag 要不要限制类型？**
A：`tags` 是整个列表，`tag` 是列表里的一个元素，所以 `add_tag()` 收单个值。内部最好统一存成 `list[str]`；外部输入可以先转成 `str` 再放进去。

---

## 3. `__touch__`、`to_dict()`、`from_dict()`

**Q：`__touch()` 是干嘛的？`to_dict()` / `from_dict()` 是什么意思？`from_dict()` return 的是什么？**
A：`__touch()` 用来统一更新 `updated_at`。`to_dict()` 是把对象变成普通字典，方便保存；`from_dict()` 是把字典变回对象。`from_dict()` return 的是一个新对象，不是字典。

## 4. 名字、对象、调用

**Q：函数名和函数有什么区别？类和类名有什么区别？为什么加不加括号差很多？**
A：名字只是引用。`hello` 是函数对象，`hello()` 是调用函数；`NoteType` 是类对象，`NoteType()` 是创建实例。核心就是：**不带括号拿到对象本身，带括号表示调用。**

---

## 5. 装饰器、语法糖、`@classmethod`

**Q：装饰器到底是什么？为什么它和函数名/函数本身有关？`@classmethod` 又是什么？**
A：因为函数本身也是对象，所以可以被传进别的函数里处理。装饰器本质就是：`f = deco(f)`。`@classmethod` 也是这个逻辑，它把普通函数变成“调用时自动接收类本身”的方法，所以 `from_dict()` 适合用它。

---

## 6. `self`、`cls`

**Q：`self` 和 `cls` 到底是什么？**
A：`self` 是实例对象，`cls` 是类本身。实例方法处理“某个对象”，类方法处理“这个类”。

## note 模块整理

- `models.py`：放 `Note`、`NoteType`
- `service.py`：放 note 的业务逻辑，如 create / update / judge
- `repository.py`：放存储逻辑，如内存暂存 `InMemoryNoteRepository`
- `__init__.py`：统一导出，方便其他模块 import
- `exceptions.py`：自定义异常，可后补
- `utils.py`：工具函数，可后补

# **2026-03-23**

```
项目当前框架：

1. models：管对象本身

- Note：note 数据对象，负责基础合法性、默认值、checksum、refresh
- NoteType：note 的结构说明书，定义字段和 kind

2. repository：管存取

- InMemoryRepository：负责 add/get/update/delete/list
- 不负责复杂业务规则

3. service：管业务流程

- NoteService：负责 create/get/list/update/delete/is_duplicate
- 负责字段数校验、查重、更新流程组织

核心关系：
NoteType -> Service -> Repository -> Note

判断一个方法放哪里：

- 对象自身逻辑 -> model
- 存储动作 -> repository
- 业务规则 -> service
```

---

## 1. `Repository` 和 `Service` 都有 CRUD，区别是什么？

**答：**不是一回事。
`Repository` 的 CRUD 是“存取动作本身”。
`Service` 的 CRUD 是“带业务规则的完整流程”。

---

## 2. `exclude_note_id` 是做什么的？

**答：**更新时查重用来排除自己。
否则一条 note 更新时会把自己也算进重复项，误判为 duplicate。

---

## 3. duplicate 应该怎么改？

**答：**改成“纯 checksum 比较”。
不要为了查重临时创建 `Note` 对象。
应该把 checksum 计算提成普通函数，然后 `service.is_duplicate()` 直接比较 checksum

---

## 4. `service.create_note()` 第一个参数该传什么？

**答：**长期设计更合理的是传 `note_type_id`。
但因为目前还没做 `NoteType` 存取层，所以暂时先放一放，后续再改

---

## 5. `exceptions.py` 是做什么的？

**答：**放自定义异常类。
当前不是必须，后面错误类型变多、测试需要精确断言、或者接 API 层时再引入。

---

## 7. `card` 模块里的 model / repo / service 又怎么分？

- model：`Card` 本体长什么样
- repo：`Card` 怎么存取
- service：根据 `Note` 和 `NoteType` 生成 card，处理 card 的业务规则

---

## `note` 和 `card` 里的 `repo` / `service` 区别是什么？

**区别在于它们服务的对象和业务目标不同。**

### 在 `note` 模块里

- `repo`：负责 `Note` 的存取
- `service`：负责 `Note` 的业务规则，比如创建校验、字段数校验、查重、更新流程

### 在 `card` 模块里

- `repo`：负责 `Card` 的存取
- `service`：负责 `Card` 的业务规则，比如根据 `Note` 和 `NoteType` 生成 card、决定生成几张、front/back 怎么映射

一句话就是：

**`note.service` 管 note 怎么合法地创建和修改；`card.service` 管 note 怎么被加工成 card。**

---

## 8. 这是不同的数据库存取吗？

**不是重点在“数据库不同”，而是“存取对象不同”。**

- `note.repository` 存的是 `Note`
- `card.repository` 存的是 `Card`

以后很可能是：

- 同一个数据库
- 不同表

比如：

- `notes` 表
- `cards` 表

所以更准确地说是：

**不同对象各有自己的 repository，不一定是不同数据库。**

## 当前决策

- 现阶段先认为 note 模块代码基本可用
- 暂不做自动化测试流程
- `create_note(note_type_id, ...)` 的改动先记入后续开发日志
- 下一阶段进入 `card` 模块设计

# **2026-03-24**

### card model 负责什么

定义“卡片对象本身有哪些属性、有哪些最基本行为”。

例如：

- 这张卡属于哪个 note
- 它是 note 的第几张派生卡
- 当前状态是什么
- 当前到期时间是什么
- 间隔、难度这些调度字段是什么

### card repository 负责什么

负责 card 的存取：

- add card
- get by id
- get by note id
- update
- delete

它只管“存和取”，不管业务规则。

### card service 负责什么

负责业务流程：

- 根据一个 note 创建对应 card
- 查找待复习 card
- 提交评分后更新 card 状态
- 调用 scheduler 算法改 card



# **2026-03-30**

render——把card和note联系起来，生成用户看见的card

review logger

```

self.status=status # new, learning, review, relearning 当每次调出review/learn的时候更新状态。
new-good=learning
new-again/unknow/forget=new
learning*(how many times)=review
review-good(how many times)=finish(常见调度算法有这个状态吗？complete)
complete再次调度-again/unknow/forget=relearning
relearning+good（*多少次）=complete（这个有必要和review区别吗）
self.due=due if due is not None else datetime.now(timezone.utc).date() scheduler控制，但是记录在review里？还是直接从scheduler里调用？
self.interval=interval scheduler控制，每天调用倒数-1
self.ease=ease 放到schedule里方便算法判断，reviewlog再调用这个算法
self.reps=reps review一次++
self.lapses=lapses review/relearning错误一次++，用到scheduler里，错的次数越多后期调出越频繁？
self.updated_at=updated_at if updated_at is not None else now  状态更新时间也要更新（只要碰到card就更新）
```

# **2026-03-31**

已完成：

```
`note_type/`：NoteType 和 registry
`note/`：Note model + repo + service
`card/`：Card model + repo + service
`render/`：根据 note/card 渲染 front/back
`scheduler/`：根据 rating 算下一状态
`reviewlogger/`：写入复习日志
```

指定一条 note，生成 card——指定一张 card，render——指定一个 rating，更新它

core engine未完成：

今天该复习哪张？

新卡、学习中卡、复习卡，谁先出？

一次学习 session 怎么连续取下一张？

deck 限额、每日新卡上限、复习上限怎么算？

learning steps 是分钟级还是天级？

sibling bury 怎么处理？

用户看到的 Again / Hard / Good / Easy 四个按钮怎么映射？

复习统计怎么从 revlog 汇总出来？

new core engine index

| 优先级 | 模块                                  | 当前状态              | 主要职责                                                     | 下一步动作                                                   |
| ------ | ------------------------------------- | --------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| P0     | `note_type/`                          | 已完成基础版          | 定义 Basic / BasicReverse / Cloze 等 note type，决定 note 如何生成 card | 先不大改，只保持接口稳定                                     |
| P0     | `note/`                               | 已完成基础版          | 管理 note 原始内容、字段校验、去重、CRUD                     | 后续只补和 deck / search 的关联字段                          |
| P0     | `card/`                               | 已完成基础版          | 管理 card 实体、状态、间隔、ease、reps、lapses 等            | 后续补 `deck_id`，必要时把 `due` 升级为 `datetime`           |
| P0     | `render/`                             | 已完成基础版          | 根据 `note + card.template_ord` 渲染真实 front/back          | 后续只补 cloze 边界情况                                      |
| P0     | `scheduler/`                          | 已完成 v1             | 根据 rating 计算下一次状态、due、interval 等                 | 下一版扩成 `again/hard/good/easy`，补 learning steps         |
| P0     | `revlog/`（你现在是 `reviewlogger/`） | 已完成基础版          | 记录每次复习前后变化                                         | 模块名建议统一成 `revlog/`                                   |
| P1     | `study/` 或 `session/` **新增**       | 未开始                | 管理一次学习会话：取下一张卡、排序队列、提交评分、返回下一张 | 立刻开做。先实现 `get_next_card()` / `answer_card()` / `get_counts()` |
| P1     | `deck/`                               | 未开始                | 管理牌组，卡片归属，支持按 deck 学习                         | 先做最小版：`Deck model + repo + service`，并给 `Card` 增加 `deck_id` |
| P1     | `deckconfig/`                         | 未开始                | 管理学习步长、毕业间隔、每日新卡数、复习上限等               | 先做最小配置：`new_per_day`、`review_per_day`、`learning_steps`、`graduating_interval` |
| P2     | `collection/`                         | 未开始                | 作为总入口，协调 note/card/deck/review/session 等模块        | 在 `study + deck + deckconfig` 稳定后再做 facade             |
| P2     | `storage/`                            | 未开始                | 从 in-memory 迁到 SQLite，负责持久化                         | 等 session/deck 稳定后统一落库                               |
| P2     | `stats/`                              | 未开始                | 基于 revlog 做学习统计、到期数量、复习量等                   | 先做最小版：今日复习数、again 次数、按天聚合                 |
| P2     | `search/`                             | 未开始                | 按关键词、tag、deck、状态查 note/card                        | 先做 service 层筛选，不急着复杂查询语法                      |
| P3     | `tags/`                               | 部分已有（note.tags） | 管理标签与筛选                                               | 暂时不单独建模块，先让 `search` 直接用 `note.tags`           |
| P3     | `config/`                             | 未开始                | 全局系统配置                                                 | 后面和 deckconfig 区分开再做                                 |
| P3     | `undo/`                               | 未开始                | 撤销操作                                                     | 等 collection / storage 稳定后再考虑                         |
| P4     | `import_export/`                      | 未开始                | 导入导出学习内容                                             | 后面做文本导入即可                                           |
| P4     | `media/`                              | 未开始                | 图片、音频、文件引用                                         | 等 card/render 稳后再扩                                      |
| P4     | `browser_table/`                      | 未开始                | 为浏览器表格视图准备列数据                                   | 放后面                                                       |
| P4     | `backend/`                            | 未开始                | 对外暴露统一 API                                             | 等 collection 成熟后再封装                                   |
| P5     | `dbcheck/`                            | 未开始                | 数据一致性检查与修复                                         | SQLite 上线后再做                                            |
| P5     | `sync/`                               | 未开始                | 云同步、账号、媒体同步                                       | 很后面再说                                                   |



# **2026-04-01**

## 计划

| 周数 | 重点 | 你现在基础上要完成的内容 | 产出 |
| ---- | ---- | ------------------------ | ---- |

| 第1周 | 稳定 core engine 基础层 | 清理 `note_type/note/card/render/scheduler/revlog` 接口；统一命名；补 `deck_id`、时间字段、状态字段 | 核心模型层定型 |
| ----- | ----------------------- | ------------------------------------------------------------ | -------------- |

| 第2周 | 做 `study/session` | 实现下一张卡、答题、继续下一张、session 计数；打通 render+scheduler+revlog | 系统第一次真正能连续学习 |
| ----- | ------------------ | ------------------------------------------------------------ | ------------------------ |

| 第3周 | 做 `deck + deckconfig + scheduler v2` | 支持 deck 学习；支持 again/hard/good/easy；learning/relearning steps；daily limits | 调度从 demo 升级为完整版本 |
| ----- | ------------------------------------- | ------------------------------------------------------------ | -------------------------- |

| 第4周 | SQLite + backend API | repository 落 SQLite；做 deck/note/study/review/stats API | 后端独立可跑，数据持久化 |
| ----- | -------------------- | --------------------------------------------------------- | ------------------------ |

| 第5周 | 前端 MVP | React 页面：deck 列表、创建 note、study 页面、stats 页面 | 前后端闭环打通 |
| ----- | -------- | -------------------------------------------------------- | -------------- |

| 第6周 | AI 辅助层 v1 | 做 1–2 个强相关 AI 功能：自动生成卡片、卡片质量审查、学习建议三选二 | 项目有“AI + SRS”特色 |
| ----- | ------------ | ------------------------------------------------------------ | -------------------- |

| 第7周 | 工程化与部署 | 测试、日志、错误处理、Docker、基础 CI；有余力再做 AWS 部署 | 更像完整工程项目 |
| ----- | ------------ | ---------------------------------------------------------- | ---------------- |

| 第8周 | 打磨与包装 | README、架构图、demo script、resume bullet、性能/设计 trade-off 总结 | 可投递版本 |
| ----- | ---------- | ------------------------------------------------------------ | ---------- |
|       |            |                                                              |            |

# **2026-04-02**

## 1. Note 创建流程

### 功能

创建一条 note，并存入 note repository。
 Create a note and save it into the note repository.

### 调用链

```
外部调用
→ NoteService.create_note()
    → NoteService.__validate_fields()
    → NoteService.is_duplicate()
        → InMemoryNoteRepository.get_all_notes()
        → calculate_checksum()
    → Note(...)
        → Note.__post_init__()
            → __validation_content()
            → __validate_note_type_id()
            → calculate_checksum()
    → InMemoryNoteRepository.add_note()
        → __serialize_note()
```

- 检查字段数和类型
- 检查是否重复
- 构造 Note 对象
- 生成 checksum / sort_field / 时间戳
- 存到 repo

------

## 2. Note 更新流程

### 功能

更新已有 note 的 fields / tags。
 Update the fields / tags of an existing note.

### 调用链

```
外部调用
→ NoteService.update_note(note_id, fields, tags)
    → InMemoryNoteRepository.get_note()
        → __deserialize_note()
    → get_note_type(note.note_type_id)
    → NoteService.__validate_fields()
    → NoteService.is_duplicate()
    → note.refresh()
        → calculate_checksum()
    → InMemoryNoteRepository.update_note()
        → __serialize_note()
```

- 读取原 note
- 按 note_type 再验证字段
- 防止更新成重复内容
- 重新计算 checksum / sort_field / updated_at
- 存回 repo

------

## 3. 由 Note 生成 Card 的流程

### 功能

把 note 转成实际可复习的 cards。
 Convert a note into actual review cards.

### 调用链

```
外部调用
→ CardService.create_cards_from_note(note)
    → CardService.__get_template_ords(note)
        → get_note_type(note.note_type_id)
        → (如果 cloze) CardService.__get_cloze_ords(text)
    → Card(...)
    → InMemoryCardRepository.add_card()
        → __serialize_card()
```

- 根据 note_type.kind 决定生成几张 card
- basic → 1 张
- basic_reverse → 2 张
- cloze → 按 cloze ord 生成多张
- 新生成 card 默认 `status='new'`，`due=today`

------

## 4. 渲染一张卡的流程

### 功能

把一张 card 真正变成 front/back。
 Render one card into actual front/back content.

### 调用链

```
外部调用
→ render_card(card, note)
    → get_note_type(note.note_type_id)
    → 根据 kind 分发:
        → __render_basic_card()
        → __render_basic_reverse_card()
        → __render_cloze_card()
            → __replace_cloze()
```

- basic：前后字段直接映射
- basic_reverse：根据 `template_ord` 交换 front/back
- cloze：根据 `template_ord` 决定当前目标 cloze，并在前面隐藏、后面显示答案

------

## 5. 单张卡复习（review）流程

### 功能

用户对一张 card 评分，系统更新这张 card 的状态，并写入复习日志。
 User rates a card, then the system updates the card state and writes a review log.

### 调用链

```
外部调用
→ ReviewLoggerService.review_card(card_id, rating)
    → ReviewLoggerService.__normalize_rating(rating)
    → InMemoryCardRepository.get_card(card_id)
        → __deserialize_card()
    → Scheduler_v1.schedule(card, normalized_rating)
        → __schedule_new_card()
        → __schedule_learning_card()
        → __schedule_review_card()
        → __schedule_relearning_card()
    → 把 scheduler 返回结果写回 card
    → card.touch()
    → InMemoryCardRepository.update_card(card)
        → __serialize_card()
    → ReviewLog(...)
    → ReviewLoggerRepository.add_log(log)
        → __seralize_log()
```

- 读当前 card
- 规范化 rating
- 调 scheduler 计算下一状态
- 更新 card 的：
  - `status`
  - `due`
  - `interval`
  - `ease`
  - `reps`
  - `lapses`
  - `step_index`
- 写一条 revlog

------

## 6. Study Session 流程

#### 功能

组织一轮今天的学习。
 Organize one study session for today.

------

### 6.1 启动 session

#### 调用链

```
外部调用
→ StudyService.start_study_session(today)
    → StudyService.__resolve_today()
    → InMemoryCardRepository.list_cards()
        → __deserialize_card() 逐张返回
    → StudyService.__is_eligible(card)
    → StudyService.__queue_sort_key(card)
```

- 设定今天日期
- 扫描所有 cards
- 筛选今天候选卡：
  - `status` 在合法集合里
  - `due <= today`
- 按状态分到三个 session 队列：
  - `learning_queue`
  - `review_queue`
  - `new_queue`

------

### 6.2 取下一张卡

#### 调用链

```
外部调用
→ StudyService.get_next_card()
    → StudyService.__pop_next_card()
    → InMemoryNoteRepository.get_note(card.note_id)
        → __deserialize_note()
    → render_card(card, note)
```

- 按优先级取下一张：
  - learning/relearning
  - review
  - new
- 找到对应 note
- 调 render 生成 front/back
- 返回给上层显示

------

### 6.3 回答当前卡

#### 调用链

```
外部调用
→ StudyService.answer_card(rating)
    → ReviewLoggerService.review_card(current_card_id, rating)
        → (整个 review 链)
    → StudyService.__is_eligible(updated_card)
    → StudyService.__enqueue_card(updated_card)
```

- 把评分动作交给 `ReviewLoggerService`
- review service 更新完 card 后返回 `updated_card`
- study service 决定：
  - 如果更新后这张卡仍然 `due <= today`，重新入队
  - 否则不再回今天队列

也就是说：

```
## `study` 不决定状态规则

## `scheduler` 决定状态规则

## `study` 只根据 scheduler 的结果做“是否继续今天复习”的判断
```

## 四、按功能视角再梳理一次整体流程

------

### 功能 A：做卡（Create learning content）

```
NoteType
定义模板规则
↓
NoteService.create_note()
创建原始笔记
↓
CardService.create_cards_from_note()
根据模板生成一张或多张 card
```

------

### 功能 B：看卡（Render content）

```
card + note
↓
render.render_card()
↓
front/back
```

------

### 功能 C：复习一张卡（Review one card）

```
ReviewLoggerService.review_card()
↓
Scheduler_v1.schedule()
↓
更新 card
↓
写 ReviewLog
```

------

### 功能 D：组织一整轮今日学习（Study session）

```
StudyService.start_study_session()
↓
筛 today due cards，分队列
↓
StudyService.get_next_card()
↓
render 出下一张
↓
StudyService.answer_card()
↓
ReviewLoggerService.review_card()
↓
根据 updated_card 是否 due<=today 决定是否重新入队
↓
StudyService.is_finished()
```

## Q&A

### 1. `StudyService` 的职责边界

- `start_study_session()`：只负责初始化 session，把 `due <= today` 的卡按状态分进队列。
- `get_next_card()`：只负责从队列取当前一张卡，并 render。
- `answer_current_card()`：只负责提交“当前这张卡”的评分，调用 `review_service` 更新 card，再决定是否重新入队。
- 它不是一口气跑完整轮学习的 driver，而是一个 **session 状态机接口**。

------

### 2. `start / get / answer` 是怎么串起来的

- 不是函数直接互调串起来。
- 是通过实例属性串起来：
  - `__today`
  - `__learning_queue / __review_queue / __new_queue`
  - `__current_card_id`
- 外部主循环才是完整 session：
  - `start -> get_next_card -> answer_current_card -> get_next_card -> ...`

------

### 3. `current_card_id` 的含义

- 表示：**当前已经发给用户、但还没完成这次答题处理的那张卡**
- 不是队列里的卡。
- 所以答完后应设回 `None`，因为“当前处理结束了”。
- 如果这张卡今天还要继续学，它会重新入队，等下次再被取出。

------

### 4. `is_finished()` 为什么还要判断 `current_card_id is None`

- 因为会出现：
  - 三个队列都空了
  - 但最后一张卡刚被 `pop` 出来，还没提交评分
- 所以结束条件必须是：
  - 队列全空
  - 且没有 in-progress 的当前卡

------

### 5. `is_active` 是否有必要

- 当前版本里基本是冗余的。
- 因为 session 状态已经能由：
  - `__today`
  - 三个队列
  - `__current_card_id`
  - `is_finished()`
     这些表达清楚。
- 建议删掉，避免和 `is_finished()` 互相打架。

------

### 6. `step_index` 从哪里来

- 不是外部手动输入。
- 初始值来自 `Card` 默认值：
  - `new/review` 初始一般是 `step_index = None`
- 第一次进入 `learning/relearning` 时，由 `scheduler` 返回：
  - `step_index = 0`
- 后续每次答题，再从 `card.step_index` 继续推进。

------

### 7. `step_index` 怎么和 review / scheduler 串起来

链路是：

- `card_repo.get_card(card_id)` 取出 card（里面带旧 `step_index`）
- `scheduler.schedule(card, rating)` 读取 `card.step_index`
- scheduler 返回新的 `step_index`
- `reviewlogger/service.py` 里：
  - `card.step_index = result["step_index"]`
  - `card_repo.update_card(card)` 持久化

也就是说：

- `step_index` 是 **Card 的持久化状态**
- 不是临时参数

------

### 8. scheduler 返回 dict，在哪里变成实例属性并保存

在`reviewlogger/service.py -> review_card()`

这里做了两步：

1. 手动写回 `card`：

- `card.status = result["status"]`
- `card.due = result["due"]`
- ...
- `card.step_index = result["step_index"]`

1. 再持久化：

- `self.__card_repo.update_card(card)`

所以：

- `scheduler` 只负责算 dict
- `review_service` 负责把 dict 落到 card 并存回 repo

------

### 9. `step_index` 要不要记进 `ReviewLog`

- 运行上不是必须
- 但调试、追踪状态变化很有用
- 建议记：
  - `old_step_index`
  - `new_step_index`

# **2026-04-03**

## 1. basic / basic_reverse / cloze 到底怎么生成 card

**问题：** `basic` 是一张卡还是两张？`basic_reverse` 和 `basic` 区别在哪？

**结论：**

- `basic`：**1 note -> 1 card**，这张 card 有 `front/back` 两面。
- `basic_reverse`：**1 note -> 2 cards**，分别是正向卡和反向卡。
- `cloze`：**1 note -> 多张 cards**，按 `c1/c2/c3...` 的 ord 生成。
- 区别不在 fields 长相，`basic` 和 `basic_reverse` 都可以是 `[front, back]`，区别在 **note type 决定生成几个 template ord**。

------

## 2. card_id 和 template_ord 分别是干什么的

**问题：** 既然有 `template_ord`，为什么还要 `card_id`？正反卡能不能共用一个 card_id？

**结论：**

- `card_id`：这张 card 自己的唯一身份。
- `template_ord`：这张 card 在所属 note 里的“位置/角色”。
- `note_id + template_ord` 可以定位“这是哪一张派生卡”，但不能替代 `card_id` 作为独立实体主键。
- 正反向卡不能共用一个 `card_id`，因为它们是两张**独立调度对象**，`due/ease/reps/lapses` 可以不同。

------

## 3. 现在有没有做句子切分

**问题：** 长句是不是会自动拆开做卡？

**结论：**

- **没有做句子切分。**
- `basic/basic_reverse`：整段字段内容直接做卡，不会按标点拆。
- `cloze`：只是扫描 `{{c1::...}}` 这种标记生成 ord，不是切句。
- 句子切分属于**制卡前预处理**，不是 scheduler / render 的职责。

------

## 4. `reconcile_cards_for_note()` 的作用

**问题：** 这个方法到底干什么？为什么不能只 delete？

**结论：**
 `reconcile_cards_for_note(note)` 的作用是：

**让“当前 note 应该拥有的 card 集合”和“仓库里实际存在的 card 集合”保持一致。**

它做三件事：

- 不该存在的 card -> 删掉
- 缺失的 card -> 补上
- 仍然有效的旧 card -> 保留原来的调度数据

为什么不能只 delete：

- update note 时，不只是“删旧卡”，还有“保留旧卡”和“新增新卡”。
- 如果你“全删再重建”，旧卡原来的复习进度会丢掉。

所以：

- **create/update note**：用 `reconcile`
- **delete note**：按 `note_id` 级联删整组 cards

------

## 5. reviewer 流程顺序到底是什么

**问题：** 是 `get -> answer -> reveal` 还是别的？

**结论：**
 正确流程是：

**`get_next_card() -> reveal_back_of_current_card() -> rate_current_card()`**

不是 `get -> answer -> reveal`。

原因：

- `answer_current_card()` 现在的真实语义不是“作答内容”，而是“提交评分”
- 一旦评分结束，这张 card 本轮就结束了，`current_card_id` 应该清空
- 所以 reveal 必须发生在 rate 之前

------

## 6. `answer_current_card()` 这个名字是否准确

**问题：** 这里的 answer 根本不是“回答”吧？

**结论：**
 对，它现在不是“回答内容”，而是“评分”。

更准确的名字应该是：

- `rate_current_card()`
- 或 `submit_rating()`

当前这个函数做的其实是：

- 根据 rating 调 scheduler
- 更新 card
- 写 review log
- 必要时重新入队

它没有处理“用户输入答案文本”。

------

## 7. 现在要不要做“用户输入答案 + 自动判对错”

**问题：** 现在要不要补 typed answer，后面用正则判断对错？

**结论：**
 **现在不建议做。**

当前阶段先把主线做稳：

- 出题
- reveal
- rating
- scheduler
- requeue
- revlog

原因：

- SRS 核心依赖的是 **rating**，不是自由文本答案
- 正则判对错只适合很窄的题型
- 自动判题会把 reviewer 层和 scheduler 层搅乱

后面如果做 typed answer，更适合作为**可选增强**：

- 用户输入答案
- 系统做辅助比对
- 最终 rating 仍然由用户自己选

------

## 8. `today` 为什么要一路传下去

**问题：** `reviewlogger/service.py` 里调 scheduler 为什么要传 `today`？不传或写 `None` 行不行？

**结论：**

- 技术上：不传也能跑，scheduler 可以回退到系统当天
- 设计上：既然 `StudyService.start_study_session(today=...)` 已经引入 session date，就应该一路传到底

这样才能保证：

- session 里判断 eligibility 用的是同一个 today
- scheduler 更新 due 也用同一个 today

否则测试和复现会乱。

------

## 9. 今天补的测试重点

**问题：** 当前阶段该测什么？

**结论：**
 今天明确了要补这类测试：

### Study 连续学习流

- 能出卡
- 能评分
- 评分后同一天重新入队
- 连续学习直到 graduate 后不再入队

### 典型场景

- `new + again`：今天重入队
- `new + 连续 good`：从 `learning` 学到 `review`
- `review + again`：进入 `relearning` 并重入队

这些测试能证明：

- study session
- scheduler
- requeue
- revlog

这条核心闭环已经通了。

------

## 10. 当前阶段最该继续做什么

**问题：** 这阶段后面优先级是什么？

**当前阶段主测试不该围绕“用户输入接口”，而该围绕“study service 接口”。**
 用户输入接口可以加，但应该作为一层很薄的 adapter，单独测，不要和 engine 测试绑死。

**简短回顾：**你说的“用户输入接口”更适合交互层测试；当前 core engine 阶段应优先直接测试 `get / reveal / rate` 这些 service 接口，把调度与重入队逻辑先测稳，再在外层补输入映射测试。

**结论：**
 先做这几个：

1. 修 `reconcile` / `delete_card` / 方法名不统一 这些 bug
2. 把 `get -> reveal -> rate` reviewer 流程整理干净
3. 补连续学习与 requeue 测试
4. 补 `basic_reverse` 和 cloze ord 增减测试
5. 保持 note-card 生命周期自动同步

暂时先不做：

- typed answer 自动判题
- deck / SQLite / API / 前端
- 更完整的 FSRS / daily limits



# **2026-04-04**

## Coding

### 1. SQLite 这一阶段到底做什么

**问题整合：现在要不要开始 SQLite？SQL 放哪？做几张表？**

**结论：**
 现在开始做 SQLite 是对的，但目标只是做**最小持久层**，不是一次做完整数据库系统。
 参照 Anki 的放法，`schema.sql` 放在：

```
coreengine/storage/schema.sql
```

这一阶段只做三张表：

- `notes`
- `cards`
- `review_logs`

先不做：

- `note_types` 表
- `deck`
- `tags` 关联表
- `media`
- migration

**核心原则：**
 先让 `note / card / reviewlog` 能真实落库，方便后续模块测试，不提前把结构做重。

------

### 2. 表字段怎么设计，尤其是 `due / created_at / NULL`

**问题整合：为什么 `due` 不默认时间？为什么 `review_logs` 里的 due 可以是 `NULL`？`created_at DEFAULT CURRENT_TIMESTAMP` 有没有问题？**

**结论：**
 这些字段语义不一样，不能一概而论。

### `cards.due`

虽然源码里构造参数写的是：

```
due: date | None = None
self.due = due if due is not None else today
```

但这说明的只是：**输入时可以不传**，不是最终对象状态允许长期为 `None`。
 `Card` 实例创建完以后，`due` 已经被补成具体日期了，所以数据库里更适合：

```
due TEXT NOT NULL
```

### `review_logs.old_due / new_due`

这是**历史快照字段**，记录某次复习前后的变化，允许为空是正常的。
 所以 log 里的 `due` 可空，和 `cards.due` 非空并不冲突。

### `created_at`

`DEFAULT CURRENT_TIMESTAMP` 只在插入时生效一次，不会自动反复更新。
 真正要防止它被改，主要靠 repo 的 update 逻辑不要去改它。

**总原则：**

- 当前状态字段：尽量非空
- 历史快照字段：可以为空
- 默认值只该给“元信息字段”，不该乱给业务调度字段

------

### 3. 外键和索引到底在干嘛

**问题整合：`FOREIGN KEY ... ON DELETE CASCADE` 是什么？索引名字怎么理解？为什么查询写 `note_id=?` 不写索引名？**

**结论：**

#### 外键

```
FOREIGN KEY(note_id) REFERENCES notes(id) ON DELETE CASCADE
```

意思是：

- `cards.note_id` 必须引用真实存在的 `notes.id`
- 如果 note 被删，相关 cards 自动一起删

作用：防止出现“note 没了但 card 还留着”的脏数据。

#### 索引

```
CREATE INDEX idx_cards_note_id ON cards(note_id);
```

这里：

- `idx_cards_note_id` 只是**索引对象的名字**
- 真正起作用的是 `ON cards(note_id)`，表示数据库额外维护了一份按 `note_id` 组织的查找结构

所以查询时仍然写：

```
SELECT * FROM cards WHERE note_id = ?;
```

不是写索引名。
 索引名只是给数据库内部那份“目录”取个名字，不是表字段。

**一句话：**
 外键解决“引用关系正确”，索引解决“查询速度更快”。

------

### 4. 连接层和路径怎么写

**问题整合：下一步写什么？`create_connection(...)` 是什么意思？没有 db 文件能不能先写？数据库目录和 coreengine 同级时路径怎么处理？**

**结论：**
 三张表定完以后，下一步不是马上写 repo，而是先写：

1. `sqlite_connection.py`
2. `schema.py`
3. `note_sqlite_repository.py`

`create_connection(...)` 本质上就是一个“创建 SQLite 连接”的函数。
 即使现在还没有 `.db` 文件也没关系，SQLite 第一次连接时可以自动创建。

如果你的目录是：

```
project_root/
  coreengine/
  database/
```

那不要写脆弱的裸相对路径，而是从 `sqlite_connection.py` 所在文件位置反推到项目根目录，再拼出：

```
database/anki_demo.db
```

### 5. today 传递链打通

**问题：** session 用固定 `TODAY`，但建卡/补卡如果没传 `today`，会回退到系统当天，导致测试取不到卡。
 **修改：**

- `card/service.py`
  - `create_cards_from_note(self, note, today=None)` 支持外部传 `today`
  - `reconcile_cards_for_note(self, note, today=None)` 支持外部传 `today`
  - 新建 card 时统一使用：
    - `today if today is not None else system_today`
- `note/service.py`
  - `create_note(..., today=None)` 把 `today` 继续传给 `card_service`
  - `update_note(..., today=None)` 同样把 `today` 传下去
- `reviewlogger/service.py`
  - `review_card(..., today=None)` 接收 session 的 `today`
- `scheduler/simple_scheduler.py`
  - `schedule(..., today=None)` 支持外部传入日期
- `study/service.py`
  - `rate_current_card()` 调 `review_service.review_card(..., today=self.__today)`
     **结论：** create card / study session / review / scheduler 现在都可以共享同一个测试日期，避免 due 与 session 日期不一致。

------

### 6. note-card 生命周期同步完善

**问题：** note 更新后 card 集合可能失真；删除 note 后可能留下孤儿 card。
 **修改：**

- `card/repository.py`
  - 新增按 `note_id` 批量删除 card 的能力
  - 修正 `delete_card()`，确保真正删除而不是只检查
- `card/service.py`
  - 增加/整理 `reconcile_cards_for_note(note, today=None)`
  - reconcile 规则明确为：
    - 多余 ord -> 删除
    - 缺失 ord -> 新增
    - 仍然有效 ord -> 保留原 card
- `note/service.py`
  - `create_note()` 后自动同步 cards
  - `update_note()` 后自动同步 cards
  - `delete_note()` 时先删该 note 的全部 cards，再删 note
     **结论：** note 和 card 的生命周期绑定起来了，不再依赖外部手动补同步。

------

### 7. 测试体系补齐

**问题：** 之前测试主要是零散验证，看不到完整流程，也缺少 reverse / cloze / reviewlog 覆盖。
 **修改：**

- `test.py` / `test_basic.py`
  - 增加并修正 `build_app()` 与 helper
  - helper 显式传 `today=TODAY`
  - 补充连续学习、重新入队、非法流程测试
- 新增/完善：
  - `test_reverse.py`
  - `test_cloze.py`
  - `test_reviewlog.py`
- 测试覆盖内容包括：
  - `basic_reverse` 两张卡是否正确生成与正反 render
  - `cloze` 的 ord 增删是否正确同步
  - `reviewlog` 的 old/new 字段是否正确记录
  - `get -> reveal -> rate` 连续学习流是否正常
     **结论：**当前 core engine 的关键分支基本都有测试覆盖。

------

### 8. demo 流程可视化

**问题：** assert 测试只能看通过/失败，看不到输入输出和日志长什么样。
 **修改：**

- 新增/整理 `demoflow.py`
  - 打印：
    - create note 输入输出
    - get_next_card 返回内容
    - reveal_back_of_current_card 返回内容
    - rate_current_card 后 card 新状态
    - review log 结构
       **结论：**除了断言测试，现在还有一个可视化 demo 脚本用来直接观察流程效果。

------

### 9. 包结构与运行方式统一

**问题：** 直接运行测试文件会报 `ModuleNotFoundError: No module named 'coreengine'`。
 **修改：**

- 统一项目按包模式运行：
  - 从项目根目录使用 `python -m coreengine.test.xxx`
- 调整包结构与 import 使用方式，避免脚本式导入和包式导入混用
- 补齐 `__init__.py` 相关包标识
   **结论：**测试与模块导入方式从“单文件脚本运行”转向“包级模块运行”

## DESIGN QUESTION

### 1. 当前阶段完成度与主线判断

- 当前 `core engine` 的基础闭环已经打通：`note -> card -> render -> study session -> scheduler -> review log`。
- `basic / basic_reverse / cloze / reviewlog` 相关测试已补齐并通过，说明这一阶段的核心模型和学习流程基本稳定。
- 当前可以进入下一阶段，但要明确下一阶段是“继续补核心学习规则”还是“开始做持久化基座”。

------

### 2. 关于下一步到底先做什么

- 最开始给出的周计划里，第 3 阶段本来应该先做：
  - `deck`
  - `deckconfig`
  - `scheduler v2`
  - `again/hard/good/easy`
  - `learning/relearning steps`
  - `daily limits`
- 之前建议先做 SQLite，是从“工程落地”和“尽快有真实持久化系统”的角度出发，不是唯一顺序。
- 当前结论是：
  - **如果严格按功能演进走**：先做 `deck + scheduler v2`
  - **如果从测试和后续系统地基考虑**：先做一个**最小 SQLite 基座**也合理
- 你当前的计划表是可以动态调整的，不是死规定。

------

### 3. 关于 SQLite 是否该提前做

- SQLite 不是一种新语言，而是一个轻量级嵌入式数据库，用的仍然是 SQL。
- Python 自带 `sqlite3`，所以环境上几乎不需要额外复杂配置。
- 如果现在先做 SQLite，后面大概率还会继续补：
  - 新表
  - 新字段
  - schema 调整
- 但只要你现在定位成**最小持久化**，复杂度是可控的。
- 当前适合的做法不是“一次设计完整数据库”，而是：
  - 先只持久化 `notes / cards / review_logs`
  - 把 SQLite 当成**后续 deck 等功能的测试基座**
- 从测试角度讲，先做最小 SQLite 是有帮助的，因为后面 deck/config/stats 的很多问题本质上是“查询和持久化问题”，不是纯逻辑问题。

------

### 4. 关于 PostgreSQL 什么时候上

- PostgreSQL 现在还不该上。
- 更合理的顺序是：
  - `in-memory`
  - `SQLite`
  - `PostgreSQL`
- PostgreSQL 更适合在这些条件出现后再上：
  - schema 基本稳定
  - API 已开始做
  - 前后端开始真正联调
  - 需要更接近真实后端部署
- 当前更适合先 SQLite，等 API 和后端结构稳定后再换 PostgreSQL。

------

### 5. 关于最小可运行 stack 的确认

- 当前最小 MVP stack 可以明确为：
  - **React + TypeScript**
  - **FastAPI**
  - **Python engine**
  - **SQLite**
- Redis 现在基本用不上。
- Redis 主要在以下场景才有意义：
  - 异步任务
  - 缓存
  - 队列
  - 多用户、更真实部署
- 对当前这个单机学习引擎 demo，Redis 不是必需品。

------

### 6. 关于运行日志是否要单独存表

- 当前要区分两类日志：
  1. **业务日志**：例如 `review_logs`，记录卡片评分和状态变化，这类必须入库
  2. **运行日志**：例如 bug/warning/error，这类是工程调试日志
- 当前阶段不建议优先把运行日志做成数据库表。
- 更合理的做法是：
  - `review_logs` 继续作为业务表保留
  - 程序运行日志先写文件（如 `app.log`）
- 后面如果真的需要做“错误历史查询 / 后台查看 warning / 前端展示运行异常”，再单独设计 `app_logs` 表。

------

### 7. 关于 Go / 多语言替换时机

- 可以逐步替换成 Go，但现在不应该因为“项目不想纯 Python”就马上动主干。
- 纯 Python 在原型和核心模型快速演进阶段是正常的，不丢人。
- 当前更重要的是：
  - 边界清晰
  - 测试稳定
  - 模型可替换
- 更合理的替换方式不是“现在直接把 core engine 改成 Go”，而是：
  - 先把 Python 完整版本做稳
  - 之后挑独立模块、worker 或 service 逐步替换
- 当前阶段做 Go 的正确方向是“预留替换点”，不是立刻迁移主干
