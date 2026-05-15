import type { FormEvent } from "react";
import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  createDeck,
  getDeckList,
  deleteDeck,
  updateDeck,
} from "../api/deckApi";
import type { DeckOut } from "../types/api";

export function DeckListPage() {
  const [decks, setDecks] = useState<DeckOut[]>([]);
  const [deckName, setDeckName] = useState("");
  const [deckDescription, setDeckDescription] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [editingDeckId, setEditingDeckId] = useState<number | null>(null);
  const [editDeckName, setEditDeckName] = useState("");
  const [editDeckDescription, setEditDeckDescription] = useState("");
  const [updatingDeckId, setUpdatingDeckId] = useState<number | null>(null);
  const [deletingDeckId, setDeletingDeckId] = useState<number | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadDecksOnMount() {
      try {
        const data = await getDeckList();

        if (!cancelled) {
          setDecks(data);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load decks");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadDecksOnMount();

    return () => {
      cancelled = true;
    };
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

  function handleStartEditDeck(deck: DeckOut) {
    setEditingDeckId(deck.deck_id);
    setEditDeckName(deck.deck_name);
    setEditDeckDescription(deck.deck_description);
    setError(null);
  }

  function handleCancelEditDeck() {
    setEditingDeckId(null);
    setEditDeckName("");
    setEditDeckDescription("");
  }

  async function handleSaveDeck(deckId: number) {
    if (!editDeckName.trim()) {
      setError("Deck name is required");
      return;
    }

    setError(null);
    setUpdatingDeckId(deckId);

    try {
      const updated = await updateDeck(deckId, {
        deck_name: editDeckName.trim(),
        deck_description: editDeckDescription.trim(),
      });

      setDecks((current) =>
        current.map((deck) => (deck.deck_id === deckId ? updated : deck)),
      );

      handleCancelEditDeck();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update deck");
    } finally {
      setUpdatingDeckId(null);
    }
  }

  async function handleDeleteDeck(deck: DeckOut) {
    if (deck.is_default) {
      setError("Default deck cannot be deleted");
      return;
    }

    const confirmed = window.confirm(
      `Delete deck "${deck.deck_name}"? Its cards will be moved to the default deck.`,
    );

    if (!confirmed) {
      return;
    }

    setError(null);
    setDeletingDeckId(deck.deck_id);

    try {
      await deleteDeck(deck.deck_id, false);

      setDecks((current) =>
        current.filter((currentDeck) => currentDeck.deck_id !== deck.deck_id),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete deck");
    } finally {
      setDeletingDeckId(null);
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
            {editingDeckId === deck.deck_id ? (
              <div className="inline-edit">
                <label>
                  Deck name
                  <input
                    value={editDeckName}
                    onChange={(event) => setEditDeckName(event.target.value)}
                  />
                </label>
          
                <label>
                  Description
                  <textarea
                    value={editDeckDescription}
                    onChange={(event) => setEditDeckDescription(event.target.value)}
                    rows={3}
                  />
                </label>
              </div>
            ) : (
              <div>
                <h2>{deck.deck_name}</h2>
                <p className="muted">
                  {deck.deck_description || "No description"}
                  {deck.is_default ? " · default deck" : ""}
                </p>
              </div>
            )}
          
            <div className="row-actions">
              {editingDeckId === deck.deck_id ? (
                <>
                  <button
                    type="button"
                    onClick={() => void handleSaveDeck(deck.deck_id)}
                    disabled={updatingDeckId === deck.deck_id}
                  >
                    {updatingDeckId === deck.deck_id ? "Saving..." : "Save"}
                  </button>
          
                  <button
                    className="button-secondary"
                    type="button"
                    onClick={handleCancelEditDeck}
                  >
                    Cancel
                  </button>
                </>
              ) : (
                <>
                  <Link
                    className="button-secondary"
                    to={`/notes/new?deck_id=${deck.deck_id}`}
                  >
                    Add note
                  </Link>
          
                  <Link
                    className="button-secondary"
                    to={`/decks/${deck.deck_id}/cards`}
                  >
                    View cards
                  </Link>
          
                  <Link
                    className="button-secondary"
                    to={`/study/${deck.deck_id}`}
                  >
                    Study
                  </Link>
          
                  <button
                    className="button-secondary"
                    type="button"
                    onClick={() => handleStartEditDeck(deck)}
                  >
                    Edit
                  </button>
          
                  <button
                    className="danger-button"
                    type="button"
                    disabled={deck.is_default || deletingDeckId === deck.deck_id}
                    onClick={() => void handleDeleteDeck(deck)}
                    title={
                      deck.is_default
                        ? "Default deck cannot be deleted"
                        : "Delete deck"
                    }
                  >
                    {deletingDeckId === deck.deck_id ? "Deleting..." : "Delete"}
                  </button>
                </>
              )}
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
