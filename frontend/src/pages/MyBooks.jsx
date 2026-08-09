import { useEffect, useState } from "react";
import api from "../services/api";

export default function MyBooks() {
  const [books, setBooks] = useState([]);
  const [err, setErr] = useState("");

  const load = async () => {
    setErr("");
    try {
      const res = await api.get("/books/me");
      setBooks(res.data);
    } catch (e) {
      setErr("Failed to load books");
    }
  };

  useEffect(()=>{ load(); }, []);

  const del = async (id) => {
    if(!confirm("Delete this book?")) return;
    await api.delete(`/books/${id}`);
    setBooks(b=>b.filter(x=>x.id!==id));
  };

  const toggle = async (book) => {
    await api.put(`/books/${book.id}`, { is_public: !book.is_public });
    load();
  };

  return (
    <div className="w-full min-w-0">
      <h2 className="text-xl sm:text-2xl font-semibold mb-4">My Books</h2>
      {err && <div className="text-red-600">{err}</div>}
      <div className="space-y-3">
        {books.length === 0 && (
          <div className="text-sm text-gray-600">No books yet</div>
        )}
        {books.map((b) => (
          <div
            key={b.id}
            className="bg-gray-50 p-3 rounded flex flex-col gap-3 sm:flex-row sm:items-start"
          >
            <div className="flex gap-3 min-w-0 flex-1">
              {b.image_url ? (
                <img
                  src={b.image_url}
                  className="w-14 h-20 sm:w-16 sm:h-20 object-cover rounded shrink-0"
                  alt="cover"
                />
              ) : (
                <div className="w-14 h-20 bg-gray-100 rounded shrink-0" />
              )}
              <div className="min-w-0 flex-1">
                <div className="font-medium break-words">{b.title}</div>
                <div className="text-sm text-gray-600 break-words">{b.author}</div>
                <div className="text-xs text-gray-500 break-all">ISBN: {b.isbn}</div>
              </div>
            </div>
            <div className="flex flex-row sm:flex-col gap-3 sm:gap-2 sm:text-right shrink-0">
              <button
                onClick={() => toggle(b)}
                className="text-sm text-indigo-600"
              >
                {b.is_public ? "Make Private" : "Make Public"}
              </button>
              <button onClick={() => del(b.id)} className="text-sm text-red-600">
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}