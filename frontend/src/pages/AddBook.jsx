import { useState } from "react";
import api from "../services/api";
import { useNavigate } from "react-router-dom";

export default function AddBook() {
  const [manual, setManual] = useState({ title: "", author: "", isbn: "", quantity: 1, is_public: true, description: "", image_url: "" });
  const [isbn, setIsbn] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const navigate = useNavigate();
  const goToMyBooks = () => {
    if (onSuccess) onSuccess();
    else navigate("/dashboard", { state: { tab: "profile", profileSection: "books" } });

  const createManual = async (e) => {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      await api.post("/books/", manual);
      goToMyBooks();
    } catch (err) {
      setError(err?.response?.data?.detail || "Create failed");
    } finally { setLoading(false); }
  };

  const fetchByIsbn = async () => {
    setError(""); setLoading(true);
    try {
      const res = await api.post("/books/by-isbn", { isbn, quantity: 1, is_public: true });
      // API creates a book immediately; navigate to my-books
      goToMyBooks();
    } catch (err) {
      setError(err?.response?.data?.detail || "ISBN fetch/create failed");
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen p-4 flex items-start justify-center">
      <div className="w-full max-w-3xl">
        <h2 className="text-2xl font-semibold mb-4">Add Book</h2>

        <section className="bg-white p-4 rounded shadow mb-6">
          <h3 className="font-medium mb-2">Add by ISBN</h3>
          <div className="flex gap-2">
            <input value={isbn} onChange={e=>setIsbn(e.target.value)} placeholder="ISBN" className="flex-1 p-2 border rounded"/>
            <button onClick={fetchByIsbn} disabled={loading||!isbn} className="bg-indigo-600 text-white px-4 rounded">Fetch & Add</button>
          </div>
        </section>

        <section className="bg-white p-4 rounded shadow">
          <h3 className="font-medium mb-2">Add manually</h3>
          {error && <div className="text-sm text-red-600 mb-2">{error}</div>}
          <form onSubmit={createManual} className="space-y-2">
            <input className="w-full p-2 border rounded" placeholder="Title" required value={manual.title} onChange={e=>setManual({...manual, title:e.target.value})} />
            <input className="w-full p-2 border rounded" placeholder="Author" value={manual.author} onChange={e=>setManual({...manual, author:e.target.value})} />
            <input className="w-full p-2 border rounded" placeholder="ISBN" value={manual.isbn} onChange={e=>setManual({...manual, isbn:e.target.value})} />
            <input type="number" className="w-24 p-2 border rounded" placeholder="Quantity" min="1" value={manual.quantity} onChange={e=>setManual({...manual, quantity:parseInt(e.target.value||1)})}/>
            <textarea className="w-full p-2 border rounded" placeholder="Description" value={manual.description} onChange={e=>setManual({...manual, description:e.target.value})}/>
            <div className="flex items-center gap-2">
              <label className="flex items-center gap-2"><input type="checkbox" checked={manual.is_public} onChange={e=>setManual({...manual, is_public:e.target.checked})}/> Public</label>
              <button className="ml-auto bg-indigo-600 text-white px-4 rounded" disabled={loading}>Add Book</button>
            </div>
          </form>
        </section>
      </div>
    </div>
  );
}