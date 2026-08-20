import { useEffect, useState } from "react";
import api from "../services/api";

export default function LentBooks(){
  const [items, setItems] = useState([]);
  const [err, setErr] = useState("");

  const load = async ()=>{
    setErr("");
    try{
      // show currently approved lends (items currently out)
      const res = await api.get("/borrow_requests/lent");
      setItems(res.data || []);
    }catch(e){
      setErr('Failed to load lent items');
    }
  };

  useEffect(()=>{ load(); }, []);

  const markCompleted = async (id)=>{
    if(!confirm('Mark as completed?')) return;
    try{
      await api.patch(`/borrow_requests/${id}/status`, { status: 'completed' });
      load();
    }catch(e){ alert('Failed to update'); }
  };

  const markReturned = async (id) => {
    if(!confirm('Confirm you have received the book back?')) return;
    try{
      await api.patch(`/borrow_requests/${id}/status`, { status: 'returned' });
      load();
    }catch(e){ alert('Failed to update'); }
  };

  const lent = items.filter((r) => r.status === "completed");
  const returned = items.filter((r) => r.status === "returned");

  const card = (r, extraClass = "bg-white") => (
    <div key={r.id} className={`p-3 rounded shadow flex gap-3 items-start ${extraClass}`}>
      {r.book_image_url ? (
        <img src={r.book_image_url} className="w-14 h-20 object-cover rounded shrink-0" alt="" />
      ) : (
        <div className="w-14 h-20 bg-gray-100 rounded shrink-0" />
      )}
      <div className="flex-1 min-w-0">
        <div className="font-medium">{r.book_title || "book"}</div>
        <div className="text-sm text-gray-600">Borrowed by: {r.requester_username || r.requester_id}</div>
        <div className="text-xs text-gray-500">Status: {r.status}</div>
      </div>
      {r.status === "completed" && (
        <button
          onClick={() => markReturned(r.id)}
          className="bg-green-600 text-white px-3 py-1 rounded shrink-0"
        >
          Returned
        </button>
      )}
    </div>
  );

  return (
    <div className="space-y-8">
      {err && <div className="text-sm text-red-600">{err}</div>}
      <section>
        <h3 className="text-lg font-medium mb-3">Books Currently Lent</h3>
        <div className="space-y-3">
          {lent.length === 0 && (
            <div className="text-sm text-gray-600">No books currently lent out.</div>
          )}
          {lent.map((r) => card(r))}
        </div>
      </section>
      <section>
        <h3 className="text-lg font-medium mb-3">Books Receieved back</h3>
        <div className="space-y-3">
          {returned.length === 0 && (
            <div className="text-sm text-gray-600">No returned books yet.</div>
          )}
          {returned.map((r) => card(r, "bg-green-50 border border-green-200"))}
        </div>
      </section>
    </div>
  );
}
