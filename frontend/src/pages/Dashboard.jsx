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
  { key: "profile", label: "My Profile" },
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
    <div className="min-h-screen bg-gray-50 p-3 sm:p-4 overflow-x-hidden">
      <div className="max-w-5xl mx-auto w-full">
        <div className="bg-white rounded-xl shadow p-4 sm:p-6 flex flex-col gap-3 sm:flex-row sm:justify-between sm:items-center">
          <div>
            <h2 className="text-xl font-semibold">Dashboard</h2>
            <p className="text-sm text-gray-600">
              {user?.username ? `Signed in as ${user.username}` : "Manage your personal library."}
            </p>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            <button onClick={() => setTab("profile")} className={`text-sm ${tab === "profile" ? "font-semibold text-indigo-700" : "text-indigo-600"}`}>
              My Profile
            </button>
            <button onClick={logout} className="bg-red-500 text-white px-3 py-1 rounded">
              Logout
            </button>
          </div>
        </div>

        <div className="mt-4 sm:mt-6 bg-white rounded-xl shadow p-3 sm:p-4 overflow-hidden">
          <div className="border-b mb-4 -mx-3 px-3 sm:mx-0 sm:px-0">
            <nav className="flex gap-1 overflow-x-auto whitespace-nowrap pb-px">
              {TABS.map((t) => (
                <button
                  key={t.key}
                  onClick={() => setTab(t.key)}
                  className={`px-3 py-2 -mb-px shrink-0 text-sm ${
                    tab === t.key
                      ? "border-b-2 border-indigo-600 text-indigo-600"
                      : "text-gray-600"
                  }`}
                >
                  {t.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="min-w-0">
            {tab === "profile" && (
              <div>
                <div className="flex gap-2 overflow-x-auto mb-4">
                  {profileSections.map((s) => (
                    <button
                      key={s.key}
                      onClick={() => setProfileSection(s.key)}
                      className={`px-3 py-1.5 rounded-full text-sm shrink-0 ${
                        profileSection === s.key
                          ? "bg-indigo-600 text-white"
                          : "bg-gray-100 text-gray-700"
                      }`}
                    >
                      {s.label}
                    </button>
                  ))}
                </div>
                {profileSection === "books" && <MyBooks />}
                {profileSection === "borrowed" && <BorrowedBooks />}
                {profileSection === "add" && (<AddBook onSuccess={() => {setProfileSection("books");}} />)}
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
    </div>
  );
}