from fastapi import FastAPI
from backend.app.routers import notes, decks, reviews, study

app = FastAPI(title="Memory Anki Demo API")

app.include_router(notes.router, prefix="/notes", tags=["notes"])
app.include_router(decks.router, prefix="/decks", tags=["decks"])
app.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
app.include_router(study.router, prefix="/study", tags=["study"])

@app.get("/health")
def health():
    return {"ok": True}