// frontend/src/api/reviewApi.ts

import { apiRequest } from "./client";
import type {
  ReviewLogOut,
  ReviewedDeckOut,
  LatestNoteReviewOut,
} from "../types/api";

// 获取当前登录用户的所有 review logs
export function listReviewLogs(): Promise<ReviewLogOut[]> {
  return apiRequest<ReviewLogOut[]>("/reviews", {
    method: "GET",
  });
}

// 可选：获取某一张 card 的 review logs
// 当前 ReviewLogsPage 不一定需要用，但可以先保留给以后 card detail 页面用
export function getReviewLogsByCard(cardId: number): Promise<ReviewLogOut[]> {
  return apiRequest<ReviewLogOut[]>(`/reviews/cards/${cardId}`, {
    method: "GET",
  });
}

export function listReviewedDecks(): Promise<ReviewedDeckOut[]> {
  return apiRequest<ReviewedDeckOut[]>("/reviews/decks", {
    method: "GET",
  });
}

export function listLatestNoteReviewsByDeck(
  deckId: number,
): Promise<LatestNoteReviewOut[]> {
  return apiRequest<LatestNoteReviewOut[]>(
    `/reviews/decks/${deckId}/notes/latest`,
    { method: "GET" },
  );
}
