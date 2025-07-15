import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { register } from '../services/api';
import { UserPlus, User, Lock } from 'lucide-react';

const Register: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    try {
      await register(username, password);
      setSuccess('Registration successful! Redirecting to login...');
      setTimeout(() => navigate('/login'), 1500);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
    }
  };

  return (
    <div className="max-w-md mx-auto bg-gray-900 p-8 rounded-xl shadow-2xl border border-gray-700">
      <div className="text-center mb-8">
        <div className="bg-white p-3 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
          <UserPlus className="h-8 w-8 text-black" />
        </div>
        <h2 className="text-3xl font-bold text-white mb-2">Create Account</h2>
        <p className="text-gray-400">Join us to automate your job search</p>
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
              placeholder="Choose a username"
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
              placeholder="Choose a password"
              required 
            />
          </div>
        </div>
        {error && <div className="text-red-400 text-sm font-medium bg-red-900/20 p-3 rounded-lg border border-red-500">{error}</div>}
        {success && <div className="text-green-400 text-sm font-medium bg-green-900/20 p-3 rounded-lg border border-green-500">{success}</div>}
        <button type="submit" className="btn btn-primary w-full text-lg py-4">
          <UserPlus className="h-5 w-5 mr-2" />
          Create Account
        </button>
      </form>
    </div>
  );
};

export default Register; 