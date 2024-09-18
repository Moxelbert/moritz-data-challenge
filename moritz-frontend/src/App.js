import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import AddNumbers from './components/AddNumbers';
import ProtectedRoute from './components/ProtectedRoute';
import { jwtDecode } from 'jwt-decode';

// Function to check if token is valid
const isTokenValid = () => {
  const token = localStorage.getItem('token');
  if (!token) return false;

  try {
    const decodedToken = jwtDecode(token); // Decode the token
    const currentTime = Date.now() / 1000; // Current time in seconds
    if (decodedToken.exp < currentTime) {
      // Token is expired, remove it
      localStorage.removeItem('token');
      return false;
    }
    return true;
  } catch (error) {
    // If token is invalid, remove it and return false
    localStorage.removeItem('token');
    return false;
  }
};

function App() {
  const isAuthenticated = isTokenValid(); 

  return (
    <Router>
      <Routes>
        {/* Redirect to login if the base path is accessed */}
        <Route path="/" element={isAuthenticated ? <Navigate to="/protected" /> : <Navigate to="/login" />} />
        
        {/* Login Route */}
        <Route path="/login" element={<Login />} />
        
        {/* Protected Route */}
        <Route path="/protected" element={<ProtectedRoute><AddNumbers /></ProtectedRoute>} />
      </Routes>
    </Router>
  );
}

export default App;