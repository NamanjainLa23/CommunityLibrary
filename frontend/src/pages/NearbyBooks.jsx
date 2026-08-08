import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

export default function NearbyBooks(){
  const navigate = useNavigate();
  const [communities, setCommunities] = useState([]);
  const [currentUserId, setCurrentUserId] = useState(null);
  const [selectedCommunity, setSelectedCommunity] = useState(null);
  const [booksByOwner, setBooksByOwner] = useState([]);
  const [selectedOwner, setSelectedOwner] = useState(null);
  const [availableCommunities, setAvailableCommunities] = useState([]);
  const [showAvailable, setShowAvailable] = useState(false);
  const [err, setErr] = useState("");

  useEffect(()=>{
    const load = async ()=>{
      setErr("");
      try{
        const res = await api.get('/communities/me');
        setCommunities(res.data || []);
      }catch(e){
        setErr('Failed to load your communities');
      }
      try{
        const me = await api.get('/users/me');
        setCurrentUserId(me.data && me.data.id ? me.data.id : null);
      }catch(_){
        //ignore
      }
    };
    load();
  },[]);

  const showCommunity = async (c) => {
    setErr("");
    setSelectedCommunity(c);
    setSelectedOwner(null);
    setBooksByOwner([]);

    try{
      const res = await api.get(`/communities/${encodeURIComponent(c.id)}`);
      const members = res.data.members || [];

      const otherMembers = members.filter(m => m.id !== currentUserId);
      const bookPromises = otherMembers.map(async (m) => {
        const br = await api.get(`/books/public?owner_id=${m.id}`);
        return {owner: m, books: br.data || []}
      });
      const books = await Promise.all(bookPromises);
      setBooksByOwner(books.filter(r=> (r.books || []).length > 0));
    }catch(e){
      setErr('Failed to load community books');
    }
  };

  const showOwner = async (owner) => {
    setSelectedOwner(owner);
  };

  const loadAvailable = async () => {
    setErr("");
    try{
      const res = await api.get('/commuinities')
      setAvailableCommunities(res.data || []);
      setShowAvailable(true);
    }catch(e){
      setErr('Failed to load available communities');
    }
  };

  const joinCommunity = async (id) => {
    if(!confirm('Join this community?')) return;
    try{
      await api.post(`/communities/${encodeURIComponent(id)}/join`);
      const res = await api.get('/communities/me');
      setCommunities(res.data || []);
      setShowAvailable(false);
    }catch(e){
      setErr('Failed to join community');
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4"> 
      <div className="col-span-1 bg-gray-50 p-3 rounded">
        <h3 className="font-medium mb-2">Communities</h3>
        {err && <div className="text-sm text-red-600 mb-2">{err}</div>}
        <div className="space-y-2">
          {communities.map(c=>(
            <button key={c.id} onClick={()=>showCommunity(c)} className={`w-full text-left p-2 bg-white rounded shadow-sm hover:bg-indigo-50 ${selectedCommunity && selectedCommunity.id===c.id ? 'ring-2 ring-indigo-200' : ''}`}>
              <div className="font-medium">{c.name}</div>
            </button>
          ))}
        </div>
      </div>

      <div className="col-span-2 bg-white p-3 rounded">
        <h3 className="font-medium mb-3">{selectedCommunity ? `Community ${selectedCommunity.name}` : 'Select a community'}</h3>
        {booksByOwner.length===0 && <div className="text-sm text-gray-600">No public books found for this community.</div>}
        <div className="space-y-3">
          {booksByOwner.map(group=> (
            <div key={group.owner.id} className="p-3 border rounded">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">{group.owner.username}</div>
                  <div className="text-xs text-gray-600">{group.owner.first_name || ''} {group.owner.last_name || ''}</div>
                </div>
                <div>
                  <button onClick={()=>showOwner(group.owner)} className="text-sm text-indigo-600">View</button>
                </div>
              </div>
              <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
                {(!selectedOwner || selectedOwner.id === group.owner.id) && group.books.map(b=> (
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
          ))}
        </div>
      </div>
    </div>
  );
}