from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import logging
import os
from ai import RecruitingAI
from dotenv import load_dotenv
from response_handler import HelixResponseHandler
import eventlet
eventlet.monkey_patch()

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure CORS
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000", "http://localhost:3001", "http://10.0.0.209:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True
    }
})
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'helix_recruiting_assistant_secret_2024')

# Initialize SocketIO with CORS settings
socketio = SocketIO(
    app,
    cors_allowed_origins=["http://localhost:3000", "http://localhost:3001", "http://10.0.0.209:3000"],
    async_mode='eventlet',
    ping_timeout=60,
    ping_interval=25,
    logger=True,
    engineio_logger=True
)

# Initialize AI component
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    logger.warning("GOOGLE_API_KEY environment variable is not properly set")
ai = RecruitingAI(api_key=api_key)

logger.info("Successfully initialized RecruitingAI")
logger.info("Starting SocketIO server on port 3002")

# Initialize AI handler
ai_handler = HelixResponseHandler()
logger.info("Initialized HelixResponseHandler")

@app.route('/')
def index():
    return 'Helix Recruiting Assistant API'

@app.route('/api/personas')
def get_personas():
    return jsonify([
        {
            "id": "friendly_recruiter",
            "name": "Friendly Recruiter",
            "description": "Warm and approachable communication style"
        },
        {
            "id": "professional_recruiter",
            "name": "Professional Recruiter",
            "description": "Formal and business-oriented communication"
        },
        {
            "id": "founder_recruiter",
            "name": "Founder Recruiter",
            "description": "Direct and passionate about the company mission"
        }
    ])

@socketio.on('connect')
def handle_connect():
    logging.info('Client connected')
    socketio.emit('connection_status', {'status': 'connected'}, room=request.sid)

@socketio.on('test_connection')
def handle_test_connection(data):
    logging.info(f'Received test connection: {data}')
    socketio.emit('test_response', {'message': 'Test connection successful'}, room=request.sid)

@socketio.on('disconnect')
def handle_disconnect():
    logging.info("Client disconnected")

@socketio.on('chat_message')
def handle_message(data):
    try:
        message = data.get('message', '')
        messages = data.get('messages', [])
        persona = data.get('persona', 'corporate_pro')
        
        logging.info(f"Received chat message: {message}")
        logging.info(f"Current messages: {messages}")
        logging.info(f"Selected persona: {persona}")
        
        # Handle initial message or greeting
        if not messages or len(messages) == 1 or message.lower() in ['hi', 'hello', 'hey']:
            logging.info("Sending persona introduction")
            intro_message = ai_handler.get_persona_intro(persona)
            logging.info(f"Generated intro message: {intro_message}")
            socketio.emit('chat_message', {
                'role': 'assistant',
                'content': intro_message
            }, room=request.sid)
            logging.info("Sent persona introduction")
            return
            
        # For follow-up messages
        if message:
            logging.info("Processing follow-up message")
            # Update conversation state
            ai_handler.update_required_info(message)
            
            # Get next question or generate sequence
            if ai_handler.should_generate_sequence():
                logging.info("Generating sequence")
                response = "Perfect! I have all the information needed to craft a personalized email sequence that aligns with your needs. I'll generate that for you now."
                socketio.emit('chat_message', {
                    'role': 'assistant',
                    'content': response
                }, room=request.sid)
                sequence = ai_handler.generate_email_sequence(messages, persona)
                socketio.emit('sequence_update', {'content': sequence}, room=request.sid)
            else:
                logging.info("Sending follow-up question")
                next_question = ai_handler.get_next_question(persona)
                if next_question:
                    logging.info(f"Generated next question: {next_question}")
                    socketio.emit('chat_message', {
                        'role': 'assistant',
                        'content': next_question
                    }, room=request.sid)
                else:
                    logging.info("No next question available, sending default question")
                    socketio.emit('chat_message', {
                        'role': 'assistant',
                        'content': "Could you tell me more about what makes this role unique?"
                    }, room=request.sid)
            
    except Exception as e:
        logging.error(f"Error processing message: {str(e)}")
        socketio.emit('chat_message', {
            'role': 'assistant',
            'content': 'I apologize, but I encountered an error. Please try again.'
        }, room=request.sid)

@socketio.on('update_tone')
def handle_tone_update(data):
    try:
        content = data.get('content', '')
        tone = data.get('tone', 'professional')
        sequence_type = data.get('sequenceType', 'passive')
        role_info = data.get('roleInfo', [])
        
        # Extract role from messages
        role = None
        for msg in role_info:
            if msg.get('role') == 'user':
                role = ai._extract_role_info(msg.get('content', ''))
                if role:
                    break
        
        if role:
            sequence = ai.generate_sequence(
                role=role,
                tone=tone,
                step_count=3
            )
            socketio.emit('sequence_update', {'content': sequence}, room=request.sid)
            
    except Exception as e:
        logging.error(f"Error updating tone: {str(e)}")
        socketio.emit('error', {'message': 'Error updating tone'}, room=request.sid)

@socketio.on('update_sequence_type')
def handle_sequence_type_update(data):
    try:
        content = data.get('content', '')
        tone = data.get('tone', 'professional')
        sequence_type = data.get('sequenceType', 'passive')
        role_info = data.get('roleInfo', [])
        
        # Extract role from messages
        role = None
        for msg in role_info:
            if msg.get('role') == 'user':
                role = ai._extract_role_info(msg.get('content', ''))
                if role:
                    break
        
        if role:
            sequence = ai.generate_sequence(
                role=role,
                tone=tone,
                step_count=3 if sequence_type == 'passive' else 4
            )
            socketio.emit('sequence_update', {'content': sequence}, room=request.sid)
            
    except Exception as e:
        logging.error(f"Error updating sequence type: {str(e)}")
        socketio.emit('error', {'message': 'Error updating sequence type'}, room=request.sid)

@socketio.on('magic_action')
def handle_magic_action(data):
    try:
        content = data.get('content', '')
        action = data.get('action', '')
        tone = data.get('tone', 'professional')
        sequence_type = data.get('sequenceType', 'passive')
        role_info = data.get('roleInfo', [])
        
        logging.info(f"Handling magic action: {action}")
        
        if action == 'enhance_personalization':
            enhanced_sequence = ai_handler.enhance_personalization(content, role_info)
            socketio.emit('sequence_update', {'content': enhanced_sequence}, room=request.sid)
            
        elif action == 'refresh':
            # Generate a new sequence with current settings
            sequence = ai_handler.generate_email_sequence(role_info, tone)
            socketio.emit('sequence_update', {'content': sequence}, room=request.sid)
            
        elif action == 'download':
            # Just acknowledge the download request
            # The actual download will be handled by the frontend
            socketio.emit('download_ready', {'content': content}, room=request.sid)
            
    except Exception as e:
        logging.error(f"Error applying magic action: {str(e)}")
        socketio.emit('error', {'message': 'Error applying magic action'}, room=request.sid)

@socketio.on('generate_sequence')
def handle_generate_sequence(data):
    try:
        messages = data.get('messages', [])
        tone = data.get('tone', 'professional')
        sequence_type = data.get('sequenceType', 'passive')
        
        # Extract role from messages
        role = None
        for msg in messages:
            if msg.get('role') == 'user':
                role = ai._extract_role_info(msg.get('content', ''))
                if role:
                    break
        
        if role:
            sequence = ai.generate_sequence(
                role=role,
                tone=tone,
                step_count=3 if sequence_type == 'passive' else 4
            )
            socketio.emit('sequence_update', {'content': sequence}, room=request.sid)
        else:
            socketio.emit('error', {'message': 'Could not determine role from conversation'}, room=request.sid)
            
    except Exception as e:
        logging.error(f"Error generating sequence: {str(e)}")
        socketio.emit('error', {'message': 'Error generating sequence'}, room=request.sid)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=3002, debug=True) 