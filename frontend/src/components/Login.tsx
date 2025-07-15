import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { login } from '../services/api';
import { LogIn, User, Lock } from 'lucide-react';

const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const res = await login(username, password);
      localStorage.setItem('token', res.data.access_token);
      localStorage.setItem('username', username);
      navigate('/');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    }
  };

  return (
    <div className="max-w-md mx-auto bg-gray-900 p-8 rounded-xl shadow-2xl border border-gray-700">
      <div className="text-center mb-8">
        <div className="bg-white p-3 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
          <LogIn className="h-8 w-8 text-black" />
        </div>
        <h2 className="text-3xl font-bold text-white mb-2">Welcome Back</h2>
        <p className="text-gray-400">Sign in to your account</p>
      </div>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <label className="block text-white font-bold text-lg">Username</label>
          <div className="relative">
            <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input 
              type="text" 
              value={username} 
              onChange={e => setUsername(e.target.value)} 
              className="input-field w-full pl-10 text-lg" 
              placeholder="Enter your username"
              required 
            />
          </div>
        </div>
        <div className="space-y-2">
          <label className="block text-white font-bold text-lg">Password</label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input 
              type="password" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              className="input-field w-full pl-10 text-lg" 
              placeholder="Enter your password"
              required 
            />
          </div>
        </div>
        {error && <div className="text-red-400 text-sm font-medium bg-red-900/20 p-3 rounded-lg border border-red-500">{error}</div>}
        <button type="submit" className="btn btn-primary w-full text-lg py-4">
          <LogIn className="h-5 w-5 mr-2" />
          Sign In
        </button>
      </form>
    </div>
  );
};

export default Login; 