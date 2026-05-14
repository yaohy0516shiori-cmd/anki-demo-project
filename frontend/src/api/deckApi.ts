import { apiRequest } from "./client";
import type { DeckOut, StudyCardOut } from "../types/api";

// get deck list
// 输入：无
// 输出：deck列表
export function getDeckList(): Promise<DeckOut[]> {
  return apiRequest<DeckOut[]>("/decks");
}

// create deck
// 输入：deck名称、deck描述
// 输出：deck信息
export function createDeck(input: {
  deck_name: string;
  deck_description: string;
}): Promise<DeckOut> {
  return apiRequest<DeckOut>("/decks", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function updateDeck(
  deck_id: number,
  data: { deck_name: string; deck_description: string },
): Promise<DeckOut> {
  return apiRequest<DeckOut>(`/decks/${deck_id}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export function deleteDeck(
  deck_id: number,
  hard: boolean = false,
): Promise<void> {
  return apiRequest(`/decks/${deck_id}?hard=${hard}`, {
    method: "DELETE",
  });
}

export function getDeckCards(deck_id: number): Promise<StudyCardOut[]> {
  return apiRequest<StudyCardOut[]>(`/decks/${deck_id}/cards`);
}
