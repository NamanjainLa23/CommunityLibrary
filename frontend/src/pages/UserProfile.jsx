import { useEffect, useState } from "react";
import api from "../services/api";
import { useParams } from "react-router-dom";

export default function UserProfile() {
  const { usernameOrId } = useParams();
  const [books, setBooks] = useState([]);
  const [profile, setProfile] = useState(null);
  const [err, setErr] = useState("");

  // Try to fetch user by username endpoint if exists; else we fetch public books by owner_id if numeric
  useEffect(()=> {
    const load = async () => {
      try {
        // Try server endpoint: /users/{usernameOrId}/books (implement later)
        // Fallback: if numeric treat as owner_id call /books/public?owner_id=...
        if(/^\d+$/.test(usernameOrId)) {
          const res = await api.get(`/books/public?owner_id=${usernameOrId}`);
          setBooks(res.data);
        } else {
          // If backend exposes /users/{username}/public-books, call it; else fallback to search users endpoint (not yet implemented)
          const res = await api.get(`/books/public?owner_username=${usernameOrId}`);
          setBooks(res.data);
        }
      } catch (e) {
        setErr("Failed to load user's public books");
      }
    };
    load();
  }, [usernameOrId]);

  return (
    <div className="p-4 max-w-4xl mx-auto">
      <h2 className="text-2xl font-semibold mb-4">User: {usernameOrId}</h2>
      {err && <div className="text-red-600">{err}</div>}
      <div className="grid sm:grid-cols-2 gap-4">
        {books.map(b=>(
          <div key={b.id} className="bg-white p-3 rounded shadow flex gap-3">
            {b.image_url ? <img src={b.image_url} className="w-16 h-20 object-cover rounded" alt="cover"/> : <div className="w-16 h-20 bg-gray-100 rounded" />}
            <div>
              <div className="font-medium">{b.title}</div>
              <div className="text-sm text-gray-600">{b.author}</div>
              <div className="text-xs text-gray-500">Qty: {b.quantity}</div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}