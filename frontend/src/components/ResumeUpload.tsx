import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, AlertCircle, CheckCircle, Loader } from 'lucide-react';
import { api } from '../services/api';

interface ResumeUploadProps {
  onUpload: (data: any) => void;
}

const ResumeUpload: React.FC<ResumeUploadProps> = ({ onUpload }) => {
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [resumeData, setResumeData] = useState<any>(null);
  const [errorMessage, setErrorMessage] = useState('');

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploadedFile(file);
    setUploadStatus('uploading');
    setErrorMessage('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await api.post('/api/parse-resume', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResumeData(response.data);
      setUploadStatus('success');
      onUpload(response.data);
    } catch (error: any) {
      setUploadStatus('error');
      setErrorMessage(error.response?.data?.detail || 'Failed to parse resume');
    }
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
    },
    multiple: false,
  });

  const resetUpload = () => {
    setUploadedFile(null);
    setResumeData(null);
    setUploadStatus('idle');
    setErrorMessage('');
  };

  return (
    <div className="space-y-4">
      {uploadStatus === 'idle' && (
        <div
          {...getRootProps()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragActive
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
          }`}
        >
          <input {...getInputProps()} />
          <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <p className="text-lg font-medium text-gray-900 mb-2">
            {isDragActive ? 'Drop your resume here' : 'Upload your resume'}
          </p>
          <p className="text-gray-500 mb-4">
            Drag and drop your resume here, or click to select a file
          </p>
          <p className="text-sm text-gray-400">
            Supports PDF, DOC, and DOCX files
          </p>
        </div>
      )}

      {uploadStatus === 'uploading' && (
        <div className="border-2 border-dashed border-primary-300 bg-primary-50 rounded-lg p-8 text-center">
          <Loader className="mx-auto h-12 w-12 text-primary-500 animate-spin mb-4" />
          <p className="text-lg font-medium text-gray-900 mb-2">
            Processing your resume...
          </p>
          <p className="text-gray-500">
            Extracting information from {uploadedFile?.name}
          </p>
        </div>
      )}

      {uploadStatus === 'success' && resumeData && (
        <div className="space-y-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span className="text-green-700 font-medium">
                Resume uploaded successfully!
              </span>
            </div>
            <p className="text-sm text-green-600 mt-1">
              {uploadedFile?.name}
            </p>
          </div>

          <div className="card">
            <h3 className="text-lg font-medium mb-4">Extracted Information</h3>
            
            <div className="space-y-4">
              {resumeData.contact_info && Object.keys(resumeData.contact_info).length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Contact Information</h4>
                  <div className="bg-gray-50 p-3 rounded">
                    {resumeData.contact_info.name && (
                      <p className="text-sm text-gray-600">Name: {resumeData.contact_info.name}</p>
                    )}
                    {resumeData.contact_info.email && (
                      <p className="text-sm text-gray-600">Email: {resumeData.contact_info.email}</p>
                    )}
                    {resumeData.contact_info.phone && (
                      <p className="text-sm text-gray-600">Phone: {resumeData.contact_info.phone}</p>
                    )}
                  </div>
                </div>
              )}

              {resumeData.skills && resumeData.skills.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {resumeData.skills.map((skill: string, index: number) => (
                      <span
                        key={index}
                        className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded-full"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {resumeData.work_experience && resumeData.work_experience.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Work Experience</h4>
                  <div className="space-y-2">
                    {resumeData.work_experience.slice(0, 3).map((job: any, index: number) => (
                      <div key={index} className="bg-gray-50 p-3 rounded">
                        <p className="text-sm font-medium text-gray-800">
                          {job.position} at {job.company}
                        </p>
                        <p className="text-xs text-gray-600">
                          {job.start_date} - {job.end_date || 'Present'}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {resumeData.education && resumeData.education.length > 0 && (
                <div>
                  <h4 className="font-medium text-gray-700 mb-2">Education</h4>
                  <div className="space-y-2">
                    {resumeData.education.slice(0, 2).map((edu: any, index: number) => (
                      <div key={index} className="bg-gray-50 p-3 rounded">
                        <p className="text-sm font-medium text-gray-800">
                          {edu.degree} in {edu.field}
                        </p>
                        <p className="text-xs text-gray-600">
                          {edu.institution} ({edu.graduation_year})
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <button
              onClick={resetUpload}
              className="mt-4 text-sm text-gray-500 hover:text-gray-700"
            >
              Upload different resume
            </button>
          </div>
        </div>
      )}

      {uploadStatus === 'error' && (
        <div className="space-y-4">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <span className="text-red-700 font-medium">
                Failed to process resume
              </span>
            </div>
            <p className="text-sm text-red-600 mt-1">
              {errorMessage}
            </p>
          </div>

          <button
            onClick={resetUpload}
            className="btn-secondary"
          >
            Try Again
          </button>
        </div>
      )}
    </div>
  );
};

export default ResumeUpload; 