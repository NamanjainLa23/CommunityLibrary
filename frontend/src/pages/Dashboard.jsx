import { useEffect, useState } from "react";
import { clearToken, loadToken } from "../services/auth";
import { useNavigate } from "react-router-dom";
import MyBooks from "./MyBooks";
import AddBook from "./AddBook";
import Search from "./Search";
import NearbyBooks from "./NearbyBooks";
import BorrowedBooks from "./BorrowedBooks";

const TABS = [
  { key: "my", label: "My Books" },
  { key: "borrowed", label: "Borrowed" },
  { key: "nearby", label: "Nearby Books" },
  { key: "book", label: "Search Book" },
  { key: "add", label: "Add / Manage" },
];

export default function Dashboard() {
  const [tab, setTab] = useState("my");
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadToken();
    setUser({ loggedIn: !!localStorage.getItem("booklender_token") });
  }, []);

  const logout = () => {
    clearToken();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-5xl mx-auto">
        <div className="bg-white rounded-xl shadow p-6 flex justify-between items-center">
          <div>
            <h2 className="text-xl font-semibold">Dashboard</h2>
            <p className="text-sm text-gray-600">Manage your personal library.</p>
          </div>
          <div className="flex items-center gap-3">
            <button onClick={()=>navigate('/user/me')} className="text-sm text-indigo-600">My Profile</button>
            <button onClick={logout} className="bg-red-500 text-white px-3 py-1 rounded">Logout</button>
          </div>
        </div>

        <div className="mt-6 bg-white rounded-xl shadow p-4">
          <div className="border-b mb-4">
            <nav className="flex gap-2">
              {TABS.map(t => (
                <button key={t.key} onClick={()=>setTab(t.key)} className={`px-3 py-2 -mb-px ${tab===t.key ? 'border-b-2 border-indigo-600 text-indigo-600' : 'text-gray-600'}`}>
                  {t.label}
                </button>
              ))}
            </nav>
          </div>

          <div>
            {tab === 'my' && <MyBooks />}
            {tab === 'borrowed' && <BorrowedBooks />}
            {tab === 'nearby' && <NearbyBooks />}
            {tab === 'book' && <Search />}
            {tab === 'add' && <AddBook />}
          </div>
        </div>
      </div>
    </div>
  );
}