// 定义 API 返回的 JSON 类型
// backend post /users/login 返回的 JSON 类型
export type TokenResponse = {
  access_token: string; // JWT token, used to authenticate user, saved in localStorage
  token_type: string; // "bearer", token type
};

// user info type, backend get /users/me 返回的 JSON 类型
// backend GET /users/me or POST /users/register 返回的 JSON 类型
export type UserOut = {
  user_id: number;
  email: string;
  username: string;
  phone: string | null;
  created_at: string;
  updated_at: string;
};

//DECK type, backend GET /decks 返回的 JSON 类型
export type DeckOut = {
  user_id: number;
  deck_id: number;
  deck_name: string;
  deck_description: string;
  is_default: boolean;
  created_at: string;
  updated_at: string;
};

// Note type, backend GET /notes 返回的 JSON 类型
export type NoteOut = {
  user_id: number;
  note_id: number;
  note_type_id: number;
  fields: string[];
  tags: string[];
  hint: string;
  sort_field: string;
  checksum: string;
  created_at: string;
  updated_at: string;
};

// StudySession type, backend GET /study/sessions 返回的 JSON 类型
export type StudySessionOut = {
  user_id: number;
  session_id: string;
  deck_id: number;
  deck_name: string;
  learning_queue: number;
  review_queue: number;
  new_queue: number;
};

// StudyCard type, backend GET /study/sessions/{session_id}/next 返回的 JSON 类型
export type StudyCardOut = {
  card_id: number;
  note_id: number;
  deck_id: number;
  template_ord: number;
  status: string;
  due: string;
  interval: number;
  ease: number;
  reps: number;
  lapses: number;
  step_index: number | null;
};

// StudyNote type, backend GET /study/sessions/{session_id}/next 返回的 JSON 类型
export type StudyNoteOut = {
  note_id: number;
  note_type_id: number;
  fields: string[];
  tags: string[];
  hint: string;
  sort_field: string;
  checksum: string;
  created_at: string;
  updated_at: string;
};

// StudyNextOut type, backend GET /study/sessions/{session_id}/next 返回的 JSON 类型
export type StudyNextOut = {
  finished: boolean;
  user_id: number;
  session_id: string;
  card: StudyCardOut | null;
  note: StudyNoteOut | null;
  front: string | null;
  status: string | null;
  step_index: number | null;
  deck_id: number | null;
  hint_available: boolean;
};

// StudyHintOut type, backend GET /study/sessions/{session_id}/hint 返回的 JSON 类型
export type StudyHintOut = {
  back: string;
};

// StudyBackOut type, backend GET /study/sessions/{session_id}/back 返回的 JSON 类型
export type StudyBackOut = {
  back: string;
};

// StudyRateOut type, backend POST /study/sessions/{session_id}/rate 返回的 JSON 类型
export type StudyRateOut = {
  card: StudyCardOut;
  log: unknown;
};
