import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getDeckCards } from "../api/deckApi";
import type { StudyCardOut } from "../types/api";

export function CardListPage() {
  const { deckId } = useParams();
  const numericDeckId = Number(deckId);

  const [cards, setCards] = useState<StudyCardOut[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadCards() {
      if (!Number.isFinite(numericDeckId)) {
        setError("Invalid deck id");
        setLoading(false);
        return;
      }

      try {
        const data = await getDeckCards(numericDeckId);

        if (!cancelled) {
          setCards(data);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load cards");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadCards();

    return () => {
      cancelled = true;
    };
  }, [numericDeckId]);

  return (
    <section className="card">
      <h1>Cards</h1>
      <p className="muted">
        Cards are generated from notes. Study actions update card scheduling
        data such as status, due, ease, reps, and lapses.
      </p>

      <div className="row-actions">
        <Link className="button-secondary" to="/decks">
          Back to decks
        </Link>

        <Link
          className="button-secondary"
          to={`/notes/new?deck_id=${numericDeckId}`}
        >
          Add note
        </Link>

        <Link className="button-secondary" to={`/study/${numericDeckId}`}>
          Study deck
        </Link>
      </div>

      {loading && <p>Loading cards...</p>}
      {error && <p className="error">{error}</p>}

      <div className="note-list">
        {cards.map((card) => (
          <article className="note-item" key={card.card_id}>
            <strong>Card #{card.card_id}</strong>
            <span>Note #{card.note_id}</span>
            <span>Deck #{card.deck_id}</span>
            <span>Status: {card.status}</span>
            <span>Due: {card.due}</span>
            <span>Interval: {card.interval}</span>
            <span>Ease: {card.ease}</span>
            <span>Reps: {card.reps}</span>
            <span>Lapses: {card.lapses}</span>
            <span>Template ord: {card.template_ord}</span>
          </article>
        ))}
      </div>
    </section>
  );
}
