import { useState } from "react";
import api from "../services/api";
import Fuse from "fuse.js";

export default function Search() {
  const [q, setQ] = useState("");
  const [results, setResults] = useState([]);
  const [info, setInfo] = useState("");
  const [loading, setLoading] = useState(false);

  const runSearch = async () => {
    if (!q) return;
    setLoading(true); setInfo(""); setResults([]);
    try {
      // Preferred: server-side search
      const res = await api.get(`/books/search?query=${encodeURIComponent(q)}`);
      if (res.status === 200 && res.data.length) {
        setResults(res.data);
        setLoading(false);
        return;
      }
      // fallback to fetching all public books and fuzzy search client-side
      const pub = await api.get("/books/public");
      const fuse = new Fuse(pub.data, { keys: ["title", "author", "isbn"], threshold: 0.4 });
      const r = fuse.search(q).map(x=>x.item);
      setResults(r);
      if (r.length===0) setInfo("No results");
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
              <div className="text-xs text-gray-500">ISBN: {b.isbn} — Owner ID: {b.owner_id}</div>
            </div>
            <div className="flex flex-col gap-2">
              <button onClick={async ()=>{
                if(!confirm('Request to borrow this book?')) return;
                try{
                  await api.post('/borrow_requests', { book_id: b.id, message: '' });
                  alert('Borrow request sent');
                }catch(e){
                  alert('Failed to send request');
                }
              }} className="bg-indigo-600 text-white px-3 py-1 rounded">Request Borrow</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}