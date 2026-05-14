import type { FormEvent } from "react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { createDeck, getDeckList } from "../api/deckApi";
import type { DeckOut } from "../types/api";

export function DeckListPage() {
  const [decks, setDecks] = useState<DeckOut[]>([]);
  const [deckName, setDeckName] = useState("");
  const [deckDescription, setDeckDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  async function loadDecks() {
    setError(null);
    setLoading(true);

    try {
      const data = await getDeckList();
      setDecks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load decks");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    void loadDecks();
  }, []);

  async function handleCreateDeck(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!deckName.trim()) {
      setError("Deck name is required");
      return;
    }

    setError(null);
    setCreating(true);

    try {
      const created = await createDeck({
        deck_name: deckName.trim(),
        deck_description: deckDescription.trim(),
      });

      setDecks((current) => [...current, created]);
      setDeckName("");
      setDeckDescription("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create deck");
    } finally {
      setCreating(false);
    }
  }

  return (
    <div className="page-grid">
      <section className="card">
        <h1>Decks</h1>
        <p className="muted">
          Deck is the entry point for study. A note belongs to a deck, and the
          generated cards inherit that deck.
        </p>

        {loading && <p>Loading decks...</p>}
        {error && <p className="error">{error}</p>}

        <div className="deck-list">
          {decks.map((deck) => (
            <article className="deck-item" key={deck.deck_id}>
              <div>
                <h2>{deck.deck_name}</h2>
                <p className="muted">
                  {deck.deck_description || "No description"}
                  {deck.is_default ? " · default deck" : ""}
                </p>
              </div>

              <div className="row-actions">
                <Link
                  className="button-secondary"
                  to={`/notes/new?deck_id=${deck.deck_id}`}
                >
                  Add note
                </Link>
                <Link
                  className="button-secondary"
                  to={`/study/${deck.deck_id}`}
                >
                  Study
                </Link>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="card">
        <h2>Create Deck</h2>

        <form className="form" onSubmit={handleCreateDeck}>
          <label>
            Deck name
            <input
              value={deckName}
              onChange={(event) => setDeckName(event.target.value)}
              placeholder="English Vocabulary"
              required
            />
          </label>

          <label>
            Description
            <textarea
              value={deckDescription}
              onChange={(event) => setDeckDescription(event.target.value)}
              placeholder="Optional description"
              rows={4}
            />
          </label>

          <button type="submit" disabled={creating}>
            {creating ? "Creating..." : "Create deck"}
          </button>
        </form>
      </section>
    </div>
  );
}
