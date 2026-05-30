import { apiRequest } from "./client";
import type {
  DailyReviewStatsOut,
  DashboardSummaryOut,
  DeckLearningStatsOut,
  DueForecastStatsOut,
  PeriodReviewStatsOut,
} from "../types/api";

export function getDashboardSummary(): Promise<DashboardSummaryOut> {
  return apiRequest<DashboardSummaryOut>("/dashboard/summary");
}

export function getDashboardDeckStats(): Promise<DeckLearningStatsOut[]> {
  return apiRequest<DeckLearningStatsOut[]>("/dashboard/decks");
}

export function getDailyReviewStats(days = 7): Promise<DailyReviewStatsOut[]> {
  return apiRequest<DailyReviewStatsOut[]>(
    `/dashboard/reviews/daily?days=${days}`,
  );
}

export function getDueForecast(days = 7): Promise<DueForecastStatsOut[]> {
  return apiRequest<DueForecastStatsOut[]>(
    `/dashboard/cards/due-forecast?days=${days}`,
  );
}

export function getMonthlyReviewStats(input: {
  year: number;
  month: number;
}): Promise<PeriodReviewStatsOut[]> {
  const params = new URLSearchParams({
    year: String(input.year),
    month: String(input.month),
  });

  return apiRequest<PeriodReviewStatsOut[]>(
    `/dashboard/reviews/monthly?${params.toString()}`,
  );
}

export function getYearlyReviewStats(
  year: number,
): Promise<PeriodReviewStatsOut[]> {
  return apiRequest<PeriodReviewStatsOut[]>(
    `/dashboard/reviews/yearly?year=${year}`,
  );
}
