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
| Engine      | Python + Rust              |

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

