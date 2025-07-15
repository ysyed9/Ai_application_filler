# AI Job Application Auto-Filler

An intelligent web application that automatically fills out job applications using AI and web automation. Upload your resume, provide your personal information, and let AI handle the rest!

## ✨ Features

- **Smart Form Detection**: Automatically detects and fills job application forms
- **Resume Parsing**: Extracts information from uploaded resumes (PDF, DOC, DOCX)
- **Personal Info Management**: Stores and auto-fills personal information
- **Intelligent Responses**: Uses LLMs to generate appropriate answers for open-ended questions
- **Diversity & Military Questions**: Handles special sections like veteran status, disability, etc.
- **One-Click Submission**: Automatically submits applications when possible
- **Real-time Progress**: Track application status with live updates
- **Free Tier Compatible**: Works with free LLM APIs and local development

## 🛠️ Tech Stack

- **Frontend**: React + TypeScript + Tailwind CSS
- **Backend**: FastAPI + Python
- **Automation**: Playwright
- **AI**: LLM integration (OpenAI, Hugging Face, or fallback responses)
- **Database**: SQLite (local storage)

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai-job-application-filler
   ```

2. **Run the setup script**
   ```bash
   python setup.py
   ```

3. **Start the application**
   ```bash
   python start.py
   ```

4. **Open your browser**
   Navigate to http://localhost:3000

### Manual Installation

If you prefer to install manually:

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt
playwright install chromium
python main.py
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## 📖 Usage

### Step 1: Enter Job URL
Paste the URL of the job application form you want to fill out.

### Step 2: Upload Resume
Upload your resume (PDF, DOC, or DOCX). The AI will extract:
- Contact information
- Work experience
- Education
- Skills
- Certifications

### Step 3: Personal Information
Fill in your personal details:
- Basic information (name, email, phone)
- Address
- Education history
- Work experience
- Skills
- Diversity information (optional)

### Step 4: Review and Submit
Review all information and start the automated application process.

### Step 5: Monitor Progress
Track the real-time progress of your application:
- Form detection
- Field filling
- Submission status

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Optional: LLM API Keys
OPENAI_API_KEY=your_openai_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# Database
DATABASE_URL=sqlite+aiosqlite:///./job_applications.db

# Server
HOST=0.0.0.0
PORT=8000
```

### Free Tier Setup

The application works without any API keys using fallback responses. For better results:

1. **OpenAI API** (Recommended)
   - Sign up at https://openai.com
   - Get your API key
   - Add to `backend/.env`

2. **Hugging Face API** (Alternative)
   - Sign up at https://huggingface.co
   - Get your API key
   - Add to `backend/.env`

## 🏗️ Project Structure

```
├── backend/                 # FastAPI backend
│   ├── main.py             # Main application
│   ├── models.py           # Data models
│   ├── database.py         # Database operations
│   ├── resume_parser.py    # Resume parsing
│   ├── form_filler.py      # Playwright automation
│   ├── llm_service.py      # LLM integration
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   └── App.tsx        # Main app
│   ├── package.json        # Node dependencies
│   └── tailwind.config.js  # Tailwind config
├── setup.py               # Setup script
├── start.py               # Startup script
└── README.md              # This file
```

## 🔍 How It Works

### 1. Form Detection
- Uses Playwright to navigate to job application URLs
- Automatically detects form fields using CSS selectors
- Maps fields to personal information categories

### 2. Resume Parsing
- Extracts text from PDF/DOC files
- Uses LLM to structure and categorize information
- Falls back to regex-based parsing if LLM unavailable

### 3. Intelligent Filling
- Maps personal info to detected form fields
- Uses LLM to generate responses for open-ended questions
- Handles diversity and military questions appropriately

### 4. Form Submission
- Automatically clicks submit buttons
- Verifies successful submission
- Provides real-time status updates

## 🛡️ Security & Privacy

- **Local Processing**: All data processed locally
- **No Data Storage**: Personal info not stored permanently
- **Secure APIs**: Uses HTTPS for external API calls
- **Optional Keys**: Works without external API keys

## 🐛 Troubleshooting

### Common Issues

1. **Playwright Browser Not Found**
   ```bash
   cd backend
   playwright install chromium
   ```

2. **Port Already in Use**
   - Backend: Change port in `backend/main.py`
   - Frontend: Change port in `frontend/package.json`

3. **API Key Errors**
   - Check your API keys in `backend/.env`
   - Or remove keys to use fallback responses

4. **Form Detection Issues**
   - Some forms may have anti-bot protection
   - Try different job application sites
   - Check browser console for errors

### Debug Mode

Enable debug mode for detailed logging:

```bash
# Backend
cd backend
python main.py --debug

# Frontend
cd frontend
REACT_APP_DEBUG=true npm start
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- [Playwright](https://playwright.dev/) for web automation
- [FastAPI](https://fastapi.tiangolo.com/) for the backend
- [React](https://reactjs.org/) for the frontend
- [Tailwind CSS](https://tailwindcss.com/) for styling

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation

---

**Note**: This tool is for educational purposes. Always review applications before submission and ensure compliance with job application terms of service. 