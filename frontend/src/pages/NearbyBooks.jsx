import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

export default function NearbyBooks(){
  const navigate = useNavigate();
  const [users, setUsers] = useState([]);
  const [selected, setSelected] = useState(null);
  const [books, setBooks] = useState([]);
  const [err, setErr] = useState("");

  useEffect(()=>{
    const load = async ()=>{
      setErr("");
      try{
        const res = await api.get('/users');
        setUsers(res.data || []);
      }catch(e){
        setErr('Failed to load users');
      }
    };
    load();
  },[]);

  const showUser = async (u) => {
    setSelected(u);
    setBooks([]);
    try{
      // prefer owner_id filter
      const res = await api.get(`/books/public?owner_id=${u.id}`);
      setBooks(res.data || []);
    }catch(e){
      setErr('Failed to load user books');
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4"> 
      <div className="col-span-1 bg-gray-50 p-3 rounded">
        <h3 className="font-medium mb-2">Users</h3>
        {err && <div className="text-sm text-red-600 mb-2">{err}</div>}
        <div className="space-y-2">
          {users.map(u=>(
            <button key={u.id} onClick={()=>showUser(u)} className="w-full text-left p-2 bg-white rounded shadow-sm hover:bg-indigo-50">
              <div className="font-medium">{u.username}</div>
              <div className="text-xs text-gray-600">{u.first_name || ''} {u.last_name || ''}</div>
            </button>
          ))}
        </div>
      </div>

      <div className="col-span-2 bg-white p-3 rounded">
        <h3 className="font-medium mb-3">{selected ? `Public books by ${selected.username}` : 'Select a user'}</h3>
        {books.length===0 && <div className="text-sm text-gray-600">No public books found.</div>}
        <div className="space-y-3">
          {books.map(b=> (
            <div key={b.id} className="p-3 border rounded flex gap-3 items-start">
              {b.image_url ? <img src={b.image_url} className="w-14 h-20 object-cover rounded" alt="cover" /> : <div className="w-14 h-20 bg-gray-100 rounded" />}
              <div>
                <div className="font-medium">{b.title}</div>
                <div className="text-sm text-gray-600">{b.author}</div>
                <div className="text-xs text-gray-500">ISBN: {b.isbn} — Qty: {b.quantity}</div>
              </div>
              <div className="ml-auto flex flex-col gap-2">
                <button onClick={async ()=>{
                  if(!localStorage.getItem('booklender_token')){ navigate('/login'); return; }
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
    </div>
  );
}
