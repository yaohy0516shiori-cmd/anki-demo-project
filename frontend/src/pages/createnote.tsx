import type { FormEvent } from "react";
import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { getDeckList } from "../api/deckApi";
import { createNote, listNotes } from "../api/noteApi";
import type { DeckOut, NoteOut } from "../types/api";

const NOTE_TYPES = [
  { id: 1, label: "Basic", fields: ["Front", "Back"] },
  { id: 2, label: "Basic Reverse", fields: ["Front", "Back"] },
  { id: 3, label: "Cloze", fields: ["Text", "Back extra"] },
];

export function CreateNotePage() {
  const [searchParams] = useSearchParams();
  const deckIdFromQuery = searchParams.get("deck_id");

  const [decks, setDecks] = useState<DeckOut[]>([]);
  const [notes, setNotes] = useState<NoteOut[]>([]);
  const [noteTypeId, setNoteTypeId] = useState(1);
  const [front, setFront] = useState("");
  const [back, setBack] = useState("");
  const [hint, setHint] = useState("");
  const [tagsText, setTagsText] = useState("");
  const [deckId, setDeckId] = useState<number | null>(
    deckIdFromQuery ? Number(deckIdFromQuery) : null,
  );
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const selectedNoteType = useMemo(
    () => NOTE_TYPES.find((item) => item.id === noteTypeId) ?? NOTE_TYPES[0],
    [noteTypeId],
  );

  useEffect(() => {
    async function loadInitialData() {
      try {
        const [deckData, noteData] = await Promise.all([
          getDeckList(),
          listNotes(),
        ]);

        setDecks(deckData);
        setNotes(noteData);

        if (!deckId && deckData.length > 0) {
          const defaultDeck =
            deckData.find((item) => item.is_default) ?? deckData[0];
          setDeckId(defaultDeck.deck_id);
        }
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load note page data",
        );
      }
    }

    void loadInitialData();
  }, [deckId]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!deckId) {
      setError("Please select a deck first");
      return;
    }

    if (!front.trim() || !back.trim()) {
      setError("Both fields are required");
      return;
    }

    setError(null);
    setSuccess(null);
    setLoading(true);

    try {
      const tags = tagsText
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean);

      const created = await createNote({
        note_type_id: noteTypeId,
        fields: [front.trim(), back.trim()],
        tags,
        hint: hint.trim(),
        deck_id: deckId,
      });

      setNotes((current) => [created, ...current]);
      setFront("");
      setBack("");
      setHint("");
      setTagsText("");
      setSuccess(
        `Created note #${created.note_id}. Card generation is handled by backend NoteService/CardService.`,
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create note");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-grid">
      <section className="card">
        <h1>Create Note</h1>
        <p className="muted">
          The frontend sends note data only. Backend creates the note and
          automatically generates the related card or cards.
        </p>

        <form className="form" onSubmit={handleSubmit}>
          <label>
            Deck
            <select
              value={deckId ?? ""}
              onChange={(event) => setDeckId(Number(event.target.value))}
              required
            >
              <option value="" disabled>
                Select deck
              </option>

              {decks.map((deck) => (
                <option key={deck.deck_id} value={deck.deck_id}>
                  {deck.deck_name}
                </option>
              ))}
            </select>
          </label>

          <label>
            Note type
            <select
              value={noteTypeId}
              onChange={(event) => setNoteTypeId(Number(event.target.value))}
            >
              {NOTE_TYPES.map((noteType) => (
                <option key={noteType.id} value={noteType.id}>
                  {noteType.label}
                </option>
              ))}
            </select>
          </label>

          <label>
            {selectedNoteType.fields[0]}
            <textarea
              value={front}
              onChange={(event) => setFront(event.target.value)}
              rows={4}
              required
            />
          </label>

          <label>
            {selectedNoteType.fields[1]}
            <textarea
              value={back}
              onChange={(event) => setBack(event.target.value)}
              rows={4}
              required
            />
          </label>

          <label>
            Hint
            <input
              value={hint}
              onChange={(event) => setHint(event.target.value)}
              placeholder="Optional hint"
            />
          </label>

          <label>
            Tags
            <input
              value={tagsText}
              onChange={(event) => setTagsText(event.target.value)}
              placeholder="comma,separated,tags"
            />
          </label>

          {error && <p className="error">{error}</p>}
          {success && <p className="success">{success}</p>}

          <button type="submit" disabled={loading}>
            {loading ? "Creating..." : "Create note"}
          </button>
        </form>
      </section>

      <section className="card">
        <h2>Recent Notes</h2>

        <div className="note-list">
          {notes.slice(0, 8).map((note) => (
            <article className="note-item" key={note.note_id}>
              <strong>#{note.note_id}</strong>
              <span>{note.fields.join(" / ")}</span>
            </article>
          ))}
        </div>

        <Link className="button-secondary" to="/decks">
          Back to decks
        </Link>
      </section>
    </div>
  );
}
