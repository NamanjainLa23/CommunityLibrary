import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Signup from "./pages/Signup";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import AddBook from "./pages/AddBook";
import MyBooks from "./pages/MyBooks"
import UserProfile from "./pages/UserProfile";
import NearbyBooks from "./pages/NearbyBooks";
import Search from "./pages/Search";
import { loadToken } from "./services/auth";

function App() {
  loadToken(); // ensure axios header set if token present

  const PrivateRoute = ({ children }) => {
    const t = !!localStorage.getItem("booklender_token");
    return t ? children : <Navigate to="/login" />;
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/users" />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/login" element={<Login />} />
        <Route path="/add-book" element={<PrivateRoute><AddBook/></PrivateRoute>} />
        <Route path="/my-books" element={<PrivateRoute><MyBooks/></PrivateRoute>} />
        <Route path="/user/:usernameOrId" element={<UserProfile/>} />
        <Route path="/users" element={<PrivateRoute><NearbyBooks/></PrivateRoute>} />
        <Route path="/search" element={<Search/>} />
        <Route path="/dashboard" element={
          <PrivateRoute><Dashboard/></PrivateRoute>
        } />
      </Routes>
    </BrowserRouter>
  );
}

export default App;