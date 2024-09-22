import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);

  const navigate = useNavigate();

  const handleLogin = async () => {
    try { //https://python-api-360127904619.europe-west3.run.app/login/
      const response = await axios.post('http://localhost:8000/login/', {
        username,
        password,
      });

      // store token in localStorage
      localStorage.setItem('token', response.data.access_token);
      setError(null);

      // redirect to the protected route after successful login
      navigate('/protected');
    } catch (err) {
      setError('Invalid credentials');
    }
  };

  return (
    <div>
      <h2>Login</h2>
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Username"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
      />
      <button onClick={handleLogin}>Login</button>
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}

export default Login;