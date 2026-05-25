// frontend/src/pages/reviewlogs.tsx

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getDeckList } from "../api/deckApi";
import { listLatestNoteReviewsByDeck } from "../api/reviewApi";
import type { DeckOut, LatestNoteReviewOut } from "../types/api";

function formatDateTime(value: string | null): string {
  if (!value) return "-";

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

export function ReviewLogsPage() {
  const [decks, setDecks] = useState<DeckOut[]>([]);
  const [expandedDeckIds, setExpandedDeckIds] = useState<Set<number>>(
    () => new Set(),
  );
  const [noteReviewsByDeckId, setNoteReviewsByDeckId] = useState<
    Record<number, LatestNoteReviewOut[]>
  >({});
  const [loadingDecks, setLoadingDecks] = useState(true);
  const [loadingDeckId, setLoadingDeckId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadDecks() {
      setLoadingDecks(true);
      setError(null);

      try {
        const data = await getDeckList();

        if (!cancelled) {
          setDecks(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load decks");
        }
      } finally {
        if (!cancelled) {
          setLoadingDecks(false);
        }
      }
    }

    void loadDecks();

    return () => {
      cancelled = true;
    };
  }, []);

  async function toggleDeck(deckId: number) {
    const alreadyExpanded = expandedDeckIds.has(deckId);

    setExpandedDeckIds((current) => {
      const next = new Set(current);

      if (alreadyExpanded) {
        next.delete(deckId);
      } else {
        next.add(deckId);
      }

      return next;
    });

    if (alreadyExpanded) {
      return;
    }

    setLoadingDeckId(deckId);
    setError(null);

    try {
      const reviews = await listLatestNoteReviewsByDeck(deckId);

      setNoteReviewsByDeckId((current) => ({
        ...current,
        [deckId]: reviews,
      }));
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load note reviews",
      );
    } finally {
      setLoadingDeckId(null);
    }
  }

  return (
    <section className="card">
      <h1>Review Logs</h1>
      <p className="muted">
        All decks are shown here. Expand a deck to view the latest review status
        for each note in that deck.
      </p>

      <div className="row-actions">
        <Link className="button-secondary" to="/decks">
          Back to decks
        </Link>

        <Link className="button-secondary" to="/notes/new">
          Create note
        </Link>
      </div>

      {loadingDecks && <p>Loading decks...</p>}

      {error && <p className="error">{error}</p>}

      {!loadingDecks && !error && decks.length === 0 && (
        <p className="muted">No decks yet. Create a deck or note first.</p>
      )}

      {!loadingDecks && decks.length > 0 && (
        <div className="review-deck-list">
          {decks.map((deck) => {
            const expanded = expandedDeckIds.has(deck.deck_id);
            const noteReviews = noteReviewsByDeckId[deck.deck_id] ?? [];
            const isLoadingThisDeck = loadingDeckId === deck.deck_id;

            return (
              <article className="review-deck-card" key={deck.deck_id}>
                <button
                  type="button"
                  className="review-deck-header"
                  onClick={() => void toggleDeck(deck.deck_id)}
                  aria-expanded={expanded}
                >
                  <div className="review-deck-main">
                    <h2>{deck.deck_name}</h2>
                    <p className="muted">
                      {deck.deck_description || "No description"}
                    </p>
                  </div>

                  <div className="review-deck-meta">
                    <span>Updated: {formatDateTime(deck.updated_at)}</span>
                    <strong>{expanded ? "Collapse" : "Expand"}</strong>
                  </div>
                </button>

                {expanded && (
                  <div className="review-deck-body">
                    <div className="row-actions">
                      <Link
                        className="button-secondary"
                        to={`/decks/${deck.deck_id}/cards`}
                      >
                        View cards
                      </Link>
                    </div>

                    {isLoadingThisDeck && <p>Loading notes...</p>}

                    {!isLoadingThisDeck && noteReviews.length === 0 && (
                      <p className="muted">
                        No review records for this deck yet.
                      </p>
                    )}

                    {!isLoadingThisDeck && noteReviews.length > 0 && (
                      <div className="table-wrapper">
                        <table className="data-table">
                          <thead>
                            <tr>
                              <th>Content</th>
                              <th>Progress</th>
                              <th>Review time</th>
                            </tr>
                          </thead>

                          <tbody>
                            {noteReviews.map((review) => (
                              <tr key={review.note_id}>
                                <td>{review.content}</td>
                                <td>{review.progress}</td>
                                <td>{formatDateTime(review.review_time)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
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
