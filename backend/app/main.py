from fastapi import FastAPI
from backend.app.routers import notes, decks, reviews, study, users, dashboard
from fastapi.middleware.cors import CORSMiddleware
'''
CREATE FASTAPI APP HERE, LOADING ROUTERS HERE
创建 app
配置 CORS
注册 routers
提供 /health
'''
app = FastAPI(title="Memory Anki Demo API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000","http://127.0.0.1:5173",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notes.router, prefix="/notes", tags=["notes"])
app.include_router(decks.router, prefix="/decks", tags=["decks"])
app.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
app.include_router(study.router, prefix="/study", tags=["study"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
@app.get("/health")
def health():
    return {"ok": True}