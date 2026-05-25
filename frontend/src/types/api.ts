export type StudySessionStart = {
  deck_id: number;
  today: string | null;
};

export type StudySessionStatusOut = {
  finished: boolean;
};

export type StudyRating = "good" | "again";

export type StudyHintOut = {
  hint: string;
};

export type StudyBackOut = {
  back: string;
};

export type StudySessionStartOut = {
  user_id: number;
  session_id: string;
  deck_id: number;
  deck_name: string;
  learning_queue: number;
  review_queue: number;
  new_queue: number;
};

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

export type DeleteResultOut = {
  message: string;
  deleted_deck_id?: number;
  deleted_deck_name?: string;
  deleted_deck_count?: number;
  moved_card_count?: number;
  target_deck_id?: number;
  deleted_card_count?: number;
  note_id?: number;
  deleted_note_count?: number;
};

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

export type DeckCreate = {
  deck_name: string;
  deck_description: string;
};

export type DeckUpdate = {
  deck_name: string | null;
  deck_description: string | null;
};

export type DeckOut = {
  user_id: number;
  deck_id: number;
  deck_name: string;
  deck_description: string;
  is_default: boolean;
  created_at: string;
  updated_at: string;
};

export type StudyRateOut = {
  card: StudyCardOut;
  review_log: ReviewLogOut;
};

export type NoteCreate = {
  note_type_id: number;
  fields: string[];
  tags: string[];
  hint: string;
  deck_id: number | null;
};

export type NoteUpdate = {
  fields: string[] | null;
  tags: string[] | null;
  hint: string | null;
};

export type NoteOut = {
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

export type ReviewLogOut = {
  user_id: number;
  review_log_id: number;
  card_id: number | null;
  deck_id: number | null;
  note_id: number | null;
  rating: string;
  old_status: string;
  new_status: string;
  old_due: string | null;
  new_due: string | null;
  old_interval: number;
  new_interval: number;
  old_ease: number;
  new_ease: number;
  old_lapses: number;
  new_lapses: number;
  old_reps: number;
  new_reps: number;
  old_step_index: number | null;
  new_step_index: number | null;
  hint_used: boolean;
  review_time: string;
};

export type UserRegister = {
  email: string;
  username: string;
  password: string;
};

export type UserLogin = {
  email: string;
  password: string;
};

export type UserOut = {
  user_id: number;
  email: string;
  username: string;
  created_at: string;
  updated_at: string;
};

export type TokenResponse = {
  access_token: string;
  token_type: "bearer" | string; // default value is "bearer"
};

export type ReviewedDeckOut = {
  deck_id: number;
  deck_name: string;
  deck_description: string;
  review_count: number;
  latest_review_time: string;
};

export type LatestNoteReviewOut = {
  note_id: number;
  content: string;
  progress: string;
  review_time: string;
};

export type EmailCodeRequest = {
  email: string;
};

export type DevEmailCodeOut = {
  message: string;
  dev_code: string;
};

export type PasswordResetConfirm = {
  email: string;
  verification_code: string;
  new_password: string;
};

export type MessageOut = {
  message: string;
};
