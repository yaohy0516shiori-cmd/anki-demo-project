import { apiRequest } from "./client";
import type {
  StudySessionStartOut,
  StudyNextOut,
  StudyHintOut,
  StudyBackOut,
  StudyRateOut,
} from "../types/api";

// start study session
// 输入：deck id、学习日期
// 输出：学习 session 开始后的数据
export function startStudySession(input: {
  deck_id: number;
}): Promise<StudySessionStartOut> {
  return apiRequest<StudySessionStartOut>("/study/sessions", {
    method: "POST", //“开始学习 session”不是单纯获取数据，它会在后端创建一个新的学习 session
    body: JSON.stringify(input),
  });
}

// get next card
// 输入：session id
// 输出：下一张卡的数据
export function getNextCard(input: {
  session_id: string;
}): Promise<StudyNextOut> {
  return apiRequest<StudyNextOut>("/study/sessions/${session_id}/next", {
    method: "GET",
    body: JSON.stringify(input),
  });
}

// get hint
// 输入：session id
// 输出：hint
export function getHint(input: { session_id: string }): Promise<StudyHintOut> {
  return apiRequest<StudyHintOut>("/study/sessions/${session_id}/hint", {
    method: "GET",
    body: JSON.stringify(input),
  });
}

// get back
// 输入：session id
// 输出：back
export function getBack(input: { session_id: string }): Promise<StudyBackOut> {
  return apiRequest<StudyBackOut>("/study/sessions/${session_id}/back", {
    // ${session_id} 是变量，需要用反引号括起来
    method: "GET",
    body: JSON.stringify(input),
  });
}

// rate card
// 输入：session id、评分
// 输出：评分后的数据
export function rateCard(input: {
  session_id: string;
  rating: string;
}): Promise<StudyRateOut> {
  return apiRequest<StudyRateOut>("/study/sessions/${session_id}/rate", {
    method: "POST", // POST请求，请求体是JSON
    body: JSON.stringify(input), // 把输入转换成JSON字符串
  });
}
