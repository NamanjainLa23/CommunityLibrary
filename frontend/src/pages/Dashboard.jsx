import { useEffect, useState } from "react";
import { clearToken, loadToken } from "../services/auth";
import { useNavigate } from "react-router-dom";
import MyBooks from "./MyBooks";
import AddBook from "./AddBook";
import NearbyBooks from "./NearbyBooks";
import BorrowedBooks from "./BorrowedBooks";
import Requests from "./Requests";
import LentBooks from "./LentBooks";
import Communities from "./Communities";
import AdminJoinRequests from "./AdminJoinRequests";
import api from "../services/api";

const TABS = [
  { key: "nearby", label: "Nearby Books" },
  { key: "communities", label: "Communities" },
  { key: "requests", label: "Requests" },
  { key: "lent", label: "Lent" },
];

export default function Dashboard() {
  const [tab, setTab] = useState("nearby");
  const [profileSection, setProfileSection] = useState("books");
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    loadToken();
    api.get("/users/me")
      .then((res) => setUser(res.data))
      .catch(() => setUser(null));
  }, []);

  const logout = () => {
    clearToken();
    navigate("/login");
  };

  const profileSections = [
    { key: "books", label: "My Books" },
    { key: "borrowed", label: "Borrowed" },
    { key: "add", label: "Add / Manage" },
    ...(user?.is_admin ? [{ key: "admin", label: "Join requests" }] : []),
  ];

  return (
    <div className="min-h-screen bg-paper text-ink p-3 sm:p-6 overflow-x-hidden">
      <div className="max-w-5xl mx-auto w-full">
        <header className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-6">
          <div>
            <p className="text-xs tracking-[0.25em] uppercase text-muted">Community Library</p>
            <h1 className="font-serif text-3xl mt-1">Your shelf</h1>
            <p className="text-sm text-muted mt-1">
              {user?.username ? `Signed in as ${user.username}` : "Borrow, lend, belong."}
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <button
              onClick={() => setTab("profile")}
              className={`px-4 py-2 rounded-full text-sm ${
                tab === "profile"
                  ? "bg-accent text-white"
                  : "bg-page border border-line text-ink hover:border-accent"
              }`}
            >
              My Profile
            </button>
            <button
              onClick={logout}
              className="px-4 py-2 rounded-full text-sm border border-line bg-page text-muted hover:text-red-800"
            >
              Logout
            </button>
          </div>
        </header>
  
        <nav className="flex gap-2 overflow-x-auto pb-2 mb-4">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`px-4 py-2 rounded-full text-sm shrink-0 ${
                tab === t.key
                  ? "bg-accent text-white shadow-sm"
                  : "bg-page border border-line text-muted hover:text-ink"
              }`}
            >
              {t.label}
            </button>
          ))}
        </nav>
  
        <div className="bg-page border border-line rounded-3xl shadow-[0_16px_40px_rgba(80,50,20,0.08)] p-4 sm:p-6 min-w-0">
          {tab === "profile" && (
            <div>
              <div className="flex gap-2 overflow-x-auto mb-5">
                {profileSections.map((s) => (
                  <button
                    key={s.key}
                    onClick={() => setProfileSection(s.key)}
                    className={`px-3 py-1.5 rounded-full text-sm shrink-0 ${
                      profileSection === s.key
                        ? "bg-ink text-page"
                        : "bg-paper text-muted border border-line"
                    }`}
                  >
                    {s.label}
                  </button>
                ))}
              </div>
              {profileSection === "books" && <MyBooks />}
              {profileSection === "borrowed" && <BorrowedBooks />}
              {profileSection === "add" && (
                <AddBook onSuccess={() => setProfileSection("books")} />
              )}
              {profileSection === "admin" && user?.is_admin && <AdminJoinRequests />}
            </div>
          )}
          {tab === "nearby" && <NearbyBooks />}
          {tab === "communities" && <Communities />}
          {tab === "requests" && <Requests />}
          {tab === "lent" && <LentBooks />}
        </div>
      </div>
    </div>
  );
}