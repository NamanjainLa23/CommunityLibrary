import { useEffect, useState } from "react";
import api from "../services/api";

export default function AdminJoinRequests() {
  const [items, setItems] = useState([]);
  const [err, setErr] = useState("");

  const load = async () => {
    setErr("");
    try {
      const res = await api.get("/communities/join-requests");
      setItems(res.data || []);
    } catch (e) {
      setErr(e?.response?.data?.detail || "Failed to load join requests");
    }
  };

  useEffect(() => { load(); }, []);

  const decide = async (communityId, reqId, status) => {
    if (!confirm(`${status} this join request?`)) return;
    try {
      await api.patch(`/communities/${communityId}/join-requests/${reqId}`, { status });
      load();
    } catch (e) {
      alert(e?.response?.data?.detail || "Failed to update");
    }
  };

  return (
    <div>
      <h3 className="text-lg font-medium mb-3">Community join requests</h3>
      {err && <div className="text-sm text-red-600 mb-2">{err}</div>}
      {items.length === 0 && (
        <div className="text-sm text-gray-600">No pending requests.</div>
      )}
      <div className="space-y-3">
        {items.map((r) => (
          <div key={r.id} className="bg-white p-3 rounded shadow flex gap-3 items-start">
            <div className="flex-1">
              <div className="font-medium">{r.community_name}</div>
              <div className="text-sm text-gray-600">From: {r.username} ({r.email})</div>
              <div className="text-xs text-gray-500">Status: {r.status}</div>
            </div>
            <div className="flex flex-col gap-2">
              <button
                onClick={() => decide(r.community_id, r.id, "approved")}
                className="bg-green-600 text-white px-3 py-1 rounded"
              >
                Approve
              </button>
              <button
                onClick={() => decide(r.community_id, r.id, "rejected")}
                className="bg-red-600 text-white px-3 py-1 rounded"
              >
                Reject
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}