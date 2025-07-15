import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import JobApplicationForm from './components/JobApplicationForm';
import ApplicationStatus from './components/ApplicationStatus';
import PersonalInfoForm from './components/PersonalInfoForm';
import ResumeUpload from './components/ResumeUpload';
import Login from './components/Login';
import Register from './components/Register';

function App() {
  // Simple handler for demonstration; you can expand this as needed
  const handlePersonalInfoSubmit = (data: any) => {
    console.log('Personal info submitted:', data);
    // You can add navigation or API calls here
  };

  return (
    <Router>
      <div className="min-h-screen bg-black text-white">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<JobApplicationForm />} />
            <Route path="/personal-info" element={<PersonalInfoForm onSubmit={handlePersonalInfoSubmit} />} />
            <Route path="/status/:appId" element={<ApplicationStatus />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App; 