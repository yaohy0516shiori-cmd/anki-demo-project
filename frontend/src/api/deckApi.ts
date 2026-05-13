import { apiRequest } from "./client";
import type { DeckOut } from "../types/api";

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
