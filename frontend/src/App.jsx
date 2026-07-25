import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Signup from "./pages/Signup";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
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
        <Route path="/" element={<Navigate to="/dashboard" />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={
          <PrivateRoute><Dashboard/></PrivateRoute>
        } />
      </Routes>
    </BrowserRouter>
  );
}

export default App;