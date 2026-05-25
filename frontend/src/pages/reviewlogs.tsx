// frontend/src/pages/reviewlogs.tsx

import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { getDeckList } from "../api/deckApi";
import { listReviewLogs } from "../api/reviewApi";
import type { DeckOut, ReviewLogOut } from "../types/api";

const UNKNOWN_DECK_KEY = "unknown";

type ReviewDeckGroup = {
  key: string;
  deckId: number | null;
  deckName: string;
  deckDescription: string;
  logs: ReviewLogOut[];
  total: number;
  good: number;
  again: number;
  hintUsed: number;
  latestReviewTime: string | null;
};

function formatDateTime(value: string | null): string {
  if (!value) return "-";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

function formatDue(value: string | null): string {
  return value || "-";
}

function getDeckKey(deckId: number | null): string {
  return deckId === null ? UNKNOWN_DECK_KEY : String(deckId);
}

function getDeckLabel(
  deckId: number | null,
  deckMap: Map<number, DeckOut>,
): string {
  if (deckId === null) {
    return "Deleted or unknown deck";
  }

  return deckMap.get(deckId)?.deck_name ?? `Deck #${deckId}`;
}

function getDeckDescription(
  deckId: number | null,
  deckMap: Map<number, DeckOut>,
): string {
  if (deckId === null) {
    return "The original deck was deleted, or this log no longer points to a deck.";
  }

  return deckMap.get(deckId)?.deck_description || "No description";
}

function compareReviewTimeDesc(a: ReviewLogOut, b: ReviewLogOut): number {
  return new Date(b.review_time).getTime() - new Date(a.review_time).getTime();
}

export function ReviewLogsPage() {
  const [logs, setLogs] = useState<ReviewLogOut[]>([]);
  const [decks, setDecks] = useState<DeckOut[]>([]);
  const [expandedDeckKeys, setExpandedDeckKeys] = useState<Set<string>>(
    () => new Set(),
  );
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadPageData() {
      setLoading(true);
      setError(null);

      try {
        const [reviewLogs, deckList] = await Promise.all([
          listReviewLogs(),
          getDeckList(),
        ]);

        if (!cancelled) {
          setLogs(reviewLogs);
          setDecks(deckList);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Failed to load review logs",
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadPageData();

    return () => {
      cancelled = true;
    };
  }, []);

  const deckGroups = useMemo<ReviewDeckGroup[]>(() => {
    const deckMap = new Map(decks.map((deck) => [deck.deck_id, deck]));
    const grouped = new Map<string, ReviewLogOut[]>();

    for (const log of logs) {
      const key = getDeckKey(log.deck_id);
      const currentLogs = grouped.get(key) ?? [];
      currentLogs.push(log);
      grouped.set(key, currentLogs);
    }

    return Array.from(grouped.entries())
      .map(([key, groupLogs]) => {
        const sortedLogs = [...groupLogs].sort(compareReviewTimeDesc);
        const firstLog = sortedLogs[0];
        const deckId = firstLog?.deck_id ?? null;

        return {
          key,
          deckId,
          deckName: getDeckLabel(deckId, deckMap),
          deckDescription: getDeckDescription(deckId, deckMap),
          logs: sortedLogs,
          total: sortedLogs.length,
          good: sortedLogs.filter((log) => log.rating === "good").length,
          again: sortedLogs.filter((log) => log.rating === "again").length,
          hintUsed: sortedLogs.filter((log) => log.hint_used).length,
          latestReviewTime: firstLog?.review_time ?? null,
        };
      })
      .sort((a, b) => {
        const timeA = a.latestReviewTime
          ? new Date(a.latestReviewTime).getTime()
          : 0;
        const timeB = b.latestReviewTime
          ? new Date(b.latestReviewTime).getTime()
          : 0;

        return timeB - timeA;
      });
  }, [decks, logs]);

  const summary = useMemo(() => {
    const total = logs.length;
    const good = logs.filter((log) => log.rating === "good").length;
    const again = logs.filter((log) => log.rating === "again").length;
    const reviewedDecks = deckGroups.length;

    return { total, good, again, reviewedDecks };
  }, [deckGroups.length, logs]);

  function toggleDeck(key: string) {
    setExpandedDeckKeys((current) => {
      const next = new Set(current);

      if (next.has(key)) {
        next.delete(key);
      } else {
        next.add(key);
      }

      return next;
    });
  }

  return (
    <section className="card">
      <h1>Review Logs</h1>
      <p className="muted">
        Review logs are read-only history records. This page first shows decks
        that have been reviewed, then you can expand one deck to inspect its
        review records.
      </p>

      <div className="row-actions">
        <Link className="button-secondary" to="/decks">
          Back to decks
        </Link>

        <Link className="button-secondary" to="/notes/new">
          Create note
        </Link>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <strong>{summary.reviewedDecks}</strong>
          <span>Reviewed decks</span>
        </div>

        <div className="stat-card">
          <strong>{summary.total}</strong>
          <span>Total reviews</span>
        </div>

        <div className="stat-card">
          <strong>{summary.good}</strong>
          <span>Good</span>
        </div>

        <div className="stat-card">
          <strong>{summary.again}</strong>
          <span>Again</span>
        </div>
      </div>

      {loading && <p>Loading review logs...</p>}

      {error && <p className="error">{error}</p>}

      {!loading && !error && deckGroups.length === 0 && (
        <p className="muted">
          No reviewed decks yet. Start a study session and rate a card first.
        </p>
      )}

      {!loading && !error && deckGroups.length > 0 && (
        <div className="review-deck-list">
          {deckGroups.map((group) => {
            const expanded = expandedDeckKeys.has(group.key);

            return (
              <article className="review-deck-card" key={group.key}>
                <button
                  type="button"
                  className="review-deck-header"
                  onClick={() => toggleDeck(group.key)}
                  aria-expanded={expanded}
                >
                  <div className="review-deck-main">
                    <h2>{group.deckName}</h2>
                    <p className="muted">{group.deckDescription}</p>
                  </div>

                  <div className="review-deck-meta">
                    <span>{group.total} reviews</span>
                    <span>{group.good} good</span>
                    <span>{group.again} again</span>
                    <span>
                      Latest: {formatDateTime(group.latestReviewTime)}
                    </span>
                    <strong>{expanded ? "Collapse" : "Expand"}</strong>
                  </div>
                </button>

                {expanded && (
                  <div className="review-deck-body">
                    <div className="row-actions">
                      {group.deckId !== null && (
                        <Link
                          className="button-secondary"
                          to={`/decks/${group.deckId}/cards`}
                        >
                          View cards
                        </Link>
                      )}
                    </div>

                    <div className="table-wrapper">
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th>Time</th>
                            <th>Card</th>
                            <th>Note</th>
                            <th>Rating</th>
                            <th>Status</th>
                            <th>Due</th>
                            <th>Interval</th>
                            <th>Ease</th>
                            <th>Hint</th>
                          </tr>
                        </thead>

                        <tbody>
                          {group.logs.map((log) => (
                            <tr key={log.review_log_id}>
                              <td>{formatDateTime(log.review_time)}</td>
                              <td>{log.card_id ?? "-"}</td>
                              <td>{log.note_id ?? "-"}</td>
                              <td>{log.rating}</td>
                              <td>
                                {log.old_status} → {log.new_status}
                              </td>
                              <td>
                                {formatDue(log.old_due)} →{" "}
                                {formatDue(log.new_due)}
                              </td>
                              <td>
                                {log.old_interval} → {log.new_interval}
                              </td>
                              <td>
                                {log.old_ease} → {log.new_ease}
                              </td>
                              <td>{log.hint_used ? "Yes" : "No"}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
