// api.ts和fastapi里schemas对应，用于定义后端返回的数据结构，前端数据校验

// 登录接口 POST /users/login 返回的数据类型
export type TokenResponse = {
  access_token: string; // 后端返回的 JWT token，前端要保存
  token_type: "bearer"; // token 类型，当前固定是 bearer
};

// 用户信息类型
export type UserOut = {
  user_id: number; // 用户 id
  email: string; // 用户邮箱
  username: string; // 用户名
  created_at: string; // 创建时间
  updated_at: string; // 更新时间
};

// Deck 类型
export type DeckOut = {
  user_id: number; // deck 属于哪个用户
  deck_id: number; // deck id
  deck_name: string; // deck 名称
  deck_description: string; // deck 描述
  is_default: boolean; // 是否是默认 deck
  created_at: string; // 创建时间
  updated_at: string; // 更新时间
};

// Note 类型
export type NoteOut = {
  user_id: number; // note 属于哪个用户
  note_id: number; // note id
  note_type_id: number; // note 类型 id
  fields: string[]; // 字段，例如 ["front", "back"]
  tags: string[]; // 标签
  hint: string; // 提示
  sort_field: string; // 排序字段
  checksum: string; // 内容校验值
  created_at: string; // 创建时间
  updated_at: string; // 更新时间
};

// 学习 session 开始后返回的数据
export type StudySessionStartOut = {
  session_id: string; // 当前学习 session 的 id
  deck_id: number; // 当前学习的 deck id
  new_queue: number; // 新卡数量
  learning_queue: number; // 学习中卡数量
  review_queue: number; // 复习卡数量
};

// Study 页面里使用的 card 类型
export type StudyCardOut = {
  card_id: number; // card id
  note_id: number; // 所属 note id
  deck_id: number; // 所属 deck id
  template_ord: number; // 模板编号
  status: string; // new / learning / review / relearning
  due: string; // 到期日期
  interval: number; // 复习间隔
  ease: number; // ease 系数
  reps: number; // 复习次数
  lapses: number; // 忘记次数
  step_index: number | null; // learning 阶段步骤，没有则为 null
};

// 获取下一张卡的返回类型
export type StudyNextOut = {
  finished: boolean; // 是否已经学完
  user_id: number; // 当前用户 id
  session_id: string; // 当前 session id
  card: StudyCardOut | null; // 有卡时是 card，没有时是 null
  note: NoteOut | null; // 有卡时是 note，没有时是 null
  front: string | null; // 卡片正面内容
  status: string | null; // 当前卡片状态
  step_index: number | null; // 当前学习步骤
  deck_id: number | null; // 当前 deck id
  hint_available: boolean; // 是否有 hint
};

// 显示 hint 后返回的数据
export type StudyHintOut = {
  hint: string; // hint 内容
};

// 显示 back 后返回的数据
export type StudyBackOut = {
  back: string; // 背面答案
};

// 评分后返回的数据
export type StudyRateOut = {
  card: StudyCardOut; // 更新后的 card
  log: unknown; // review log，暂时先用 unknown
};
