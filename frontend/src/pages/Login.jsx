import { useState, useEffect } from "react";
import api from "../services/api";
import { saveToken } from "../services/auth";
import { useNavigate, Link } from "react-router-dom";

export default function Login() {
  const [form, setForm] = useState({ mobile: "", password: "" });
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [waking, setWaking] = useState(true);
  const [wakeMessage, setWakeMessage] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    let cancelled = false;
    const wake = async () => {
      setWaking(true);
      setWakeMessage(
        "The app was idle. Starting the server — this can take about 30–40 seconds."
      );
      for (let i = 0; i < 20 && !cancelled; i++) {
        try {
          await api.get("/health"); // baseURL already includes /api
          if (!cancelled) {
            setWaking(false);
            setWakeMessage("");
          }
          return;
        } catch {
          await new Promise((r) => setTimeout(r, 2000));
        }
      }
      if (!cancelled) {
        setWakeMessage("Still starting. Wait a bit, then try again.");
      }
    };
    wake();
    return () => { cancelled = true; };
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const res = await api.post("/auth/login", form);
      saveToken(res.data);
      navigate("/dashboard");
    } catch (err) {
      setError(err?.response?.data?.detail || "Login failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-[#f4efe6] relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,_#f3d5b5_0%,_transparent_50%),radial-gradient(ellipse_at_bottom_right,_#c4ddd6_0%,_transparent_45%)]" />
      <div className="absolute -left-8 top-16 rotate-[-18deg] hidden md:flex gap-1">
        {["#7c2d12", "#1e3a5f", "#b45309", "#365314", "#9f1239"].map((c) => (
          <div key={c} className="w-7 h-44 rounded-sm shadow-lg" style={{ background: c }} />
        ))}
      </div>
  
      <div className="relative w-full max-w-5xl grid md:grid-cols-2 gap-8 items-center">
        <div className="hidden md:block text-[#3d2c1e] px-4">
          <p className="text-sm tracking-[0.25em] uppercase text-[#9a6b4a]">Community Library</p>
          <h1 className="mt-3 text-5xl font-serif leading-tight">
            Books next door,<br />stories to share.
          </h1>
          <p className="mt-4 text-lg text-[#6b5344] max-w-md">
            Sign in to borrow from neighbors, lend your shelf, and keep the stack circulating.
          </p>
        </div>
  
        <div className="w-full max-w-md mx-auto bg-[#fffaf3] border border-[#e8d9c4] rounded-3xl shadow-[0_20px_50px_rgba(80,50,20,0.12)] p-8">
          <div className="md:hidden mb-4">
            <p className="text-xs tracking-[0.2em] uppercase text-[#9a6b4a]">Community Library</p>
          </div>
          <h2 className="font-serif text-3xl text-[#3d2c1e]">Welcome back</h2>
          <p className="text-sm text-[#6b5344] mt-1 mb-6">Open your shelf with mobile and password.</p>
  
          {error && (
            <div className="mb-4 text-sm text-red-800 bg-red-50 border border-red-100 p-3 rounded-xl">{error}</div>
          )}
          {wakeMessage && (
            <div className="mb-4 text-sm text-amber-900 bg-amber-50 border border-amber-100 p-3 rounded-xl">
              {wakeMessage}
            </div>
          )}
  
          <form onSubmit={submit} className="space-y-4">
            <label className="block text-xs font-medium text-[#6b5344]">Mobile</label>
            <input
              className="w-full p-3 rounded-xl border border-[#e0d0bc] bg-white focus:outline-none focus:ring-2 focus:ring-[#c2410c]/40"
              placeholder="9000000000"
              value={form.mobile}
              onChange={(e) => setForm({ ...form, mobile: e.target.value })}
              required
            />
            <label className="block text-xs font-medium text-[#6b5344]">Password</label>
            <div className="relative">
              <input
                className="w-full p-3 pr-16 rounded-xl border border-[#e0d0bc] bg-white focus:outline-none focus:ring-2 focus:ring-[#c2410c]/40"
                placeholder="••••••••"
                type={showPassword ? "text" : "password"}
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
                required
              />
              <button
                type="button"
                onClick={() => setShowPassword((v) => !v)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-sm text-[#c2410c]"
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
            <button
              className="w-full mt-2 bg-[#c2410c] hover:bg-[#9a3412] text-white py-3 rounded-xl font-medium disabled:opacity-60"
              disabled={waking}
            >
              {waking ? "Waking the library…" : "Open the library"}
            </button>
          </form>
  
          <p className="mt-6 text-center text-sm text-[#6b5344]">
            New here?{" "}
            <Link to="/signup" className="text-[#c2410c] font-medium underline underline-offset-2">
              Get a library card
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}