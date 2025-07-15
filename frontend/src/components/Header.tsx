import React from 'react';
import { useState, useEffect } from 'react';
import { Briefcase, User, LogOut, LogIn, UserPlus, Sparkles } from 'lucide-react';

function Header() {
  const [username, setUsername] = useState<string | null>(null);

  useEffect(() => {
    setUsername(localStorage.getItem('username'));
  }, []);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    setUsername(null);
    window.location.reload();
  };

  return (
    <header className="bg-gradient-to-r from-gray-900 via-gray-800 to-black border-b border-gray-700 shadow-2xl py-6 mb-8">
      <div className="container mx-auto flex justify-between items-center px-6">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-3">
            <div className="bg-white p-2 rounded-lg shadow-lg">
              <Briefcase className="h-8 w-8 text-black" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-white flex items-center space-x-2">
                <span>AI Job Application</span>
                <Sparkles className="h-6 w-6 text-yellow-400 animate-pulse" />
              </h1>
              <p className="text-gray-300 text-sm font-medium">Automate Your Job Search</p>
            </div>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          {username ? (
            <>
              <div className="flex items-center space-x-3 bg-gray-800 px-4 py-2 rounded-lg border border-gray-600">
                <User className="h-5 w-5 text-green-400" />
                <span className="text-white font-bold">Welcome, {username}!</span>
              </div>
              <button 
                onClick={handleLogout} 
                className="btn btn-outline flex items-center space-x-2 hover:bg-red-600 hover:border-red-600"
              >
                <LogOut className="h-4 w-4" />
                <span>Logout</span>
              </button>
            </>
          ) : (
            <>
              <a href="/login" className="btn btn-outline flex items-center space-x-2 text-white">
                <LogIn className="h-4 w-4" />
                <span>Login</span>
              </a>
              <a href="/register" className="btn btn-primary flex items-center space-x-2 text-black">
                <UserPlus className="h-4 w-4" />
                <span>Register</span>
              </a>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

export default Header; 