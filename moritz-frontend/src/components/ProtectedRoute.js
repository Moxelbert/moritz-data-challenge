import { Navigate } from 'react-router-dom';

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('token');

  // ff token is missing, redirect to login
  if (!token) {
    return <Navigate to="/login" />;
  }

  // else render the protected component
  return children;
}

export default ProtectedRoute;
