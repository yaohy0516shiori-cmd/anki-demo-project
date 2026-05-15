import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  getNextCard,
  rateCard,
  revealBack,
  revealHint,
  startStudySession,
} from "../api/studyApi";
import type {
  StudyBackOut,
  StudyHintOut,
  StudyNextOut,
  StudyRating,
  StudySessionStartOut,
} from "../types/api";

export function StudyPage() {
  const { deckId } = useParams();
  const numericDeckId = Number(deckId);

  const [session, setSession] = useState<StudySessionStartOut | null>(null);
  const [current, setCurrent] = useState<StudyNextOut | null>(null);
  const [hint, setHint] = useState<StudyHintOut | null>(null);
  const [back, setBack] = useState<StudyBackOut | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    async function start() {
      if (!Number.isFinite(numericDeckId)) {
        setError("Invalid deck id");
        setLoading(false);
        return;
      }

      setError(null);
      setLoading(true);

      try {
        const createdSession = await startStudySession({
          deck_id: numericDeckId,
          today: null,
        });

        setSession(createdSession);

        const next = await getNextCard(createdSession.session_id);
        setCurrent(next);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to start study session",
        );
      } finally {
        setLoading(false);
      }
    }

    void start();
  }, [numericDeckId]);

  async function handleRevealHint() {
    if (!session) return;

    setError(null);
    setActionLoading(true);

    try {
      const data = await revealHint(session.session_id);
      setHint(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to get hint");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleRevealBack() {
    if (!session) return;

    setError(null);
    setActionLoading(true);

    try {
      const data = await revealBack(session.session_id);
      setBack(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to get back");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleRate(rating: StudyRating) {
    if (!session) return;

    setError(null);
    setActionLoading(true);

    try {
      await rateCard(session.session_id, rating);

      setHint(null);
      setBack(null);

      const next = await getNextCard(session.session_id);
      setCurrent(next);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to rate card");
    } finally {
      setActionLoading(false);
    }
  }

  if (loading) {
    return <section className="card">Starting study session...</section>;
  }

  if (error && !current) {
    return (
      <section className="card">
        <p className="error">{error}</p>
        <Link className="button-secondary" to="/decks">
          Back to decks
        </Link>
      </section>
    );
  }

  if (current?.finished) {
    return (
      <section className="card study-card">
        <h1>Study Finished</h1>
        <p className="muted">No more due cards in this session.</p>
        <Link className="button-secondary" to="/decks">
          Back to decks
        </Link>
      </section>
    );
  }

  return (
    <section className="card study-card">
      <div className="study-meta">
        <span>Deck #{session?.deck_id}</span>
        <span>New {session?.new_queue ?? 0}</span>
        <span>Learning {session?.learning_queue ?? 0}</span>
        <span>Review {session?.review_queue ?? 0}</span>
      </div>

      <h1>Study</h1>

      <div className="flashcard">
        <p className="muted">Front</p>
        <h2>{current?.front ?? "No front content"}</h2>
      </div>

      {hint && (
        <div className="info-box">
          <strong>Hint:</strong> {hint.hint}
        </div>
      )}

      {back && (
        <div className="info-box">
          <strong>Back:</strong> {back.back}
        </div>
      )}

      {error && <p className="error">{error}</p>}

      <div className="row-actions center-actions">
        <button
          type="button"
          className="button-secondary"
          onClick={handleRevealHint}
          disabled={actionLoading || !current?.hint_available || Boolean(hint)}
        >
          Reveal hint
        </button>

        <button
          type="button"
          className="button-secondary"
          onClick={handleRevealBack}
          disabled={actionLoading || Boolean(back)}
        >
          Reveal back
        </button>
      </div>

      <div className="row-actions center-actions">
        <button
          type="button"
          className="danger-button"
          onClick={() => void handleRate("again")}
          disabled={actionLoading || !back}
        >
          Again
        </button>

        <button
          type="button"
          onClick={() => void handleRate("good")}
          disabled={actionLoading || !back}
        >
          Good
        </button>
      </div>
    </section>
  );
}
