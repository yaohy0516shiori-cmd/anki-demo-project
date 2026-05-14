# Memory Anki Demo 项目结构与当前完成度说明

> 审查对象：当前上传的 `demo.zip`  
> 审查时间：2026-05-13  
> 项目定位：一个 Anki-like / flashcard 记忆系统，目标是从本地单用户 MVP 逐步扩展为带登录、多用户隔离、FastAPI 后端和 React + TypeScript 前端的完整 Web App。

---

## 1. 当前项目总体判断

当前项目已经不是最早期的纯 core engine 原型，而是进入了 **core engine + SQLite + FastAPI + 前端接口层** 的阶段。

目前已经具备的主链路是：

```text
用户注册/登录
  ↓
创建用户默认 deck
  ↓
创建 note
  ↓
根据 note type 自动生成 card
  ↓
按 deck 开始 study session
  ↓
取下一张 card 并渲染 front
  ↓
显示 hint / back
  ↓
用户评分 good / again
  ↓
Scheduler 计算 card 新状态
  ↓
更新 card + 写入 review_log
  ↓
如果今天仍需学习，则重新放回 session queue
```

但它还不能算完整产品。当前更准确的状态是：

```text
后端基础主链路：基本可跑
core engine：核心闭环已形成
SQLite persistence：已接入
多用户隔离：已经开始并覆盖主要核心表
FastAPI：已接线并可启动
前端：项目已初始化，API 封装已有，但页面和路由仍是半成品
测试：新多用户链路测试可通过，但旧单用户测试未迁移导致全量测试失败
工程化：还缺少统一启动说明、依赖说明、迁移策略、正式环境配置
```

---

## 2. 当前目录结构

当前有效目录可以按下面方式理解：

```text
memory anki demo/
├── backend/                 # FastAPI 后端接口层
│   ├── app/
│   │   ├── main.py           # FastAPI app、CORS、router 注册、/health
│   │   ├── deps.py           # 依赖注入：DB connection、repo、service、当前用户
│   │   ├── auth.py           # JWT token 创建与解析
│   │   ├── session_manager.py# 目前为空，未形成实际职责
│   │   └── routers/          # HTTP endpoint
│   │       ├── users.py
│   │       ├── decks.py
│   │       ├── notes.py
│   │       ├── study.py
│   │       └── reviews.py
│   └── schemas/              # Pydantic request/response schema
│       ├── users.py
│       ├── deck.py
│       ├── note.py
│       ├── study.py
│       └── review.py
│
├── coreengine/               # 业务核心层，不直接依赖 HTTP
│   ├── user/                 # 用户模型、用户服务、用户仓储接口
│   ├── deck/                 # deck 模型、服务、仓储接口
│   ├── note/                 # note 模型、服务、校验、checksum
│   ├── note_type/            # BASIC / BASIC_REVERSE / CLOZE 类型定义
│   ├── card/                 # card 模型、生成、查询、移动、删除
│   ├── render/               # 根据 note + card 渲染 front/back/hint
│   ├── scheduler/            # 简化调度器 Scheduler_v1
│   ├── reviewlogger/         # review log 模型、服务、仓储接口
│   ├── study/                # study session、队列、学习流程控制
│   ├── storage/              # SQLite repository + schema
│   └── test/                 # pytest 测试
│
├── database/                 # 当前本地 SQLite DB 位置
│   └── anki_demo.db           # 运行后生成，不应作为核心源码依赖
│
├── frontend/                 # React + TypeScript + Vite 前端
│   ├── src/
│   │   ├── api/               # 前端 API 调用封装
│   │   ├── auth/              # token 保存/读取
│   │   ├── types/             # TS API 类型定义
│   │   ├── pages/             # 页面文件，目前多数为空
│   │   ├── componets/         # protected route 目录，命名存在拼写问题
│   │   └── App.tsx            # 当前仍是 Vite 默认展示页
│   ├── package.json
│   ├── tsconfig*.json
│   └── vite.config.ts
│
└── readme/                   # 项目设计文档与开发日志
    ├── Product design.md
    ├── Tech doc.md
    ├── DEVELOP LOG of ANKI PRACTISE.md
    └── developlist.txt
```

`.git/`、`node_modules/`、`__pycache__/`、`.pytest_cache/` 属于本地运行或工具生成内容，不应该作为项目结构的核心部分理解，也不建议包含在后续提交或压缩包中。

---

## 3. 各层职责

## 3.1 Frontend：展示层 / 用户交互层

当前前端定位是：

```text
React 页面
  ↓
API 函数封装
  ↓
统一 apiRequest
  ↓
携带 JWT token 请求 FastAPI
```

已经存在的内容：

- Vite + React + TypeScript 项目已经建立。
- `package.json` 中已经有 `dev`、`build`、`lint` 等脚本。
- `tsconfig.json`、`tsconfig.app.json`、`tsconfig.node.json` 已经存在。
- `api/client.ts` 已经封装统一请求函数。
- `authApi.ts`、`deckApi.ts`、`noteApi.ts`、`studyApi.ts` 已经开始对应后端接口。
- `types/api.ts` 已经开始定义后端返回数据类型。
- `.env` 中已经配置 `VITE_API_BASE_URL=http://localhost:8000`。

未完成内容：

- `App.tsx` 仍是 Vite 默认页面，没有接入项目主路由。
- `pages/` 下的登录、注册、deck list、create note、study 页面基本为空。
- protected route 文件存在，但尚未形成完整前端鉴权流程。
- API 封装和后端接口还有不一致，尤其是 study 相关 path、GET/POST 使用方式、返回字段命名。
- 前端还没有真正完成“登录后进入 deck → 创建 note → 开始学习”的页面闭环。

前端当前状态可以概括为：

```text
工程壳子已建好，API 层已开始，但 UI/route/页面状态管理还没有真正完成。
```

---

## 3.2 Backend：FastAPI 接口层 / 应用编排层

后端当前定位是：

```text
HTTP request
  ↓
FastAPI router
  ↓
Pydantic schema 校验输入
  ↓
Depends 注入 service/repo/current_user_id
  ↓
调用 coreengine 完成业务
  ↓
返回 JSON 给前端
```

已经存在的内容：

- `main.py` 已经创建 FastAPI app。
- 已配置 CORS，允许本地前端访问。
- 已注册 users、decks、notes、study、reviews routers。
- `/health` 可正常返回 `{ "ok": true }`。
- `auth.py` 已实现 JWT 创建和解析。
- `deps.py` 已经把 SQLite connection、repo、service、current user 组合起来。
- `users.py` 已有 register、login、me。
- `decks.py` 已有 deck CRUD、查看 deck cards、软删除/硬删除入口。
- `notes.py` 已有 note 创建、查询、列表、更新、删除。
- `study.py` 已有 start session、next、hint、back、rate、status。
- `reviews.py` 已有按 card 查询 review logs。

当前后端主链路实测状态：

```text
/health                      可用
/users/register              可用
/users/login                 可用
/decks                       可返回默认 deck
/notes                       可创建 note，并触发 card 生成
/study/sessions              可创建学习 session
/study/sessions/{id}/next    可取下一张卡
/study/sessions/{id}/hint    可显示 hint
/study/sessions/{id}/back    可显示 back
/study/sessions/{id}/rate    可评分并写入 review log
```

未完成内容：

- 缺少正式的 API smoke test / integration test 文件。
- 部分 response schema 与实际返回字段还没有完全统一。
- 异常返回结构尚未统一，例如错误码、错误 message 格式还比较粗。
- 数据库路径、密钥、环境变量、运行模式仍偏开发环境。
- `session_manager.py` 当前为空，说明 session 管理职责已经转移到 repository，但旧文件还未清理。
- 还没有 Alembic migration 或其他数据库版本管理方式。
- 还没有完整启动文档，例如后端安装依赖、启动命令、前后端联调步骤。

后端当前状态可以概括为：

```text
FastAPI 接口已经接上 coreengine，基础业务能跑；但 API contract、测试、配置、工程化还没完全收口。
```

---

## 3.3 Core Engine：业务核心层

coreengine 是项目最重要的业务层。它不应该关心 HTTP，也不应该直接关心前端页面。它负责真正的记忆系统规则。

当前 coreengine 的主关系是：

```text
User
  └── Deck
        └── Card
              ├── Note
              └── ReviewLog

NoteType 决定 Note 如何生成 Card
Render 决定 Card 如何显示 front/back
Scheduler 决定评分后 Card 如何变化
StudySession 决定本轮学习队列如何推进
```

### User 模块

作用：

- 管理用户注册、登录、密码 hash、密码验证。
- 注册用户时创建用户自己的 default deck。
- 为多用户隔离提供 `user_id` 基础。

当前状态：基本完成 MVP 所需的用户核心能力。

未完成：

- 找回密码、修改 profile、邮箱验证等产品功能未做。
- 密码策略、安全策略仍是开发级别。

---

### Deck 模块

作用：

- 管理 deck 的创建、查询、更新、删除。
- 每个用户拥有自己的 default deck。
- deck 组织的是 card，不直接拥有 note。
- 支持把 cards 移动到其他 deck。
- 支持删除 deck 时移动 cards 到 default deck，或 hard delete cards。

当前状态：deck 已经从“缺失模块”进入可用状态，是当前主链路的一部分。

未完成：

- deck config 未实现。
- deck 层级结构未实现。
- deck 统计信息未完整实现。
- 删除规则还需要在前端产品交互上明确呈现。

---

### Note 模块

作用：

- note 是源学习内容。
- note 保存 fields、tags、hint、note_type_id、checksum。
- note 创建时会触发 card 生成。
- note 更新时会根据新的字段重新 reconcile cards。

当前状态：note CRUD 和 card 自动生成链路已形成。

未完成：

- note search 还不完整。
- tags 只是存储字段，还没有完整查询/过滤能力。
- hint 已接入学习流程，但还没有复杂展示规则。
- 更复杂的 note type/template 系统尚未实现。

---

### NoteType 模块

作用：

- 定义 note 的字段结构和 card 生成规则。
- 当前支持 basic、basic_reverse、cloze。

当前状态：V1 简化版本已可用。

未完成：

- 自定义 note type 未实现。
- 自定义模板未实现。
- 多字段复杂渲染规则未实现。

---

### Card 模块

作用：

- card 是真正被学习和复习的对象。
- card 由 note 生成。
- card 属于某一个 deck。
- card 保存学习状态：status、due、interval、ease、reps、lapses、step_index。

当前状态：card 生成、查询、删除、移动、按 deck 查 due cards 已经接入主链路。

未完成：

- card browser、批量移动、批量删除等管理功能未完成。
- card 状态统计还不完整。
- card 与 deck config 的关系尚未建立。

---

### Render 模块

作用：

- 把 note + card 转换为学习时展示的 front/back。
- basic：front/back 直接对应字段。
- basic_reverse：根据 template_ord 生成正向或反向卡。
- cloze：根据 cloze ordinal 隐藏目标答案。
- hint：从 note 中读取并在学习流程中显示。

当前状态：基础渲染能力已完成。

未完成：

- 富文本、Markdown、图片、音频、LaTeX 等 media 渲染未实现。
- answer checking 未实现，仍以用户自评为主。

---

### Scheduler 模块

作用：

- 根据 card 当前状态、rating、today、hint_used 计算新的 card 状态。
- 不直接保存数据，只返回调度结果。

当前状态：简化调度器 `Scheduler_v1` 已可用。

当前支持：

- `new → learning`
- `learning → review`
- `review + again → relearning`
- `relearning → review`
- `good / again` 两种 rating
- hint 使用后的 ease 惩罚
- again 后 lapse/ease/reps 更新

未完成：

- 暂未支持 hard / easy。
- 暂未支持 FSRS 或更完整的 SM-2 变体。
- 暂未支持 deck-level scheduling config。
- 暂未支持学习步长的真实分钟级延迟，只是 same-day 简化逻辑。

---

### ReviewLog 模块

作用：

- 每次评分后写入一条 review log。
- 记录 card 前后状态变化。
- 记录 rating、hint_used、interval/ease/reps/lapses/step_index 的变化。

当前状态：基础 review log 能写入并查询。

未完成：

- 没有统计 dashboard。
- 没有按日期范围、deck、用户学习趋势做完整分析。
- 没有前端展示 review history。

---

### Study 模块

作用：

- 创建学习 session。
- 按 deck 加载 due cards。
- 把 cards 分到 learning / review / new 三个 queue。
- 控制一轮学习中 current card、hint、back、rating 的状态。
- 评分后决定是否把 card 重新放回队列。

当前状态：学习 session 主链路已经成型。

当前队列优先级：

```text
learning / relearning > review > new
```

当前 session 持久化：

- 后端 DI 使用 SQLite session repository。
- 测试中仍有部分使用 in-memory session repository。

未完成：

- session 过期机制未实现。
- 多 tab / 重复点击 / 并发 rating 的保护还不完整。
- session resume、暂停、取消等产品行为未实现。

---

## 3.4 Storage：SQLite 持久层

当前 SQLite schema 已经包含：

```text
user
 deck
 note
 card
 review_log
 study_session
```

当前设计要点：

- 主要业务表已经加入 `user_id`。
- deck、note、card、review_log、study_session 都围绕用户隔离。
- card 中保存 `deck_id`，说明 deck 组织 card，而不是直接组织 note。
- review_log 使用 append-style 记录每次评分事件。
- study_session 保存 queue 和 current_card_id。
- 已经建立一些索引用于 user/deck/due/status 查询。
- 已开启 foreign keys、WAL、busy_timeout。

当前未完成：

- 没有 migration 工具，schema 变化仍靠手动 SQL。
- 没有 seed/reset 脚本的统一说明。
- `database/anki_demo.db` 是运行产物，不应作为源码核心依赖。
- 未来迁移 PostgreSQL 时，需要重新整理 repository 与 schema migration。

---

## 4. 当前测试状态

本次检查执行了后端和 core engine 的基础验证。

### 4.1 FastAPI 基础链路

已验证：

```text
GET  /health
POST /users/register
POST /users/login
GET  /decks
POST /notes
POST /study/sessions
GET  /study/sessions/{session_id}/next
POST /study/sessions/{session_id}/hint
POST /study/sessions/{session_id}/back
POST /study/sessions/{session_id}/rate
```

结果：基础链路可运行。

### 4.2 pytest

当前全量执行结果：

```text
20 tests total
10 passed
10 failed
```

失败原因不是核心链路完全断掉，而是旧的 `test_flow.py` 仍使用单用户时期的调用方式，例如不传 `user_id`，或创建 deck 时不传 `user_id`。当前代码已经迁移到多用户签名，所以旧测试需要同步迁移。

单独执行新的用户隔离与 review log 相关测试：

```text
9 passed
```

说明新的多用户链路测试是可以通过的。

### 4.3 Frontend TypeScript

已验证：

```text
npx tsc -b
```

结果：TypeScript 编译通过。

`npm run build` 在当前 Linux 解压环境中卡在 `vite: Permission denied`，更像是压缩包从 Windows 环境带来的 `node_modules/.bin` 执行权限问题。源码层面更重要的结论是：前端类型检查能过，但页面和 API 对齐仍未完成。

---

## 5. 已完成部分

## 5.1 Core Engine 已完成

- note / card 分离。
- basic、basic_reverse、cloze 三类 note type。
- note 创建后自动生成 cards。
- note 更新后 reconcile cards。
- deck 模块已接入 card 组织关系。
- default deck 机制已建立。
- card 存储学习状态。
- study session 三队列设计已实现。
- hint / back / rate 学习流程已接入。
- scheduler v1 已能计算基础调度结果。
- review log 已能记录评分前后状态。
- SQLite repository 已覆盖主要模块。
- transaction manager 已用于关键业务流程。
- user_id 多用户隔离已覆盖主要业务表和服务接口。

## 5.2 Backend 已完成

- FastAPI app 可启动。
- CORS 已配置。
- JWT 登录认证已建立。
- 当前用户从 Authorization header 解析。
- users/decks/notes/study/reviews routers 已建立。
- 后端依赖注入已把 repo/service/coreengine 串起来。
- 基础 API 主链路能跑通。

## 5.3 Frontend 已完成

- Vite + React + TypeScript 项目已建立。
- TypeScript 配置已存在。
- API base URL 已通过 `.env` 配置。
- token 读取与请求头注入已开始实现。
- auth/deck/note/study API 文件已建立。
- 后端数据类型已开始在 `types/api.ts` 中定义。

## 5.4 Documentation 已完成

- 已有产品设计文档。
- 已有技术设计文档。
- 已有开发日志。
- 已有 deck 开发清单。

---

## 6. 未完成部分

## 6.1 必须优先完成

1. **迁移旧测试到多用户版本**

   当前全量 pytest 失败主要来自旧单用户测试。需要统一所有测试调用方式，使它们传入 `user_id`，并使用用户自己的 default deck。

2. **对齐前端 API 封装与后端接口**

   前端 study API 仍存在路径模板、GET/POST、body 使用、返回字段命名等不一致。这会直接影响前端接入。

3. **完成前端页面闭环**

   需要至少做出：login、register、deck list、create note、study page、protected route。

4. **补后端 API smoke tests**

   用 TestClient 固化注册、登录、创建 note、study session、review log 的完整 HTTP 流程。

5. **整理运行文档**

   需要明确：Python 依赖安装、后端启动、前端启动、数据库初始化、测试命令。

---

## 6.2 可以后置完成

1. **PostgreSQL**

   SQLite 对当前 MVP 足够。PostgreSQL 应该等本地闭环稳定后再迁移。

2. **Redis**

   当前没有高并发 session、缓存、rate limit 或后台队列需求，因此 Redis 不是当前必要项。

3. **Kafka**

   当前项目没有事件流、大规模异步消费、多服务解耦需求，因此 Kafka 暂时没有实际使用场景。

4. **Celery/RQ**

   暂时没有需要后台处理的长任务。导入导出、同步、统计重算等功能出现后再考虑。

5. **高级调度算法**

   当前 scheduler v1 足够支撑 MVP。hard/easy、FSRS、deck config 可以作为后续增强。

6. **搜索、统计、导入导出、media**

   这些是产品功能增强，不是当前前后端接通的前置条件。

---

## 7. 模块之间的联系

## 7.1 用户注册链路

```text
POST /users/register
  ↓
users router
  ↓
UserService.register_user
  ↓
UserRepository.add_user
  ↓
DeckRepository.ensure_created
  ↓
为该 user 创建 Default deck
```

作用：每个用户注册后自动拥有自己的默认 deck，后续 note 不传 deck_id 时可以落到 default deck。

---

## 7.2 登录认证链路

```text
POST /users/login
  ↓
UserService.login
  ↓
verify_password
  ↓
create_access_token(user_id)
  ↓
前端保存 access_token
  ↓
后续请求携带 Authorization: Bearer token
  ↓
get_current_user_id 解析 user_id
```

作用：后端所有用户私有数据都通过 token 解析出的 `user_id` 隔离。

---

## 7.3 创建 note 与生成 card 链路

```text
POST /notes
  ↓
notes router
  ↓
NoteService.create_note
  ↓
校验 note_type + fields
  ↓
检查 duplicate
  ↓
NoteRepository.add_note
  ↓
CardService.create_cards_from_note
  ↓
根据 note_type 生成 1 张或多张 card
  ↓
CardRepository.add_card
```

作用：note 是源内容，card 是实际复习对象。创建 note 后，系统自动生成可学习的 cards。

---

## 7.4 更新 note 与 reconcile cards 链路

```text
PATCH /notes/{note_id}
  ↓
NoteService.update_note
  ↓
更新 fields / tags / hint
  ↓
如果 fields 改变
  ↓
CardService.reconcile_cards_for_note
  ↓
保留仍有效的 card
  ↓
新增缺失的 card
  ↓
删除不再需要的 card
```

作用：尤其是 cloze note，字段改变后 card 数量可能变化，所以必须 reconcile。

---

## 7.5 开始学习链路

```text
POST /study/sessions
  ↓
StudyService.start_study_session
  ↓
校验 deck 属于当前 user
  ↓
CardRepository.get_due_cards_by_deck_id
  ↓
按 status 分入 learning/review/new queue
  ↓
SessionRepository.create_session
```

作用：study session 是一次学习任务，不是 card 本身。它保存本轮学习队列和当前卡状态。

---

## 7.6 获取下一张卡链路

```text
GET /study/sessions/{session_id}/next
  ↓
StudyService.get_next_card
  ↓
从 queue 中按优先级 pop card_id
  ↓
读取 card + note
  ↓
Render.render_card
  ↓
返回 front、card 信息、note 信息、hint_available
```

作用：前端只负责展示，真正的下一张卡选择逻辑在 StudyService 中。

---

## 7.7 hint/back/rate 链路

```text
POST /study/sessions/{session_id}/hint
  ↓
标记 current_hint_used = True

POST /study/sessions/{session_id}/back
  ↓
标记 current_back_revealed = True

POST /study/sessions/{session_id}/rate
  ↓
ReviewLoggerService.review_card
  ↓
Scheduler_v1.schedule
  ↓
CardRepository.update_card
  ↓
ReviewLogRepository.add_log
  ↓
StudyService 判断是否 re-enqueue
```

作用：hint/back 是学习过程状态；rating 才会真正改变 card 状态并写 review log。

---

## 8. 下一步推荐顺序

当前不建议马上补 Redis、PostgreSQL、Kafka 或复杂分布式内容。更合理的顺序是：

```text
1. 先修前端 API 封装与后端 contract 不一致
2. 迁移旧 pytest，保证全量测试通过
3. 写后端 HTTP smoke test
4. 完成前端 login/register/deck/create note/study 页面闭环
5. 补项目启动文档和依赖文档
6. 再考虑搜索、统计、deck config、高级 scheduler
7. 最后再考虑 PostgreSQL / Redis / worker / sync
```

判断标准：

```text
只要还没有稳定做到：
用户登录 → 创建 deck/note → 开始学习 → 评分 → 下次进入仍能看到正确状态
就不应该急着上复杂基础设施。
```

---

## 9. 当前项目一句话总结

当前项目已经完成了 Anki-like 系统最核心的业务骨架：`user → deck → note → card → study session → scheduler → review log`。现在最大的工作不是继续堆新技术栈，而是把前后端接口、测试、页面闭环和工程文档收口，让它从“能跑的后端原型”变成“可以演示的最小产品”。
