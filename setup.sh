#!/bin/bash

# Create virtual environment for backend
echo "Setting up backend..."
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize frontend
echo "Setting up frontend..."
cd ../frontend
npm install

# Create necessary directories
echo "Creating necessary directories..."
cd ..
mkdir -p backend/migrations
mkdir -p frontend/public

# Create .env file for backend
echo "Creating backend .env file..."
cat > backend/.env << EOL
GOOGLE_API_KEY=your_google_api_key_here
DATABASE_URL=postgresql://localhost/helix
FLASK_SECRET_KEY=your_secret_key_here
EOL

echo "Setup complete! To start the application:"
echo "1. Start the backend: cd backend && source venv/bin/activate && flask run"
echo "2. Start the frontend: cd frontend && npm start" 