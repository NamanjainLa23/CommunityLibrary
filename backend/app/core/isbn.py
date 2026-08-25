import httpx
from typing import Optional, Dict
import os
import re

GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

OPEN_LIBRARY_URL = "https://openlibrary.org/api/books"

def normalise_isbn(isbn: str | None) -> str:
    if not isbn:
        return ""
    return re.sub(r"[^0-9Xx]", "", str(isbn)).upper()


def isbn10_to_isbn13(isbn10: str | None) -> str | None:
    if len(isbn10) != 10:
        return None
    
    core = "978" + isbn10[:9]
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(core))
    check = (10 - (total % 10)) % 10
    return core + str(check)


def fetch_book_by_isbn(isbn: str) -> Optional[Dict]:
    params = {"q": f"isbn:{isbn}"}
    if GOOGLE_BOOKS_API_KEY:
        params["key"] = GOOGLE_BOOKS_API_KEY
    try:
        resp = httpx.get(GOOGLE_BOOKS_URL, params=params, timeout=10)
        if resp.status_code == 429:
            raise RuntimeError("Google Books API quoto exceeded")

        resp.raise_for_status()
        data = resp.json()
        items = data.get("items") or []
        if not items:
            return None

        info = items[0].get("volumeInfo", {})
        title = info.get("title")
        authors = info.get("authors") or []
        industry_ids = info.get("industryIdentifiers") or []
        found_isbn = isbn

        for ident in industry_ids:
            if ident.get("type") in ("ISBN_13", "ISBN_10"):
                found_isbn = ident.get("identifier")
                break

        image_links = info.get("imageLinks") or {}
        image_url = image_links.get("thumbnail") or image_links.get("smallThumbnail")

        return {
            "title": title,
            "author": ", ".join(authors) if authors else None,
            "isbn": found_isbn,
            "published_date": info.get("publishedDate"),
            "description": info.get("description"),
            "image_url": image_url
        }
    except httpx.HTTPStatusError:
        return None

#ToDo: add this as fallback
def fetch_book_by_isbn_openlibrary(isbn: str) -> Optional[Dict]:
    try:
        resp = httpx.get(
            OPEN_LIBRARY_URL,
            params={
                "bibkeys": f"ISBN:{isbn}",
                "format": "json",
                "jscmd": "data",
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        book = data.get(f"ISBN:{isbn}")
        if not book:
            return None
        authors = book.get("authors") or []
        cover = book.get("cover") or {}
        return {
            "title": book.get("title"),
            "author": ", ".join(a["name"] for a in authors) if authors else None,
            "isbn": isbn,
            "published_date": book.get("publish_date"),
            "description": book.get("notes") or book.get("subtitle"),
            "image_url": cover.get("large") or cover.get("medium") or cover.get("small"),
        }
    except Exception:
        return None