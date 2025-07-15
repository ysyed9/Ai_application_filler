import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Link, Upload, Play, AlertCircle, CheckCircle } from 'lucide-react';
import ResumeUpload from './ResumeUpload';
import PersonalInfoForm from './PersonalInfoForm';
import { api } from '../services/api';

interface ApplicationStatus {
  status: 'idle' | 'processing' | 'completed' | 'error';
  message: string;
  progress: number;
  appId?: string;
}

const JobApplicationForm: React.FC = () => {
  const [jobUrl, setJobUrl] = useState('');
  const [resumeData, setResumeData] = useState<any>(null);
  const [personalInfo, setPersonalInfo] = useState<any>(null);
  const [applicationStatus, setApplicationStatus] = useState<ApplicationStatus>({
    status: 'idle',
    message: '',
    progress: 0
  });
  const [currentStep, setCurrentStep] = useState<'url' | 'resume' | 'personal' | 'submit'>('url');
  const navigate = useNavigate();

  const handleUrlSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (jobUrl.trim()) {
      setCurrentStep('resume');
    }
  };

  const handleResumeUpload = (data: any) => {
    setResumeData(data);
    setCurrentStep('personal');
  };

  const handlePersonalInfoSubmit = (data: any) => {
    setPersonalInfo(data);
    setCurrentStep('submit');
  };

  const handleStartApplication = async () => {
    if (!jobUrl || !resumeData || !personalInfo) {
      return;
    }

    setApplicationStatus({
      status: 'processing',
      message: 'Starting application process...',
      progress: 0
    });

    try {
      const response = await api.post('/api/start-application', {
        url: jobUrl,
        personal_info: personalInfo,
        resume_data: resumeData
      });

      const { application_id } = response.data;
      
      setApplicationStatus({
        status: 'processing',
        message: 'Application started successfully!',
        progress: 10,
        appId: application_id
      });

      // Navigate to status page
      navigate(`/status/${application_id}`);

    } catch (error: any) {
      setApplicationStatus({
        status: 'error',
        message: error.response?.data?.detail || 'Failed to start application',
        progress: 0
      });
    }
  };

  const resetForm = () => {
    setJobUrl('');
    setResumeData(null);
    setPersonalInfo(null);
    setCurrentStep('url');
    setApplicationStatus({
      status: 'idle',
      message: '',
      progress: 0
    });
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          AI Job Application Auto-Filler
        </h1>
        <p className="text-gray-600 text-lg">
          Automatically fill out job applications with your resume and personal information
        </p>
      </div>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-center space-x-4">
          {[
            { key: 'url', label: 'Job URL', icon: Link },
            { key: 'resume', label: 'Resume Upload', icon: Upload },
            { key: 'personal', label: 'Personal Info', icon: 'User' },
            { key: 'submit', label: 'Submit', icon: Play }
          ].map((step, index) => {
            const Icon = step.icon;
            const isActive = currentStep === step.key;
            const isCompleted = ['url', 'resume', 'personal'].indexOf(step.key) < ['url', 'resume', 'personal'].indexOf(currentStep);
            
            return (
              <div key={step.key} className="flex items-center">
                <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                  isActive ? 'border-primary-600 bg-primary-600 text-white' :
                  isCompleted ? 'border-green-500 bg-green-500 text-white' :
                  'border-gray-300 bg-white text-gray-400'
                }`}>
                  {isCompleted ? (
                    <CheckCircle className="h-5 w-5" />
                  ) : (
                    <Icon className="h-5 w-5" />
                  )}
                </div>
                <span className={`ml-2 text-sm font-medium ${
                  isActive ? 'text-primary-600' :
                  isCompleted ? 'text-green-600' :
                  'text-gray-400'
                }`}>
                  {step.label}
                </span>
                {index < 3 && (
                  <div className={`w-16 h-0.5 ml-4 ${
                    isCompleted ? 'bg-green-500' : 'bg-gray-300'
                  }`} />
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Step 1: Job URL */}
      {currentStep === 'url' && (
        <div className="card animate-fade-in">
          <h2 className="text-xl font-semibold mb-4">Step 1: Enter Job Application URL</h2>
          <form onSubmit={handleUrlSubmit} className="space-y-4">
            <div className="form-group">
              <label htmlFor="jobUrl" className="form-label">
                Job Application URL
              </label>
              <input
                type="url"
                id="jobUrl"
                value={jobUrl}
                onChange={(e) => setJobUrl(e.target.value)}
                placeholder="https://example.com/job-application"
                className="input-field"
                required
              />
              <p className="text-sm text-gray-500 mt-1">
                Paste the URL of the job application form you want to fill out
              </p>
            </div>
            <button type="submit" className="btn-primary">
              Continue to Resume Upload
            </button>
          </form>
        </div>
      )}

      {/* Step 2: Resume Upload */}
      {currentStep === 'resume' && (
        <div className="card animate-fade-in">
          <h2 className="text-xl font-semibold mb-4">Step 2: Upload Your Resume</h2>
          <ResumeUpload onUpload={handleResumeUpload} />
          <div className="mt-4">
            <button 
              onClick={() => setCurrentStep('url')}
              className="btn-secondary mr-2"
            >
              Back
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Personal Information */}
      {currentStep === 'personal' && (
        <div className="card animate-fade-in">
          <h2 className="text-xl font-semibold mb-4">Step 3: Personal Information</h2>
          <PersonalInfoForm onSubmit={handlePersonalInfoSubmit} />
          <div className="mt-4">
            <button 
              onClick={() => setCurrentStep('resume')}
              className="btn-secondary mr-2"
            >
              Back
            </button>
          </div>
        </div>
      )}

      {/* Step 4: Review and Submit */}
      {currentStep === 'submit' && (
        <div className="card animate-fade-in">
          <h2 className="text-xl font-semibold mb-4">Step 4: Review and Submit</h2>
          
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium mb-2">Job URL</h3>
              <p className="text-gray-600 break-all">{jobUrl}</p>
            </div>

            <div>
              <h3 className="text-lg font-medium mb-2">Resume Information</h3>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">
                  Skills: {resumeData?.skills?.join(', ') || 'None detected'}
                </p>
                <p className="text-sm text-gray-600">
                  Experience: {resumeData?.work_experience?.length || 0} positions
                </p>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-medium mb-2">Personal Information</h3>
              <div className="bg-gray-50 p-4 rounded-lg">
                <p className="text-sm text-gray-600">
                  Name: {personalInfo?.first_name} {personalInfo?.last_name}
                </p>
                <p className="text-sm text-gray-600">
                  Email: {personalInfo?.email}
                </p>
              </div>
            </div>
          </div>

          <div className="mt-6 flex space-x-4">
            <button 
              onClick={() => setCurrentStep('personal')}
              className="btn-secondary"
            >
              Back
            </button>
            <button 
              onClick={handleStartApplication}
              className="btn-primary"
              disabled={applicationStatus.status === 'processing'}
            >
              {applicationStatus.status === 'processing' ? (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Processing...</span>
                </div>
              ) : (
                'Start Application'
              )}
            </button>
          </div>

          {applicationStatus.status === 'error' && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center space-x-2">
                <AlertCircle className="h-5 w-5 text-red-500" />
                <span className="text-red-700">{applicationStatus.message}</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Reset Button */}
      {currentStep !== 'url' && (
        <div className="mt-8 text-center">
          <button 
            onClick={resetForm}
            className="text-gray-500 hover:text-gray-700 text-sm"
          >
            Start Over
          </button>
        </div>
      )}
    </div>
  );
};

export default JobApplicationForm; 