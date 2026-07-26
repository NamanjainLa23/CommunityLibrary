from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="BookLender API", version="0.1.0")

from app.db import engine, Base
from app.models import user, book  # import models so SQLAlchemy registers them

Base.metadata.create_all(bind=engine)

from app.routers import auth as auth_router
from app.routers import books as book_router

app.include_router(auth_router.router)
app.include_router(book_router.router)


# Allow the Vite dev server to call this API during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "BookLender"}