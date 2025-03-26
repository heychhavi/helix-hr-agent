from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import os
from datetime import datetime
from ai import RecruitingAI
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure database - use SQLite instead of PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///helix.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev')

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
socketio = SocketIO(
    app, 
    cors_allowed_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    logger=True, 
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25
)

# Initialize AI
try:
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key or api_key == "your_google_api_key_here":
        logger.warning("GOOGLE_API_KEY environment variable is not properly set, using placeholder")
        api_key = "PLACEHOLDER_KEY"
    ai = RecruitingAI(api_key)
    logger.info("Successfully initialized RecruitingAI")
except Exception as e:
    logger.error(f"Failed to initialize RecruitingAI: {str(e)}")
    raise

# Models
class Sequence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Routes
@app.route('/')
def index():
    return "Helix HR Agent API is running!"

@app.route('/api/health')
def health_check():
    return jsonify({"status": "ok", "message": "API is running"})

@app.route('/api/sequences', methods=['GET'])
def get_sequences():
    sequences = Sequence.query.all()
    return jsonify([{
        'id': seq.id,
        'title': seq.title,
        'content': seq.content,
        'created_at': seq.created_at.isoformat(),
        'updated_at': seq.updated_at.isoformat()
    } for seq in sequences])

@app.route('/api/sequences', methods=['POST'])
def create_sequence():
    data = request.json
    sequence = Sequence(
        title=data['title'],
        content=data['content']
    )
    db.session.add(sequence)
    db.session.commit()
    return jsonify({
        'id': sequence.id,
        'title': sequence.title,
        'content': sequence.content,
        'created_at': sequence.created_at.isoformat(),
        'updated_at': sequence.updated_at.isoformat()
    }), 201

@app.route('/api/sequences/<int:sequence_id>', methods=['PUT'])
def update_sequence(sequence_id):
    sequence = Sequence.query.get_or_404(sequence_id)
    data = request.json
    sequence.title = data.get('title', sequence.title)
    sequence.content = data.get('content', sequence.content)
    db.session.commit()
    return jsonify({
        'id': sequence.id,
        'title': sequence.title,
        'content': sequence.content,
        'created_at': sequence.created_at.isoformat(),
        'updated_at': sequence.updated_at.isoformat()
    })

# Socket.IO events
@socketio.on('connect')
def handle_connect():
    logger.info("Client connected")
    emit('chat_message', {
        'role': 'assistant',
        'content': "Hello! I'm your HR recruiting assistant. How can I help you today?"
    })

@socketio.on('disconnect')
def handle_disconnect():
    logger.info("Client disconnected")

@socketio.on('chat_message')
def handle_chat_message(data):
    try:
        message = data.get('message', '')
        messages = data.get('messages', [])
        
        logger.info(f"Received chat message: '{message}', history length: {len(messages)}")
        
        # Generate AI response
        ai_response = ai.generate_response(messages)
        logger.info(f"Generated AI response: '{ai_response[:30]}...'")
        
        # Emit the response back to the client
        emit('chat_message', {
            'role': 'assistant',
            'content': ai_response
        })
        
        # If we have enough information, generate a sequence
        if len(messages) >= 4:
            logger.info("Generating sequence from conversation context")
            role_info = {
                'role': messages[0].get('content', ''),
                'target_audience': messages[1].get('content', ''),
                'requirements': messages[2].get('content', ''),
                'company_culture': messages[3].get('content', '')
            }
            sequence = ai.generate_sequence(role_info)
            emit('sequence_update', {'content': sequence})
            logger.info(f"Sequence generated and sent to client: '{sequence[:30]}...'")
    except Exception as e:
        logger.error(f"Error handling chat message: {str(e)}")
        emit('chat_message', {
            'role': 'assistant',
            'content': f"I apologize, but I encountered an error: {str(e)}"
        })

if __name__ == '__main__':
    try:
        # Make sure database tables exist
        with app.app_context():
            db.create_all()
            logger.info("Database tables created")
        
        # Start the Socket.IO server
        logger.info("Starting SocketIO server on port 5001")
        socketio.run(app, host='0.0.0.0', port=5001, debug=True)
    except Exception as e:
        logger.error(f"Error starting server: {str(e)}")
        raise 