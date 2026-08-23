from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="BookLender API", version="0.1.0")

from app.db import engine, Base

# ensure models are imported so SQLAlchemy metadata includes them
from app.models import user as user_model  # noqa: F401
from app.models import book as book_model  # noqa: F401
from app.models import borrow as borrow_model  # noqa: F401
from app.models import community as community_model  # noqa: F401

Base.metadata.create_all(bind=engine)

from app.routers import auth as auth_router
from app.routers import books as book_router
from app.routers import users as users_router
from app.routers import borrow_requests as borrow_requests_router
from app.routers import communities as communities_router

app.include_router(auth_router.router)
app.include_router(book_router.router)
app.include_router(users_router.router)
app.include_router(borrow_requests_router.router)
app.include_router(communities_router.router)

# Allow the Vite dev server to call this API during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://community-library-six.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "app": "BookLender"}