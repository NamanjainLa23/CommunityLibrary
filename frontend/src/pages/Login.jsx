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
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="w-full max-w-md bg-white rounded-xl shadow p-6">
        <h1 className="text-2xl font-semibold mb-4">Sign in</h1>
        {error && <div className="mb-3 text-sm text-red-600">{error}</div>}
        <form onSubmit={submit} className="space-y-3">
          <input className="w-full p-2 border rounded" placeholder="Mobile" value={form.mobile} onChange={e=>setForm({...form, mobile:e.target.value})} required />
          <div className="relative">
            <input
              className="w-full p-2 pr-16 border rounded"
              placeholder="Password"
              type={showPassword ? "text" : "password"}
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              required
            />
            <button
              type="button"
              onClick={() => setShowPassword((v) => !v)}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-sm text-indigo-600"
            >
              {showPassword ? "Hide" : "Show"}
            </button>
          </div>
          {wakeMessage && (
            <div className="mb-3 text-sm text-amber-800 bg-amber-50 p-3 rounded">
              {wakeMessage}
            </div>
          )}
          <button className="w-full bg-indigo-600 text-white p-2 rounded hover:bg-indigo-700" disabled={waking}>{waking ? "Starting server…" : "Login"}</button>
        </form>
        <p className="mt-4 text-center text-sm">
          New here? <Link to="/signup" className="text-indigo-600">Create account</Link>
        </p>
      </div>
    </div>
  );
}