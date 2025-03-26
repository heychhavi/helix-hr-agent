# Helix HR Agent

A modern AI-powered recruiting outreach platform that helps HR professionals create and manage personalized outreach sequences through an intuitive chat interface.

## Features

- 🤖 AI-powered chat interface for creating outreach sequences
- 📝 Dynamic workspace for real-time sequence editing
- 🔄 Live updates between chat and workspace
- 💾 Persistent storage of sequences and preferences
- 🎨 Modern, responsive UI

## Tech Stack

- Frontend: React + TypeScript
- Backend: Flask + Python
- Database: PostgreSQL
- AI: OpenAI Assistants API
- Real-time Updates: Socket.IO

## Setup Instructions

### Prerequisites

- Node.js (v16 or higher)
- Python 3.8+
- PostgreSQL
- OpenAI API key

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
flask run
```

### Database Setup

1. Create a PostgreSQL database
2. Update the database connection string in `backend/.env`
3. Run migrations:
```bash
cd backend
flask db upgrade
```

## Environment Variables

Create a `.env` file in the backend directory with:

```
OPENAI_API_KEY=your_api_key
DATABASE_URL=postgresql://user:password@localhost:5432/helix
FLASK_SECRET_KEY=your_secret_key
```

## Development

- Frontend runs on: http://localhost:3000
- Backend runs on: http://localhost:5000
- API documentation available at: http://localhost:5000/api/docs 