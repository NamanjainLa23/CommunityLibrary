import httpx
from typing import Optional, Dict
import os

GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"
GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")

OPEN_LIBRARY_URL = "https://openlibrary.org/api/books"


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
        industry_ids = info.get("IndustryIdentifiers") or []
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