# 之前讨论过的代码问题总结：按前后端分类

> 审查对象：当前 `demo.zip` 以及此前围绕该项目反复讨论过的问题  
> 说明：本文件不按具体文件逐行展开，而是把问题抽象成类别，方便作为后续重构/开发 checklist。

---

## 1. 总体问题主线

这个项目的问题不是“某一两个函数写错”，而是从单机 core engine 原型逐步扩展到 Web App 时，出现了几类典型过渡问题：

```text
单用户 → 多用户
内存状态 → 持久化状态
脚本调用 → HTTP API
后端原型 → 前端可调用接口
局部测试 → 全链路测试
设计文档 → 当前代码实现
```

因此，之前讨论的多数问题都可以归为以下几类：

- 数据归属没有完全统一。
- 接口 contract 没有完全对齐。
- service / repository 边界需要收紧。
- session 状态不能只依赖内存。
- 测试还混有旧版本调用方式。
- 前端目前还没有真正接成产品页面。
- 复杂基础设施不应早于 MVP 闭环。

---

# 2. 后端 / Core Engine 问题分类

## 2.1 多用户隔离问题

之前最大的一类问题是：项目从单用户模式切到多用户模式后，所有核心数据都必须带上 `user_id`。

涉及对象包括：

```text
user
 deck
 note
 card
 review_log
 study_session
```

核心原则是：

```text
所有读取、更新、删除，都不能只靠业务对象 id。
必须同时限制 user_id。
```

否则会出现：

- 用户 A 查到用户 B 的 deck。
- 用户 A 用自己的 session 操作别人的 card。
- note/card/review_log 查询越权。
- default deck 被多个用户错误共享。

当前代码已经开始系统性加入 `user_id`，这是正确方向。剩余问题主要是测试、前端类型、部分接口返回结构还没有完全同步。

---

## 2.2 Note / Card / Deck 数据关系问题

之前反复明确过一个核心设计：

```text
Note 是源内容。
Card 是复习对象。
Deck 组织 Card，不直接组织 Note。
```

这类问题的本质是数据建模问题，不是简单代码语法问题。

正确关系应该是：

```text
Note 负责保存原始学习内容
NoteType 决定一个 Note 生成几张 Card
Card 保存具体复习状态
Deck 负责组织 Card
ReviewLog 记录 Card 的复习事件
```

常见错误倾向是：

- 想让 deck 直接存 note list。
- 创建 note 时不清楚 deck_id 应该传给谁。
- 更新 note 后忘记同步 card。
- 删除 deck 时没有明确 card 是移动还是删除。

当前方向已经调整为：创建 note 后由 CardService 生成 cards，并把 cards 放入目标 deck。这是更合理的模型。

---

## 2.3 Service / Repository 边界问题

项目中一直需要避免的结构性问题是：

```text
Repository 只做存取。
Service 做业务流程。
Scheduler 只计算，不保存。
Render 只渲染，不改状态。
Router 只处理 HTTP，不写业务规则。
```

之前出现过的许多 bug，本质上是边界不清造成的。

例如：

- repository 返回值语义不统一。
- service 里假设 repository 一定是某种实现。
- scheduler 计算结果没有明确由谁持久化。
- note 更新后 card reconcile 应该由 service 协调，而不是散落在外部调用。

现在项目已经明显向分层架构靠拢，但仍需要继续保持这个原则，避免后续前端接入时把业务规则写进 router 或页面里。

---

## 2.4 事务边界问题

之前讨论过一个非常关键的问题：某些操作必须是原子操作。

典型场景：

```text
创建 note
  ↓
保存 note
  ↓
生成 card
```

这三步不能只成功一半。否则会出现：

- note 已保存，但 card 没生成。
- card 已更新，但 review_log 没写入。
- session 状态已改变，但评分结果没保存。

因此，后端需要明确事务边界。

当前项目已经有 transaction manager，并且在 note 创建、review、study session 等关键流程中开始使用，这是正确方向。

后续仍要继续检查：

- 一个业务动作是否横跨多个 repository。
- 如果中间失败，是否能 rollback。
- 测试是否覆盖失败回滚场景。

---

## 2.5 Study Session 状态管理问题

StudyService 之前最大的风险是“有状态对象”和“Web 请求”之间的冲突。

在脚本里，一个 service 对象内部保存当前队列没问题；但在 FastAPI 里，每个 HTTP 请求可能是独立的，甚至未来可能有多个 worker。

因此 session 状态应该持久化为：

```text
session_id
user_id
deck_id
learning_queue
review_queue
new_queue
current_card_id
current_hint_used
current_back_revealed
```

核心原则是：

```text
HTTP 请求之间不能靠 Python 对象内存保存关键业务状态。
```

当前后端已经有 SQLite session repository，这是正确方向。测试中仍可以使用 in-memory repo，但应用层不应该依赖内存 session。

---

## 2.6 Scheduler 设计问题

之前围绕 scheduler 讨论过的核心不是“公式复杂度”，而是职责边界：

```text
Scheduler 只接收当前 card 状态 + rating + context。
Scheduler 返回新状态。
Scheduler 不直接写数据库。
```

当前 scheduler v1 是简化版，支持：

- new / learning / review / relearning
- good / again
- hint_used 对 ease 的惩罚
- again 对 ease/lapses/reps 的影响

未完成的复杂能力应该后置：

- hard / easy
- deck config
- FSRS
- 真实分钟级 learning steps
- 更复杂的 lapse 策略

现在最重要的是保证当前简化规则稳定、可测试、可解释。

---

## 2.7 ReviewLog 记录问题

ReviewLog 的定位是业务日志，不是普通运行日志。

它应该记录：

```text
哪张卡
哪个用户
哪个 deck
哪次评分
评分前状态
评分后状态
是否用了 hint
复习时间
```

之前讨论过的关键点是：review log 应该是 append-style record，不应该被 scheduler 或 card update 隐式吞掉。

当前 review log 已经能记录基础状态变化。后续可以基于它做统计，但统计不是当前 MVP 前置条件。

---

## 2.8 SQLite / PostgreSQL / Redis / Kafka 的取舍问题

之前已经形成的结论是：

```text
当前 MVP 用 SQLite 是合理的。
不要为了展示技术栈而过早引入 PostgreSQL、Redis、Kafka。
```

原因：

- 当前瓶颈不是数据库性能。
- 当前还没有高并发请求压力。
- 当前没有真正需要消息队列的异步任务。
- 当前没有事件流消费场景。
- 当前最缺的是前后端闭环和测试稳定性。

合理顺序是：

```text
先稳定 SQLite + FastAPI + React MVP
再迁移 PostgreSQL
有缓存/session/rate-limit 需求时再引入 Redis
有后台任务时再引入 Celery/RQ
有事件流或多服务解耦需求时才考虑 Kafka
```

---

## 2.9 JWT / 鉴权问题

之前讨论过 JWT 的作用：

```text
后端登录成功后签发 token。
前端保存 token。
后续请求带上 token。
后端用 SECRET_KEY + HS256 验证 token 是否被篡改。
验证通过后取出 user_id。
```

这类问题本质是身份识别与数据隔离问题。

当前需要继续注意：

- token 只证明“这个请求属于哪个用户”。
- 数据查询仍必须在数据库层加 `user_id` 条件。
- 不能只靠前端传 user_id。
- 生产环境不能使用开发默认 SECRET_KEY。

---

## 2.10 测试版本不一致问题

当前全量测试失败主要不是因为新主链路完全不可用，而是因为测试集里混有旧单用户版本调用方式。

这是项目迭代中很常见的问题：

```text
代码已进入多用户版本
但旧测试仍按单用户版本调用
```

需要做的是：

- 保留有价值的测试意图。
- 把旧测试迁移到 user-scoped 调用方式。
- 删除或重写已经不符合当前架构的测试。
- 补 HTTP 层 smoke tests。

测试目标应该从“单个函数能跑”升级为：

```text
注册 → 登录 → 创建 note → 生成 card → study session → rate → review log
```

---

# 3. 前端问题分类

## 3.1 项目初始化已完成，但还不是产品前端

当前前端已经有：

- Vite
- React
- TypeScript
- tsconfig
- package.json scripts
- API client
- API 类型定义
- token 工具

但页面仍没有真正完成。

当前状态更像是：

```text
前端工程脚手架 + API 调用草稿
```

还不是：

```text
可登录、可创建内容、可学习、可展示状态的产品 UI
```

---

## 3.2 前后端 API contract 不一致问题

前端当前最大问题不是 React 组件，而是 API contract 对齐。

主要类别包括：

- 前端请求路径和后端路径不一致。
- 前端 HTTP method 和后端 method 不一致。
- 前端给 GET 请求传 body，不符合常规用法，也不匹配当前后端设计。
- 前端类型字段和后端实际返回字段不一致。
- 前端对 study session 的参数传递方式还没有完全按后端 path parameter 设计。

这类问题会导致：

```text
TypeScript 可能能编译
但浏览器真实请求会失败
```

因此，前端接入前必须先用一张 API 对照表统一：

```text
功能
后端 method
后端 path
request body
response shape
前端 api 函数
前端类型
```

---

## 3.3 Token 与登录态问题

当前前端已经开始做 token 保存与请求头注入，这是正确方向。

但完整登录态还需要：

- 登录成功后保存 token。
- 页面刷新后能读取 token。
- 请求 `/users/me` 验证当前用户。
- 未登录时跳转 login。
- 登出时清空 token。
- API 报 401 时处理失效登录态。

这些属于前端 app 层逻辑，不应该写散在每个页面里。

---

## 3.4 页面状态管理问题

当前还没有真正页面闭环，因此后续需要处理以下状态：

- 登录表单状态。
- 注册表单状态。
- deck list 加载状态。
- create note 表单状态。
- study session 当前卡状态。
- hint/back 是否已经显示。
- rating 后是否自动取下一张。
- session finished 状态。
- API loading/error 状态。

MVP 不一定需要 Redux 或复杂状态库。当前用 React local state 和少量组件拆分就够。

---

## 3.5 TypeScript 类型问题

TypeScript 的作用不是让代码变复杂，而是固定前后端数据契约。

之前讨论过的问题可以归为：

- 类型定义没有跟后端 schema 同步。
- 返回字段命名不一致。
- 某些字段后端有，前端类型缺失。
- 某些字段前端期待有，但后端实际返回不同名称。
- `unknown` 只能临时使用，后续应该定义 ReviewLog 类型。

后续应该让 `types/api.ts` 成为前端接后端的“合同文件”。

---

## 3.6 路由与页面组织问题

当前页面目录已经存在，但还未真正连到 `App.tsx`。

需要形成基本路由结构：

```text
/login
/register
/decks
/notes/new
/study/:deckId
```

并加入 protected route：

```text
未登录 → login
已登录 → 允许访问 decks/study
```

当前不需要过早做复杂 UI，优先完成可用流程。

---

## 3.7 前端构建与依赖问题

当前 TypeScript 编译可以通过，但压缩包中的 `node_modules` 带来了环境差异问题。

这类问题的本质是工程管理问题：

- `node_modules` 不应该进入项目压缩包或 Git。
- 应该通过 `package.json` + `package-lock.json` 恢复依赖。
- 跨系统时可执行权限可能失效。
- 构建应以干净安装后的结果为准。

前端后续应保证：

```text
删除 node_modules
npm install
npm run build
npm run dev
```

能在本地稳定工作。

---

# 4. 前后端共同问题

## 4.1 设计文档与代码实现不同步

项目文档里早期仍有“V1 single-user”的表述，但当前代码已经加入 user/JWT/user_id scoped data。

这不是坏事，说明项目在演进；但文档需要更新，否则后续会造成混乱。

需要同步的点包括：

- 当前已经不是纯单用户模型。
- default deck 是 per-user 的。
- note/card/deck/review/session 都应 user-scoped。
- 前端请求不应该传 user_id，而应由 token 决定当前用户。

---

## 4.2 命名与结构一致性问题

之前代码里出现过一些命名不一致、目录命名不规范、返回字段不统一的问题。

这类问题看起来小，但会影响后续维护。

需要统一：

- API path 命名。
- response 字段命名。
- schema 命名。
- repository 方法命名。
- frontend type 命名。
- 目录名拼写。

命名统一之后，前端接入会明显更容易。

---

## 4.3 “能跑”与“能作为项目展示”之间的差距

当前后端主链路能跑，但要作为完整项目展示，还需要：

- README 写清楚如何启动。
- 测试全绿。
- 前端能展示完整流程。
- 数据库初始化方式明确。
- `.env` 示例明确。
- 不提交运行产物和依赖目录。
- API contract 清晰。

所以当前阶段最重要的不是继续加功能，而是工程收口。

---

# 5. 当前优先级总结

## P0：必须先做

```text
1. 统一前后端 API contract
2. 修正前端 study API 封装
3. 把旧 pytest 迁移到 user_id 版本
4. 补后端 HTTP smoke test
5. 完成 login/register/deck/create note/study 页面闭环
```

## P1：基础产品完善

```text
1. ReviewLog 前端展示
2. Note list / deck cards 展示
3. API 错误提示统一
4. README 启动文档
5. .gitignore / 依赖 / 环境变量清理
```

## P2：后续增强

```text
1. Search / tags filtering
2. Stats dashboard
3. Deck config
4. hard / easy rating
5. 更完整 scheduler
6. PostgreSQL migration
```

## P3：暂时不要急着做

```text
1. Redis
2. Kafka
3. Celery/RQ
4. 分布式架构
5. 高并发优化
6. AI 自动制卡
7. 多设备同步
```

---

# 6. 最终判断

当前项目的主要问题已经不是“底层逻辑完全没有”，而是处在一个典型的过渡阶段：

```text
core engine 已经有骨架
backend 已经开始可用
frontend 还没有真正接上
tests 还混有旧架构
文档还没有完全追上代码
```

所以接下来最有效的开发策略是：

```text
少加新技术，多做收口。
少补复杂功能，多保证一条完整用户路径稳定。
```

只要先把“登录 → 创建内容 → 学习 → 评分 → 记录保存 → 再次进入仍正确”这条路径做稳，这个项目就已经具备基础全栈作品的核心展示价值。
