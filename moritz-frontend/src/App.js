import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import AddNumbers from './components/AddNumbers';
import UploadJson from './components/UploadJson';
import ProtectedRoute from './components/ProtectedRoute';
import { jwtDecode } from 'jwt-decode';

// check if token is valid
const isTokenValid = () => {
  const token = localStorage.getItem('token');
  if (!token) return false;

  try {
    const decodedToken = jwtDecode(token);
    const currentTime = Date.now() / 1000;
    if (decodedToken.exp < currentTime) {
      // if token is expired, remove it
      localStorage.removeItem('token');
      return false;
    }
    return true;
  } catch (error) {
    // ff token is invalid, remove it and return false
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
        
        {/* Protected Route with both components */}
        <Route path="/protected" element={<ProtectedRoute>
          <AddNumbers />
          <UploadJson />
        </ProtectedRoute>} />
      </Routes>
    </Router>
  );
}

export default App;