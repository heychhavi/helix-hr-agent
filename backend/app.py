from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import logging
import os
from ai import RecruitingAI
from dotenv import load_dotenv
from response_handler import HelixResponseHandler
import eventlet
from models import db, EmailSequence, Conversation
from config import config

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config['development'])

# Configure CORS
CORS(app, resources={r"/*": {"origins": app.config['CORS_ALLOWED_ORIGINS']}})
db.init_app(app)
socketio = SocketIO(
    app,
    cors_allowed_origins=app.config['CORS_ALLOWED_ORIGINS'],
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

# Create database tables
with app.app_context():
    db.create_all()
    logging.info("Database tables created successfully")

@app.route('/')
def index():
    return 'Helix Recruiting Assistant API'

@app.route('/api/test-db')
def test_db():
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        
        # Get table information
        email_sequences_count = EmailSequence.query.count()
        conversations_count = Conversation.query.count()
        
        return jsonify({
            'status': 'success',
            'message': 'Database connection successful',
            'tables': {
                'email_sequences': {
                    'exists': True,
                    'count': email_sequences_count
                },
                'conversations': {
                    'exists': True,
                    'count': conversations_count
                }
            }
        })
    except Exception as e:
        logging.error(f"Database connection error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Database connection failed: {str(e)}'
        }), 500

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
    """Handle client connection."""
    logging.info("Client connected")
    socketio.emit('connection_status', {'status': 'connected'}, room=request.sid)

@socketio.on('test_connection')
def handle_test_connection(data):
    """Handle test connection."""
    logging.info(f"Received test connection: {data}")
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
        sequence_generated = data.get('sequence_generated', False)
        
        logging.info(f"Received chat message: {message}")
        logging.info(f"Current messages: {messages}")
        logging.info(f"Selected persona: {persona}")
        logging.info(f"Sequence generated: {sequence_generated}")
        
        # Save conversation to database
        if messages:
            conversation = Conversation(messages=messages, persona=persona)
            db.session.add(conversation)
            db.session.commit()
        
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
            
            # If sequence was already generated, handle feedback
            if sequence_generated:
                logging.info("Handling post-sequence feedback")
                feedback_response = ai_handler.handle_sequence_feedback(message)
                socketio.emit('chat_message', {
                    'role': 'assistant',
                    'content': feedback_response
                }, room=request.sid)
                return
                
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
                
                # Save sequence to database
                email_sequence = EmailSequence(
                    persona=persona,
                    tone=data.get('tone', 'professional'),
                    sequence_type=data.get('sequenceType', 'passive'),
                    content=sequence
                )
                db.session.add(email_sequence)
                db.session.commit()
                
                socketio.emit('sequence_update', {'content': sequence}, room=request.sid)
                
                # Send follow-up message asking for feedback
                feedback_prompt = "How's that sequence? I can help you refine it further - would you like me to make any specific improvements? For example:\n1. Make it more technical\n2. Add more specific examples\n3. Adjust the tone\n4. Make it more concise\n5. Add more personalization"
                socketio.emit('chat_message', {
                    'role': 'assistant',
                    'content': feedback_prompt
                }, room=request.sid)
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
            
            # Save enhanced sequence
            email_sequence = EmailSequence(
                persona=data.get('persona', 'corporate_pro'),
                tone=tone,
                sequence_type=sequence_type,
                content=enhanced_sequence
            )
            db.session.add(email_sequence)
            db.session.commit()
            
            socketio.emit('sequence_update', {'content': enhanced_sequence}, room=request.sid)
            
        elif action == 'refresh':
            # Generate a new sequence with current settings
            sequence = ai_handler.generate_email_sequence(role_info, tone)
            
            # Save new sequence
            email_sequence = EmailSequence(
                persona=data.get('persona', 'corporate_pro'),
                tone=tone,
                sequence_type=sequence_type,
                content=sequence
            )
            db.session.add(email_sequence)
            db.session.commit()
            
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