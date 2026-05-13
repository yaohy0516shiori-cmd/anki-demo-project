import { apiRequest } from "./client";
import type { NoteOut } from "../types/api";

// create note
// 输入：note类型、note字段、note标签、note提示
// 输出：note信息
export function createNote(input: {
  note_type_id: number;
  fields: string[];
  tags: string[];
  hint: string;
  deck_id: number;
}): Promise<NoteOut> {
  return apiRequest<NoteOut>("/notes", {
    method: "POST", // POST请求，请求体是JSON
    body: JSON.stringify(input), // 把输入转换成JSON字符串
  });
}

// get note list
// 输入：无
// 输出：note列表
export function getNoteList(): Promise<NoteOut[]> {
  return apiRequest<NoteOut[]>("/notes");
}
