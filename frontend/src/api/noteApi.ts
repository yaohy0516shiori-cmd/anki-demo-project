import { apiRequest } from "./client";
import type { DeleteResultOut, NoteOut } from "../types/api";

// create note
// 输入：note类型、note字段、note标签、note提示
// 输出：note信息
export function createNote(input: {
  note_type_id: number;
  fields: string[];
  tags: string[];
  hint: string;
  deck_id: number | null;
}): Promise<NoteOut> {
  return apiRequest<NoteOut>("/notes", {
    method: "POST", // POST请求，请求体是JSON
    body: JSON.stringify(input), // 把输入转换成JSON字符串
  });
}

// get note list
// 输入：无
// 输出：note列表
export function listNotes(): Promise<NoteOut[]> {
  return apiRequest<NoteOut[]>("/notes");
}

export function getNote(note_id: number): Promise<NoteOut> {
  return apiRequest<NoteOut>(`/notes/${note_id}`);
}

export function updateNote(
  note_id: number,
  data: { fields: string[]; tags: string[]; hint: string },
): Promise<NoteOut> {
  return apiRequest<NoteOut>(`/notes/${note_id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export function deleteNote(note_id: number): Promise<DeleteResultOut> {
  return apiRequest<DeleteResultOut>(`/notes/${note_id}`, {
    method: "DELETE",
  });
}
