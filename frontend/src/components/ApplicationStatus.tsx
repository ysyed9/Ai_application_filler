import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { CheckCircle, AlertCircle, Clock, Play, Check, X } from 'lucide-react';
import { api } from '../services/api';

interface ApplicationStatus {
  status: 'starting' | 'processing' | 'completed' | 'error';
  message: string;
  progress: number;
  details?: any;
}

const ApplicationStatus: React.FC = () => {
  const { appId } = useParams<{ appId: string }>();
  const [status, setStatus] = useState<ApplicationStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!appId) return;

    const fetchStatus = async () => {
      try {
        const response = await api.get(`/api/application-status/${appId}`);
        setStatus(response.data);
      } catch (error) {
        console.error('Error fetching status:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();

    // Poll for status updates if not completed
    const interval = setInterval(async () => {
      if (status?.status === 'completed' || status?.status === 'error') {
        clearInterval(interval);
        return;
      }

      try {
        const response = await api.get(`/api/application-status/${appId}`);
        setStatus(response.data);
      } catch (error) {
        console.error('Error fetching status:', error);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [appId, status?.status]);

  if (loading) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="card text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading application status...</p>
        </div>
      </div>
    );
  }

  if (!status) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="card text-center">
          <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Application Not Found</h2>
          <p className="text-gray-600 mb-4">
            The application with ID {appId} could not be found.
          </p>
          <Link to="/" className="btn-primary">
            Start New Application
          </Link>
        </div>
      </div>
    );
  }

  const getStatusIcon = () => {
    switch (status.status) {
      case 'starting':
        return <Play className="h-8 w-8 text-blue-500" />;
      case 'processing':
        return <Clock className="h-8 w-8 text-yellow-500 animate-pulse" />;
      case 'completed':
        return <CheckCircle className="h-8 w-8 text-green-500" />;
      case 'error':
        return <X className="h-8 w-8 text-red-500" />;
      default:
        return <Clock className="h-8 w-8 text-gray-500" />;
    }
  };

  const getStatusColor = () => {
    switch (status.status) {
      case 'starting':
        return 'text-blue-600';
      case 'processing':
        return 'text-yellow-600';
      case 'completed':
        return 'text-green-600';
      case 'error':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getProgressColor = () => {
    switch (status.status) {
      case 'starting':
        return 'bg-blue-500';
      case 'processing':
        return 'bg-yellow-500';
      case 'completed':
        return 'bg-green-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="card">
        <div className="text-center mb-6">
          <div className="flex justify-center mb-4">
            {getStatusIcon()}
          </div>
          <h2 className={`text-2xl font-semibold mb-2 ${getStatusColor()}`}>
            {status.status === 'starting' && 'Starting Application'}
            {status.status === 'processing' && 'Processing Application'}
            {status.status === 'completed' && 'Application Completed'}
            {status.status === 'error' && 'Application Error'}
          </h2>
          <p className="text-gray-600">{status.message}</p>
        </div>

        {/* Progress Bar */}
        <div className="mb-6">
          <div className="flex justify-between text-sm text-gray-600 mb-2">
            <span>Progress</span>
            <span>{status.progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-500 ${getProgressColor()}`}
              style={{ width: `${status.progress}%` }}
            ></div>
          </div>
        </div>

        {/* Status Details */}
        {status.details && (
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <h3 className="font-medium text-gray-900 mb-2">Details</h3>
            <div className="space-y-2 text-sm text-gray-600">
              {status.details.submitted && (
                <div className="flex items-center space-x-2">
                  <Check className="h-4 w-4 text-green-500" />
                  <span>Application submitted</span>
                </div>
              )}
              {status.details.successful && (
                <div className="flex items-center space-x-2">
                  <Check className="h-4 w-4 text-green-500" />
                  <span>Submission successful</span>
                </div>
              )}
              {status.details.message && (
                <p>{status.details.message}</p>
              )}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex justify-center space-x-4">
          {status.status === 'completed' && (
            <div className="text-center">
              <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Application Submitted Successfully!
              </h3>
              <p className="text-gray-600 mb-4">
                Your job application has been automatically filled and submitted.
              </p>
              <Link to="/" className="btn-primary">
                Start Another Application
              </Link>
            </div>
          )}

          {status.status === 'error' && (
            <div className="text-center">
              <X className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Application Failed
              </h3>
              <p className="text-gray-600 mb-4">
                There was an error processing your application. Please try again.
              </p>
              <div className="space-x-4">
                <Link to="/" className="btn-primary">
                  Try Again
                </Link>
                <button className="btn-secondary">
                  Contact Support
                </button>
              </div>
            </div>
          )}

          {status.status === 'processing' && (
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Processing Your Application
              </h3>
              <p className="text-gray-600 mb-4">
                Please wait while we fill out your job application automatically.
              </p>
              <div className="text-sm text-gray-500">
                This may take a few minutes...
              </div>
            </div>
          )}
        </div>

        {/* Application ID */}
        <div className="mt-6 pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-500 text-center">
            Application ID: {appId}
          </p>
        </div>
      </div>
    </div>
  );
};

export default ApplicationStatus; 