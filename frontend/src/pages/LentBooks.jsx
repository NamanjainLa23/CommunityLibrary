import { useEffect, useState } from "react";
import api from "../services/api";

export default function LentBooks(){
  const [items, setItems] = useState([]);
  const [err, setErr] = useState("");

  const load = async ()=>{
    setErr("");
    try{
      // show currently approved lends (items currently out)
      const res = await api.get("/borrow_requests/lent?status=completed");
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

  const markReceived = async (id) => {
    if(!confirm('Confirm you have received the book back?')) return;
    try{
      await api.patch(`/borrow_requests/${id}/status`, { status: 'received' });
      load();
    }catch(e){ alert('Failed to update'); }
  };

  return (
    <div>
      <h3 className="text-lg font-medium mb-3">Lent Books</h3>
      {err && <div className="text-sm text-red-600 mb-2">{err}</div>}
      <div className="space-y-3">
        {items.length===0 && <div className="text-sm text-gray-600">No lent items.</div>}
        {items.map(r=> (
          <div key={r.id} className="bg-white p-3 rounded shadow flex gap-3 items-start">
            <div className="flex-1">
            {r.book_image_url ? (
                <img
                  src={r.book_image_url}
                  className="w-14 h-20 sm:w-16 sm:h-20 object-cover rounded shrink-0"
                  alt="cover"
                />
              ) : (
                <div className="w-14 h-20 bg-gray-100 rounded shrink-0" />
              )}
              <div className="font-medium">{r.book_title || 'book'}</div>
              <div className="text-sm text-gray-600">Borrowed by: {r.requester_username || r.requester_id}</div>
              <div className="text-xs text-gray-500">Status: {r.status}</div>
            </div>
            <div className="flex flex-col gap-2">
              {r.status === 'approved' && <button onClick={()=>markReceived(r.id)} className="bg-green-600 text-white px-3 py-1 rounded">Book Received</button>}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
