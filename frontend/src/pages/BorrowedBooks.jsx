import { useEffect, useState } from "react";
import api from "../services/api";

export default function BorrowedBooks() {
  const [items, setItems] = useState([]);
  const [err, setErr] = useState("");

  useEffect(()=>{
    const load = async ()=>{
      setErr("");
      try {
        // Backend endpoint may not exist yet; try /books/borrowed
        const res = await api.get('/books/borrowed');
        setItems(res.data || []);
      } catch (e) {
        setErr('No borrowed-items endpoint available or failed to load.');
      }
    };
    load();
  },[]);

  return (
    <div>
      <h3 className="text-lg font-medium mb-3">Borrowed Items</h3>
      {err && <div className="text-sm text-gray-600 mb-2">{err}</div>}
      <div className="space-y-3">
        {items.length===0 && <div className="text-sm text-gray-600">No borrowed items to show.</div>}
        {items.map(it => (
          <div key={it.id} className="bg-gray-50 p-3 rounded">
            <div className="font-medium">{it.title}</div>
            <div className="text-sm text-gray-600">Borrowed from: {it.owner_username || it.owner_id}</div>
            <div className="text-xs text-gray-500">Due: {it.due_date || '—'}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
