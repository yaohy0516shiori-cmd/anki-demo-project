import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import {
  getDailyReviewStats,
  getDashboardDeckStats,
  getDashboardSummary,
  getDueForecast,
  getMonthlyReviewStats,
  getYearlyReviewStats,
} from "../api/dashboardApi";
import { SimpleBarChart, SimpleLineChart } from "../components/SimpleCharts";
import type {
  DailyReviewStatsOut,
  DashboardSummaryOut,
  DeckLearningStatsOut,
  DueForecastStatsOut,
  PeriodReviewStatsOut,
} from "../types/api";

type HistoryMode = "month" | "year";

function getCurrentMonthValue(): string {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
}

function formatDateTime(value: string | null): string {
  if (!value) return "-";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

export function DashboardPage() {
  const [summary, setSummary] = useState<DashboardSummaryOut | null>(null);
  const [deckStats, setDeckStats] = useState<DeckLearningStatsOut[]>([]);
  const [weeklyReviews, setWeeklyReviews] = useState<DailyReviewStatsOut[]>([]);
  const [dueForecast, setDueForecast] = useState<DueForecastStatsOut[]>([]);
  const [historyStats, setHistoryStats] = useState<PeriodReviewStatsOut[]>([]);
  const [historyMode, setHistoryMode] = useState<HistoryMode>("month");
  const [selectedMonth, setSelectedMonth] = useState(getCurrentMonthValue);
  const [selectedYear, setSelectedYear] = useState(
    String(new Date().getFullYear()),
  );
  const [loading, setLoading] = useState(true);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [historyError, setHistoryError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadDashboard() {
      setLoading(true);
      setError(null);

      try {
        const [summaryData, deckData, weeklyData, dueData] = await Promise.all([
          getDashboardSummary(),
          getDashboardDeckStats(),
          getDailyReviewStats(7),
          getDueForecast(7),
        ]);

        if (!cancelled) {
          setSummary(summaryData);
          setDeckStats(deckData);
          setWeeklyReviews(weeklyData);
          setDueForecast(dueData);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Failed to load dashboard",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadDashboard();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadHistoryStats() {
      setHistoryLoading(true);
      setHistoryError(null);

      try {
        let data: PeriodReviewStatsOut[];

        if (historyMode === "month") {
          const [yearText, monthText] = selectedMonth.split("-");
          data = await getMonthlyReviewStats({
            year: Number(yearText),
            month: Number(monthText),
          });
        } else {
          data = await getYearlyReviewStats(Number(selectedYear));
        }

        if (!cancelled) {
          setHistoryStats(data);
        }
      } catch (err) {
        if (!cancelled) {
          setHistoryError(
            err instanceof Error ? err.message : "Failed to load history stats",
          );
        }
      } finally {
        if (!cancelled) {
          setHistoryLoading(false);
        }
      }
    }

    void loadHistoryStats();

    return () => {
      cancelled = true;
    };
  }, [historyMode, selectedMonth, selectedYear]);

  const weeklyChartData = useMemo(
    () =>
      weeklyReviews.map((item) => ({
        label: item.date,
        value: item.review_count,
      })),
    [weeklyReviews],
  );

  const dueChartData = useMemo(
    () =>
      dueForecast.map((item) => ({ label: item.date, value: item.due_count })),
    [dueForecast],
  );

  const historyChartData = useMemo(
    () =>
      historyStats.map((item) => ({
        label: item.period,
        value: item.review_count,
      })),
    [historyStats],
  );

  if (loading) {
    return (
      <section className="card">
        <h1>Dashboard</h1>
        <p className="muted">Loading study statistics...</p>
      </section>
    );
  }

  return (
    <div className="dashboard-page">
      <section className="dashboard-hero card">
        <div>
          <h1>Dashboard</h1>
          <p className="muted">
            Review your total content, today&apos;s workload, recent learning
            trend, and longer-term progress after login.
          </p>
        </div>

        <div className="row-actions">
          <Link className="button-secondary" to="/decks">
            Go to decks
          </Link>
          <Link className="button-secondary" to="/notes/new">
            Create note
          </Link>
        </div>
      </section>

      {error && <p className="error">{error}</p>}

      {summary && (
        <section className="metric-grid">
          <article className="metric-card">
            <span>Total decks</span>
            <strong>{summary.total_decks}</strong>
          </article>
          <article className="metric-card">
            <span>Total notes</span>
            <strong>{summary.total_notes}</strong>
          </article>
          <article className="metric-card">
            <span>Total cards</span>
            <strong>{summary.total_cards}</strong>
          </article>
          <article className="metric-card highlight">
            <span>Due today</span>
            <strong>{summary.due_today_cards}</strong>
          </article>
          <article className="metric-card">
            <span>Reviewed today</span>
            <strong>{summary.today_reviews}</strong>
          </article>
          <article className="metric-card">
            <span>Today Good / Again</span>
            <strong>
              {summary.today_good_reviews} / {summary.today_again_reviews}
            </strong>
          </article>
          <article className="metric-card">
            <span>All Good / Again</span>
            <strong>
              {summary.good_reviews} / {summary.again_reviews}
            </strong>
          </article>
          <article className="metric-card">
            <span>Good rate</span>
            <strong>{Math.round(summary.good_rate * 100)}%</strong>
          </article>
        </section>
      )}

      <section className="dashboard-grid">
        <SimpleLineChart
          title="Past 7 days reviewed cards"
          data={weeklyChartData}
        />
        <SimpleBarChart title="Next 7 days due cards" data={dueChartData} />
      </section>

      <section className="card">
        <div className="section-title-row">
          <div>
            <h2>History trend</h2>
            <p className="muted">
              Switch between selected month and selected year.
            </p>
          </div>

          <div className="history-controls">
            <select
              value={historyMode}
              onChange={(event) =>
                setHistoryMode(event.target.value as HistoryMode)
              }
            >
              <option value="month">Month</option>
              <option value="year">Year</option>
            </select>

            {historyMode === "month" ? (
              <input
                type="month"
                value={selectedMonth}
                onChange={(event) => setSelectedMonth(event.target.value)}
              />
            ) : (
              <input
                type="number"
                min="1970"
                max="3000"
                value={selectedYear}
                onChange={(event) => setSelectedYear(event.target.value)}
              />
            )}
          </div>
        </div>

        {historyLoading && <p className="muted">Loading history stats...</p>}
        {historyError && <p className="error">{historyError}</p>}
        {!historyLoading && !historyError && (
          <SimpleLineChart
            title="Review count by period"
            data={historyChartData}
          />
        )}
      </section>

      <section className="card">
        <div className="section-title-row">
          <div>
            <h2>Deck learning status</h2>
            <p className="muted">
              Per-deck card count, due count, and rating result. Latest review:{" "}
              {formatDateTime(summary?.latest_review_time ?? null)}
            </p>
          </div>
        </div>

        {deckStats.length === 0 ? (
          <p className="muted">No deck data yet.</p>
        ) : (
          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Deck</th>
                  <th>Cards</th>
                  <th>Due today</th>
                  <th>New</th>
                  <th>Learning</th>
                  <th>Review</th>
                  <th>Relearning</th>
                  <th>Good</th>
                  <th>Again</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {deckStats.map((deck) => (
                  <tr key={deck.deck_id}>
                    <td>{deck.deck_name}</td>
                    <td>{deck.card_count}</td>
                    <td>{deck.due_today_count}</td>
                    <td>{deck.new_count}</td>
                    <td>{deck.learning_count}</td>
                    <td>{deck.review_count}</td>
                    <td>{deck.relearning_count}</td>
                    <td>{deck.good_count}</td>
                    <td>{deck.again_count}</td>
                    <td>
                      <Link
                        className="table-link"
                        to={`/study/${deck.deck_id}`}
                      >
                        Study
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </div>
  );
}
