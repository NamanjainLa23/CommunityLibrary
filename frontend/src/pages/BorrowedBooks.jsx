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
            <div className="flex gap-3 min-w-0 flex-1">
              {it.image_url ? (
                <img
                  src={it.image_url}
                  className="w-14 h-20 sm:w-16 sm:h-20 object-cover rounded shrink-0"
                  alt="cover"
                />
              ) : (
                <div className="w-14 h-20 bg-gray-100 rounded shrink-0" />
              )}
            </div>
            <div className="font-medium">{it.title}</div>
            <div className="text-sm text-gray-600">Borrowed from: {it.owner_username || it.owner_id}</div>
            <div className="text-xs text-gray-500">Due: {it.due_date || '—'}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
