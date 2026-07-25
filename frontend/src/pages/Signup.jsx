import { useState } from "react";
import api from "../services/api";
import { saveToken } from "../services/auth";
import { useNavigate, Link } from "react-router-dom";

export default function Signup() {
  const [form, setForm] = useState({ username: "", email: "", first_name: "", last_name: "", mobile: "", password: "" });
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const res = await api.post("/auth/signup", form);
      // API returns user; auto-login by calling login endpoint
      const loginRes = await api.post("/auth/login", { mobile: form.mobile, password: form.password });
      saveToken(loginRes.data);
      navigate("/dashboard");
    } catch (err) {
      setError(err?.response?.data?.detail || "Signup failed");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 p-4">
      <div className="w-full max-w-md bg-white rounded-xl shadow p-6">
        <h1 className="text-2xl font-semibold mb-4">Create account</h1>
        {error && <div className="mb-3 text-sm text-red-600">{error}</div>}
        <form onSubmit={submit} className="space-y-3">
          <input className="w-full p-2 border rounded" placeholder="Username" value={form.username} onChange={e=>setForm({...form, username:e.target.value})} required />
          <input className="w-full p-2 border rounded" placeholder="Email" type="email" value={form.email} onChange={e=>setForm({...form, email:e.target.value})} required />
          <input className="w-full p-2 border rounded" placeholder="First name" value={form.first_name} onChange={e=>setForm({...form, first_name:e.target.value})} />
          <input className="w-full p-2 border rounded" placeholder="Last name" value={form.last_name} onChange={e=>setForm({...form, last_name:e.target.value})} />
          <input className="w-full p-2 border rounded" placeholder="Mobile" value={form.mobile} onChange={e=>setForm({...form, mobile:e.target.value})} />
          <input className="w-full p-2 border rounded" placeholder="Password" type="password" value={form.password} onChange={e=>setForm({...form, password:e.target.value})} required />
          <button className="w-full bg-indigo-600 text-white p-2 rounded hover:bg-indigo-700">Sign up</button>
        </form>
        <p className="mt-4 text-center text-sm">
          Already have an account? <Link to="/login" className="text-indigo-600">Login</Link>
        </p>
      </div>
    </div>
  );
}