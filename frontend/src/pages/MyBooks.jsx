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
    <div className="p-4 max-w-4xl mx-auto">
      <h2 className="text-2xl font-semibold mb-4">My Books</h2>
      {err && <div className="text-red-600">{err}</div>}
      <div className="space-y-3">
        {books.length===0 && <div className="text-sm text-gray-600">No books yet</div>}
        {books.map(b=>(
          <div key={b.id} className="bg-white p-3 rounded shadow flex items-start gap-4">
            {b.image_url ? <img src={b.image_url} className="w-16 h-20 object-cover rounded" alt="cover"/> : <div className="w-16 h-20 bg-gray-100 rounded" />}
            <div className="flex-1">
              <div className="font-medium">{b.title}</div>
              <div className="text-sm text-gray-600">{b.author}</div>
              <div className="text-xs text-gray-500">ISBN: {b.isbn}</div>
            </div>
            <div className="flex flex-col gap-2 text-right">
              <div className="text-sm">Qty: {b.quantity}</div>
              <button onClick={()=>toggle(b)} className="text-sm text-indigo-600">{b.is_public ? "Make Private" : "Make Public"}</button>
              <button onClick={()=>del(b.id)} className="text-sm text-red-600">Delete</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}