import React, { useState, useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { Plus, Trash2 } from 'lucide-react';
import { getPersonalInfo, updatePersonalInfo } from '../services/api';

interface PersonalInfoFormProps {
  onSubmit: (data: any) => void;
}

interface Education {
  degree: string;
  field: string;
  institution: string;
  graduation_year: string;
  gpa?: string;
}

interface WorkExperience {
  company: string;
  position: string;
  start_date: string;
  end_date?: string;
  description: string;
}

interface DiversityInfo {
  veteran_status: string;
  disability_status: string;
  race_ethnicity: string;
  gender: string;
}

interface FormData {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  address: {
    street: string;
    city: string;
    state: string;
    zip_code: string;
    country: string;
  };
  education: Education[];
  work_history: WorkExperience[];
  skills: string[];
  diversity_info: DiversityInfo;
}

const PersonalInfoForm: React.FC<PersonalInfoFormProps> = ({ onSubmit }) => {
  const { register, handleSubmit, control, watch, setValue, formState: { errors }, reset } = useForm<FormData>({
    defaultValues: {
      address: {
        country: 'USA'
      },
      education: [],
      work_history: [],
      skills: [],
      diversity_info: {
        veteran_status: 'No',
        disability_status: 'No',
        race_ethnicity: 'Prefer not to say',
        gender: 'Prefer not to say'
      }
    }
  });

  const [skillInput, setSkillInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [saveMsg, setSaveMsg] = useState('');

  // Auto-load personal info if logged in
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setLoading(true);
      getPersonalInfo()
        .then(res => {
          if (res.data) {
            reset(res.data);
          }
        })
        .finally(() => setLoading(false));
    }
  }, [reset]);

  const addEducation = () => {
    const currentEducation = watch('education');
    setValue('education', [...currentEducation, {
      degree: '',
      field: '',
      institution: '',
      graduation_year: '',
      gpa: ''
    }]);
  };

  const removeEducation = (index: number) => {
    const currentEducation = watch('education');
    setValue('education', currentEducation.filter((_, i) => i !== index));
  };

  const addWorkExperience = () => {
    const currentWork = watch('work_history');
    setValue('work_history', [...currentWork, {
      company: '',
      position: '',
      start_date: '',
      end_date: '',
      description: ''
    }]);
  };

  const removeWorkExperience = (index: number) => {
    const currentWork = watch('work_history');
    setValue('work_history', currentWork.filter((_, i) => i !== index));
  };

  const addSkill = () => {
    if (skillInput.trim()) {
      const currentSkills = watch('skills');
      setValue('skills', [...currentSkills, skillInput.trim()]);
      setSkillInput('');
    }
  };

  const removeSkill = (index: number) => {
    const currentSkills = watch('skills');
    setValue('skills', currentSkills.filter((_, i) => i !== index));
  };

  const onFormSubmit = async (data: FormData) => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        await updatePersonalInfo(data);
        setSaveMsg('Personal info saved!');
        setTimeout(() => setSaveMsg(''), 2000);
      } catch {
        setSaveMsg('Failed to save info');
      }
    }
    onSubmit(data);
  };

  return (
    <>
      {loading && <div className="text-center text-gray-500">Loading your info...</div>}
      {saveMsg && <div className="text-center text-green-600 mb-2">{saveMsg}</div>}
      <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
        {/* Basic Information */}
        <div className="card">
          <h3 className="text-lg font-medium mb-4">Basic Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="form-group">
              <label htmlFor="first_name" className="form-label">First Name</label>
              <input
                {...register('first_name', { required: 'First name is required' })}
                type="text"
                className="input-field"
              />
              {errors.first_name && (
                <p className="error-message">{errors.first_name.message}</p>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="last_name" className="form-label">Last Name</label>
              <input
                {...register('last_name', { required: 'Last name is required' })}
                type="text"
                className="input-field"
              />
              {errors.last_name && (
                <p className="error-message">{errors.last_name.message}</p>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="email" className="form-label">Email</label>
              <input
                {...register('email', { 
                  required: 'Email is required',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Invalid email address'
                  }
                })}
                type="email"
                className="input-field"
              />
              {errors.email && (
                <p className="error-message">{errors.email.message}</p>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="phone" className="form-label">Phone</label>
              <input
                {...register('phone', { required: 'Phone number is required' })}
                type="tel"
                className="input-field"
              />
              {errors.phone && (
                <p className="error-message">{errors.phone.message}</p>
              )}
            </div>
          </div>
        </div>

        {/* Address */}
        <div className="card">
          <h3 className="text-lg font-medium mb-4">Address</h3>
          <div className="space-y-4">
            <div className="form-group">
              <label htmlFor="address.street" className="form-label">Street Address</label>
              <input
                {...register('address.street', { required: 'Street address is required' })}
                type="text"
                className="input-field"
              />
              {errors.address?.street && (
                <p className="error-message">{errors.address.street.message}</p>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="form-group">
                <label htmlFor="address.city" className="form-label">City</label>
                <input
                  {...register('address.city', { required: 'City is required' })}
                  type="text"
                  className="input-field"
                />
                {errors.address?.city && (
                  <p className="error-message">{errors.address.city.message}</p>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="address.state" className="form-label">State</label>
                <input
                  {...register('address.state', { required: 'State is required' })}
                  type="text"
                  className="input-field"
                />
                {errors.address?.state && (
                  <p className="error-message">{errors.address.state.message}</p>
                )}
              </div>

              <div className="form-group">
                <label htmlFor="address.zip_code" className="form-label">ZIP Code</label>
                <input
                  {...register('address.zip_code', { required: 'ZIP code is required' })}
                  type="text"
                  className="input-field"
                />
                {errors.address?.zip_code && (
                  <p className="error-message">{errors.address.zip_code.message}</p>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Education */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium">Education</h3>
            <button
              type="button"
              onClick={addEducation}
              className="flex items-center space-x-1 text-primary-600 hover:text-primary-700 text-sm"
            >
              <Plus className="h-4 w-4" />
              <span>Add Education</span>
            </button>
          </div>

          <Controller
            name="education"
            control={control}
            render={({ field }) => (
              <div className="space-y-4">
                {field.value.map((_, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="font-medium">Education #{index + 1}</h4>
                      <button
                        type="button"
                        onClick={() => removeEducation(index)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="form-group">
                        <label className="form-label">Degree</label>
                        <input
                          {...register(`education.${index}.degree` as const)}
                          type="text"
                          className="input-field"
                          placeholder="e.g., Bachelor of Science"
                        />
                      </div>

                      <div className="form-group">
                        <label className="form-label">Field of Study</label>
                        <input
                          {...register(`education.${index}.field` as const)}
                          type="text"
                          className="input-field"
                          placeholder="e.g., Computer Science"
                        />
                      </div>

                      <div className="form-group">
                        <label className="form-label">Institution</label>
                        <input
                          {...register(`education.${index}.institution` as const)}
                          type="text"
                          className="input-field"
                          placeholder="University name"
                        />
                      </div>

                      <div className="form-group">
                        <label className="form-label">Graduation Year</label>
                        <input
                          {...register(`education.${index}.graduation_year` as const)}
                          type="text"
                          className="input-field"
                          placeholder="YYYY"
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          />
        </div>

        {/* Work History */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium">Work History</h3>
            <button
              type="button"
              onClick={addWorkExperience}
              className="flex items-center space-x-1 text-primary-600 hover:text-primary-700 text-sm"
            >
              <Plus className="h-4 w-4" />
              <span>Add Work Experience</span>
            </button>
          </div>

          <Controller
            name="work_history"
            control={control}
            render={({ field }) => (
              <div className="space-y-4">
                {field.value.map((_, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="font-medium">Work Experience #{index + 1}</h4>
                      <button
                        type="button"
                        onClick={() => removeWorkExperience(index)}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="form-group">
                        <label className="form-label">Company</label>
                        <input
                          {...register(`work_history.${index}.company` as const)}
                          type="text"
                          className="input-field"
                          placeholder="Company name"
                        />
                      </div>

                      <div className="form-group">
                        <label className="form-label">Position</label>
                        <input
                          {...register(`work_history.${index}.position` as const)}
                          type="text"
                          className="input-field"
                          placeholder="Job title"
                        />
                      </div>

                      <div className="form-group">
                        <label className="form-label">Start Date</label>
                        <input
                          {...register(`work_history.${index}.start_date` as const)}
                          type="month"
                          className="input-field"
                        />
                      </div>

                      <div className="form-group">
                        <label className="form-label">End Date</label>
                        <input
                          {...register(`work_history.${index}.end_date` as const)}
                          type="month"
                          className="input-field"
                          placeholder="Leave empty if current"
                        />
                      </div>
                    </div>

                    <div className="form-group mt-4">
                      <label className="form-label">Description</label>
                      <textarea
                        {...register(`work_history.${index}.description` as const)}
                        className="input-field"
                        rows={3}
                        placeholder="Describe your responsibilities and achievements"
                      />
                    </div>
                  </div>
                ))}
              </div>
            )}
          />
        </div>

        {/* Skills */}
        <div className="card">
          <h3 className="text-lg font-medium mb-4">Skills</h3>
          <div className="space-y-4">
            <div className="flex space-x-2">
              <input
                type="text"
                value={skillInput}
                onChange={(e) => setSkillInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                placeholder="Add a skill"
                className="input-field flex-1"
              />
              <button
                type="button"
                onClick={addSkill}
                className="btn-primary"
              >
                Add
              </button>
            </div>

            <Controller
              name="skills"
              control={control}
              render={({ field }) => (
                <div className="flex flex-wrap gap-2">
                  {field.value.map((skill, index) => (
                    <span
                      key={index}
                      className="flex items-center space-x-1 px-3 py-1 bg-primary-100 text-primary-700 rounded-full text-sm"
                    >
                      <span>{skill}</span>
                      <button
                        type="button"
                        onClick={() => removeSkill(index)}
                        className="text-primary-500 hover:text-primary-700"
                      >
                        ×
                      </button>
                    </span>
                  ))}
                </div>
              )}
            />
          </div>
        </div>

        {/* Diversity Information */}
        <div className="card">
          <h3 className="text-lg font-medium mb-4">Diversity Information (Optional)</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="form-group">
              <label className="form-label">Veteran Status</label>
              <select
                {...register('diversity_info.veteran_status')}
                className="input-field"
              >
                <option value="No">No</option>
                <option value="Yes">Yes</option>
                <option value="Prefer not to say">Prefer not to say</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Disability Status</label>
              <select
                {...register('diversity_info.disability_status')}
                className="input-field"
              >
                <option value="No">No</option>
                <option value="Yes">Yes</option>
                <option value="Prefer not to say">Prefer not to say</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Race/Ethnicity</label>
              <select
                {...register('diversity_info.race_ethnicity')}
                className="input-field"
              >
                <option value="Prefer not to say">Prefer not to say</option>
                <option value="White">White</option>
                <option value="Black or African American">Black or African American</option>
                <option value="Hispanic or Latino">Hispanic or Latino</option>
                <option value="Asian">Asian</option>
                <option value="Native American">Native American</option>
                <option value="Pacific Islander">Pacific Islander</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div className="form-group">
              <label className="form-label">Gender</label>
              <select
                {...register('diversity_info.gender')}
                className="input-field"
              >
                <option value="Prefer not to say">Prefer not to say</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Non-binary">Non-binary</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <button type="submit" className="btn-primary">
            Continue to Review
          </button>
        </div>
      </form>
    </>
  );
};

export default PersonalInfoForm; 