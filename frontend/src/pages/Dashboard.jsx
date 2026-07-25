import { useEffect, useState } from "react";
import api from "../services/api";
import { clearToken, loadToken } from "../services/auth";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadToken();
    // Optionally fetch current user from backend (you'll implement endpoint later)
    // For now show token presence
    setUser({ loggedIn: !!localStorage.getItem("booklender_token") });
  }, []);

  const logout = () => {
    clearToken();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-3xl mx-auto">
        <div className="bg-white rounded-xl shadow p-6 flex justify-between items-center">
          <div>
            <h2 className="text-xl font-semibold">Welcome</h2>
            <p className="text-sm text-gray-600">You are logged in.</p>
          </div>
          <div>
            <button onClick={logout} className="bg-red-500 text-white px-3 py-1 rounded">Logout</button>
          </div>
        </div>
        <div className="mt-6">
          <p className="text-sm text-gray-700">(Dashboard content goes here — we'll add library features next.)</p>
        </div>
      </div>
    </div>
  );
}