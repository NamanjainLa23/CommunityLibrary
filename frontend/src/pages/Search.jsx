import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import Fuse from "fuse.js";
import { formatIsbn } from "../utils/isbn";

export default function Search() {
  const navigate = useNavigate();
  const [q, setQ] = useState("");
  const [results, setResults] = useState([]);
  const [info, setInfo] = useState("");
  const [loading, setLoading] = useState(false);
  const [requestedBookIds, setRequestedBookIds] = useState(new Set());

  const runSearch = async () => {
    if (!q) return;
    setLoading(true); 
    setInfo(""); 
    setResults([]);
    try {
      const res = await api.get(`/books/search?query=${encodeURIComponent(q)}`);
      let books = [];
      if (res.status === 200 && res.data.length) {
        books = res.data;
      } 
      else {
        // fallback to fetching all public books and fuzzy search client-side
        const pub = await api.get("/books/public");
        const fuse = new Fuse(pub.data, { keys: ["title", "author", "isbn"], threshold: 0.4 });
        books = fuse.search(q).map(x=>x.item);
        if (books.length===0) setInfo("No results");
      }
      setResults(books);
      
      try {
        const mine = await api.get("/borrow_requests/me");
        const ids = new Set(
          (mine.data || [])
            .filter((r) => ["pending", "approved"].includes(r.status))
            .map((r) => String(r.book_id))
        );
        setRequestedBookIds(ids);
      } catch (_) {}

    } catch (e) {
      setInfo("Search failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <h2 className="text-2xl font-semibold mb-4">Search Books / Owners</h2>
      <div className="flex gap-2 mb-4">
        <input value={q} onChange={e=>setQ(e.target.value)} className="flex-1 p-2 border rounded" placeholder="Search by title, author, isbn, username or mobile" />
        <button onClick={runSearch} className="bg-indigo-600 text-white px-4 rounded" disabled={loading}>Search</button>
      </div>
      {info && <div className="text-sm text-gray-600 mb-2">{info}</div>}
      <div className="space-y-3">
        {results.map(b=>(
          <div key={`${b.id}-${b.owner_id}`} className="bg-white p-3 rounded shadow flex gap-3">
            {b.image_url ? <img src={b.image_url} className="w-16 h-20 object-cover rounded" alt="cover"/> : <div className="w-16 h-20 bg-gray-100 rounded" />}
            <div className="flex-1">
              <div className="font-medium">{b.title}</div>
              <div className="text-sm text-gray-600">{b.author}</div>
              <div className="text-xs text-gray-500">ISBN: {formatIsbn(b.isbn)}</div>
            </div>
            <div className="flex flex-col gap-2">
            {requestedBookIds.has(String(b.id)) ? (
              <button disabled className="bg-gray-200 text-gray-600 px-3 py-1 rounded cursor-not-allowed">Borrow requested</button>
            ) : (
              <button
                onClick={async () => {
                  if (!localStorage.getItem("booklender_token")) {
                    navigate("/login");
                    return;
                  }
                  if (!confirm("Request to borrow this book?")) return;
                  try {
                    await api.post("/borrow_requests/", { book_id: b.id, message: "" });
                    alert('Borrow request sent');
                    setRequestedBookIds((prev) => new Set([...prev, String(b.id)]));
                  } catch (e) {
                    alert(e?.response?.data?.detail || "Failed to send request");
                  }
                }}
                className="bg-indigo-600 text-white px-3 py-1 rounded"
              >
                Request Borrow
              </button>
            )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}