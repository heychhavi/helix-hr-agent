# Helix HR Agent
## Demo : https://www.loom.com/share/4654ec3d734a41eea8b5e1ecb0c7bd9c?sid=7b827805-7c6f-4550-994a-d13a796886ba
A modern AI-powered recruiting outreach platform that helps HR professionals create and manage personalized outreach sequences through an intuitive chat interface.

![Helix HR Agent](https://img.shields.io/badge/Helix-HR%20Agent-blue)

## 📌 Overview

Helix HR Agent is a prototype of an AI-powered recruiting tool that helps HR professionals create personalized outreach sequences through a chat-driven interface. The application uses AI (Google's Gemini) to analyze the conversation and generate customized recruiting messages.

## ✨ Features

- 🤖 **AI-powered chat interface**: Conversational interface for creating outreach sequences
- 📝 **Dynamic workspace**: Real-time sequence editing with a live preview
- 🔄 **Live updates**: Instant reflection of changes between chat and workspace
- 💾 **Persistent storage**: Sequences and preferences stored in a database
- 🎨 **Modern UI**: Clean, responsive interface using Material UI

## 🛠️ Tech Stack

- **Frontend**: React + TypeScript, Material UI
- **Backend**: Flask + Python
- **Database**: SQLite (easy to replace with PostgreSQL)
- **AI**: Google Gemini API
- **Real-time Updates**: Socket.IO

## 🚀 Getting Started

### Prerequisites

- Node.js (v16 or higher)
- Python 3.8+
- Google API key for Gemini (optional, falls back to mock data)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/heychhavi/helix-hr-agent.git
   cd helix-hr-agent
   ```

2. **Setup with the provided script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Configure environment variables**
   - Create a `.env` file in the `backend` directory:
   ```
   GOOGLE_API_KEY=your_google_api_key_here
   FLASK_SECRET_KEY=your_secret_key_here
   ```

### Running the Application

1. **Start the backend**
   ```bash
   cd backend
   source venv/bin/activate
   python app.py
   ```

2. **Start the frontend (in a separate terminal)**
   ```bash
   cd frontend
   npm start
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5001

## 🧪 How to Use

1. **Start a conversation**: Begin by greeting the AI assistant
2. **Provide role information**: When prompted, share details about:
   - The role you're recruiting for
   - Target audience/candidates
   - Key requirements or skills needed
   - Company culture
3. **Review and edit**: After collecting information, the AI will generate a sequence in the workspace
4. **Customize**: Edit the generated sequence directly in the workspace

## 📚 Project Structure

```
helix-hr-agent/
├── backend/               # Flask server
│   ├── app.py             # Main application file
│   ├── ai.py              # AI integration module
│   └── requirements.txt   # Python dependencies
├── frontend/              # React + TypeScript
│   ├── public/            # Static files
│   ├── src/               # Source code
│   │   ├── components/    # React components
│   │   ├── App.tsx        # Main App component
│   │   └── index.tsx      # Entry point
│   ├── package.json       # NPM dependencies
│   └── tsconfig.json      # TypeScript configuration
└── setup.sh               # Setup script
```

## 📝 License

This project is for demonstration purposes. Feel free to use and modify as needed.

## 🙏 Acknowledgements

- Google Gemini API for AI capabilities
- Material UI for the frontend components
- Socket.IO for real-time communication 
