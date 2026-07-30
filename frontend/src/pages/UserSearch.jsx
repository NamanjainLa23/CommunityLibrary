import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function UserSearch() {
  const [q, setQ] = useState("");
  const navigate = useNavigate();

  const go = (e) => {
    e.preventDefault();
    if(!q) return;
    // Navigate to user profile route which will load public books
    navigate(`/user/${encodeURIComponent(q)}`);
  };

  return (
    <div>
      <h3 className="text-lg font-medium mb-3">Search User</h3>
      <form onSubmit={go} className="flex gap-2 mb-4">
        <input className="flex-1 p-2 border rounded" placeholder="Enter username or numeric id" value={q} onChange={e=>setQ(e.target.value)} />
        <button className="bg-indigo-600 text-white px-4 rounded">Go</button>
      </form>
      <p className="text-sm text-gray-600">Enter a username (e.g. user1) or numeric user id to view their public books.</p>
    </div>
  );
}
