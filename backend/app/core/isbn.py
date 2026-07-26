import httpx
from typing import Optional, Dict

GOOGLE_BOOKSISBN_URL = "https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"

def fetch_book_by_isbn(isbn: str) -> Optional[Dict]:
    try:
        url = GOOGLE_BOOKSISBN_URL.format(isbn=isbn)
        resp = httpx.get(url, timeout=10)
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
    except Exception:
        return None