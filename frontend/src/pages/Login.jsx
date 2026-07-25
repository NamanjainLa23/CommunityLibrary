import { useState } from "react";
import api from "../services/api";
import { saveToken } from "../services/auth";
import { useNavigate, Link } from "react-router-dom";

export default function Login() {
  const [form, setForm] = useState({ mobile: "", password: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();

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
          <input className="w-full p-2 border rounded" placeholder="Password" type="password" value={form.password} onChange={e=>setForm({...form, password:e.target.value})} required />
          <button className="w-full bg-indigo-600 text-white p-2 rounded hover:bg-indigo-700">Login</button>
        </form>
        <p className="mt-4 text-center text-sm">
          New here? <Link to="/signup" className="text-indigo-600">Create account</Link>
        </p>
      </div>
    </div>
  );
}