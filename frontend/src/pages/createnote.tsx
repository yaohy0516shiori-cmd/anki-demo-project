import type { FormEvent } from "react";
import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { getDeckList } from "../api/deckApi";
import { createNote, listNotes, deleteNote, updateNote } from "../api/noteApi";
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
  const [editingNoteId, setEditingNoteId] = useState<number | null>(null);
  const [editFront, setEditFront] = useState("");
  const [editBack, setEditBack] = useState("");
  const [editHint, setEditHint] = useState("");
  const [editTagsText, setEditTagsText] = useState("");
  const [updatingNoteId, setUpdatingNoteId] = useState<number | null>(null);
  const [deletingNoteId, setDeletingNoteId] = useState<number | null>(null);
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
  function handleStartEditNote(note: NoteOut) {
    setEditingNoteId(note.note_id);
    setEditFront(note.fields[0] ?? "");
    setEditBack(note.fields[1] ?? "");
    setEditHint(note.hint);
    setEditTagsText(note.tags.join(", "));
    setError(null);
    setSuccess(null);
  }

  function handleCancelEditNote() {
    setEditingNoteId(null);
    setEditFront("");
    setEditBack("");
    setEditHint("");
    setEditTagsText("");
  }

  async function handleSaveNote(noteId: number) {
    if (!editFront.trim() || !editBack.trim()) {
      setError("Both fields are required");
      return;
    }

    setError(null);
    setSuccess(null);
    setUpdatingNoteId(noteId);

    try {
      const tags = editTagsText
        .split(",")
        .map((tag) => tag.trim())
        .filter(Boolean);

      const updated = await updateNote(noteId, {
        fields: [editFront.trim(), editBack.trim()],
        tags,
        hint: editHint.trim(),
      });

      setNotes((current) =>
        current.map((note) => (note.note_id === noteId ? updated : note)),
      );

      handleCancelEditNote();
      setSuccess(
        `Updated note #${noteId}. Related cards were reconciled by backend.`,
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update note");
    } finally {
      setUpdatingNoteId(null);
    }
  }

  async function handleDeleteNote(note: NoteOut) {
    const confirmed = window.confirm(
      `Delete note #${note.note_id}? Its generated cards will also be deleted.`,
    );

    if (!confirmed) {
      return;
    }

    setError(null);
    setSuccess(null);
    setDeletingNoteId(note.note_id);

    try {
      await deleteNote(note.note_id);

      setNotes((current) =>
        current.filter((currentNote) => currentNote.note_id !== note.note_id),
      );

      setSuccess(`Deleted note #${note.note_id} and its related cards.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to delete note");
    } finally {
      setDeletingNoteId(null);
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
              {editingNoteId === note.note_id ? (
                <div className="inline-edit">
                  <strong>Editing note #{note.note_id}</strong>

                  <label>
                    Front
                    <textarea
                      value={editFront}
                      onChange={(event) => setEditFront(event.target.value)}
                      rows={3}
                    />
                  </label>

                  <label>
                    Back
                    <textarea
                      value={editBack}
                      onChange={(event) => setEditBack(event.target.value)}
                      rows={3}
                    />
                  </label>

                  <label>
                    Hint
                    <input
                      value={editHint}
                      onChange={(event) => setEditHint(event.target.value)}
                    />
                  </label>

                  <label>
                    Tags
                    <input
                      value={editTagsText}
                      onChange={(event) => setEditTagsText(event.target.value)}
                    />
                  </label>

                  <div className="row-actions">
                    <button
                      type="button"
                      onClick={() => void handleSaveNote(note.note_id)}
                      disabled={updatingNoteId === note.note_id}
                    >
                      {updatingNoteId === note.note_id ? "Saving..." : "Save"}
                    </button>

                    <button
                      className="button-secondary"
                      type="button"
                      onClick={handleCancelEditNote}
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <strong>#{note.note_id}</strong>
                  <span>{note.fields.join(" / ")}</span>

                  <div className="row-actions">
                    <button
                      className="button-secondary"
                      type="button"
                      onClick={() => handleStartEditNote(note)}
                    >
                      Edit
                    </button>

                    <button
                      className="danger-button"
                      type="button"
                      disabled={deletingNoteId === note.note_id}
                      onClick={() => void handleDeleteNote(note)}
                    >
                      {deletingNoteId === note.note_id
                        ? "Deleting..."
                        : "Delete"}
                    </button>
                  </div>
                </>
              )}
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
