import { useEffect, useState } from "react";
import api from "../services/api";

export default function Communities(){
  const [my, setMy] = useState([]);
  const [available, setAvailable] = useState([]);
  const [err, setErr] = useState("");

  const load = async ()=>{
    setErr("");
    try{
      const res = await api.get('/communities/me');
      setMy(res.data || []);
    }catch(e){
      setMy([]);
    }
    try{
      const res2 = await api.get('/communities');
      setAvailable(res2.data || []);
    }catch(e){
      setAvailable([]);
    }
  }

  useEffect(()=>{ load(); }, []);

  const join = async (id)=>{
    if(!confirm('Join this community?')) return;
    try{
      await api.post(`/communities/${encodeURIComponent(id)}/join`);
      await load();
    }catch(e){
      alert('Failed to join');
    }
  }

  const leave = async (id)=>{
    if(!confirm('Leave this community?')) return;
    try{
      await api.post(`/communities/${encodeURIComponent(id)}/leave`);
      await load();
    }catch(e){
      alert('Failed to leave');
    }
  }

  return (
    <div className="p-4">
      <h3 className="text-lg font-medium mb-3">Communities</h3>
      {err && <div className="text-sm text-red-600 mb-2">{err}</div>}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-3 rounded">
          <h4 className="font-medium mb-2">Your Communities</h4>
          {my.length===0 && <div className="text-sm text-gray-600">You are not a member of any communities.</div>}
          <div className="space-y-2 mt-2">
            {my.map(c => (
              <div key={c.id} className="flex items-center justify-between p-2 border rounded">
                <div>
                  <div className="font-medium">{c.name}</div>
                </div>
                <div>
                  <button onClick={()=>leave(c.id)} className="text-sm text-red-600">Leave</button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white p-3 rounded">
          <h4 className="font-medium mb-2">Available Communities</h4>
          {available.length===0 && <div className="text-sm text-gray-600">No communities available.</div>}
          <div className="space-y-2 mt-2">
            {available.map(c => (
              <div key={c.id} className="flex items-center justify-between p-2 border rounded">
                <div>
                  <div className="font-medium">{c.name}</div>
                </div>
                <div>
                  <button onClick={()=>join(c.id)} className="text-sm text-indigo-600">Join</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
