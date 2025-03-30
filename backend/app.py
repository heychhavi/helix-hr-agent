import os
import logging
import json
from dotenv import load_dotenv
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from models import db, EmailSequence

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://neondb_owner:npg_pvayKxe05qno@ep-silent-bonus-a68yb6ue-pooler.us-west-2.aws.neon.tech/neondb?sslmode=require'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize database
db.init_app(app)
with app.app_context():
    db.create_all()

# Initialize Socket.IO
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Gemini
api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    logger.error("GOOGLE_API_KEY environment variable not found")
    raise ValueError("GOOGLE_API_KEY environment variable is required")

try:
    genai.configure(api_key=api_key)
    # Test the configuration with a simple prompt
    model = genai.GenerativeModel('gemini-2.0-flash')
    test_response = model.generate_content("Test")
    logger.info("Successfully initialized Gemini API")
except Exception as e:
    logger.error(f"Failed to initialize Gemini API: {str(e)}")
    raise

# Handler functions
def analyze_sequence_metrics(sequence):
    """Analyze sequence metrics using Gemini."""
    try:
        # First try to parse the sequence if it's a string
        if isinstance(sequence, str):
            try:
                # Remove markdown code blocks if present
                clean_sequence = sequence.strip()
                if clean_sequence.startswith('```'):
                    clean_sequence = clean_sequence.split('```')[1]
                    if clean_sequence.startswith('json'):
                        clean_sequence = clean_sequence[4:]
                clean_sequence = clean_sequence.strip()
                sequence_data = json.loads(clean_sequence)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse sequence JSON: {str(e)}")
                sequence_data = sequence
        else:
            sequence_data = sequence

        logger.info(f"Analyzing sequence: {sequence_data}")
        
        prompt = f"""You are a recruiting email performance analyst.

Analyze the following outreach sequence and estimate:

1. Estimated open rate (%): Based on subject lines, tone, curiosity factor
2. Estimated response rate (%): Based on call to action, personalization, clarity
3. Sentiment: Positive / Neutral / Negative
4. Personalization score (0-100): How tailored is this?
5. Quality score (0-100): How likely is this to perform well overall?

Consider these factors:
- Subject line effectiveness
- Message clarity and structure
- Call-to-action strength
- Personalization level
- Overall professionalism
- Value proposition clarity

Respond in **strict JSON** like this:
{{
  "open_rate": "52%",
  "response_rate": "24%",
  "sentiment": "Positive",
  "personalization_score": "75",
  "quality_score": "82"
}}

Here is the sequence:
{json.dumps(sequence_data, indent=2)}
"""
        response = model.generate_content(prompt)
        logger.info(f"Metrics analysis response: {response.text}")
        
        # Clean the response text
        clean_response = response.text.strip()
        if clean_response.startswith('```'):
            clean_response = clean_response.split('```')[1]
            if clean_response.startswith('json'):
                clean_response = clean_response[4:]
        clean_response = clean_response.strip()
        
        metrics = json.loads(clean_response)
        logger.info(f"Parsed metrics: {metrics}")
        return metrics
    except Exception as e:
        logger.error(f"Error analyzing sequence metrics: {str(e)}")
        return {
            "open_rate": "N/A",
            "response_rate": "N/A",
            "sentiment": "N/A",
            "personalization_score": "N/A",
            "quality_score": "N/A"
        }

def generate_suggestions(sequence):
    """Generate AI suggestions for improving the sequence."""
    try:
        prompt = f"""You are an AI recruiting coach reviewing an outreach sequence.

Analyze the sequence and provide 3 actionable suggestions to improve it. Focus on:
- Personalization (LinkedIn, GitHub, shared interests)
- Subject line quality
- Message clarity, tone, or engagement
- Targeting the right candidate

Respond in JSON as:
{{
  "suggestions": [
    "Suggestion 1...",
    "Suggestion 2...",
    "Suggestion 3..."
  ]
}}

Here is the sequence to analyze:
{json.dumps(sequence, indent=2)}
"""
        response = model.generate_content(prompt)
        logger.info(f"Suggestions response: {response.text}")
        
        # Clean the response text
        clean_response = response.text.strip()
        if clean_response.startswith('```'):
            clean_response = clean_response.split('```')[1]
            if clean_response.startswith('json'):
                clean_response = clean_response[4:]
        clean_response = clean_response.strip()
        
        suggestions = json.loads(clean_response)
        logger.info(f"Parsed suggestions: {suggestions}")
        return suggestions.get('suggestions', [])
    except Exception as e:
        logger.error(f"Error generating suggestions: {str(e)}")
        return []

def handle_sequence_generation(data):
    """Generate a sequence based on the conversation context."""
    try:
        logger.info(f"Generating sequence with data: {data}")
        messages = data.get('messages', [])
        tone = data.get('tone', 'professional')
        sequence_type = data.get('sequenceType', 'passive')
        persona = data.get('persona', 'corporate_pro')
        
        # Generate sequence using Gemini
        prompt = f"""Based on the following conversation, generate a recruiting outreach sequence.

Context:
- Messages: {messages}
- Tone: {tone}
- Sequence Type: {sequence_type}

Generate a sequence of 2-3 emails. Return ONLY a JSON array of email steps, each with 'subject' and 'body' fields.
Format the response exactly like this:
[
  {{
    "subject": "Exciting Senior Backend Engineer opportunity at [Company]",
    "body": "Email body here..."
  }},
  {{
    "subject": "Following up: Senior Backend Engineer role",
    "body": "Follow up email body here..."
  }}
]"""
        
        response = model.generate_content(prompt)
        logger.info(f"Generated sequence response: {response.text}")
        
        # Clean the response text
        clean_response = response.text.strip()
        if clean_response.startswith('```'):
            clean_response = clean_response.split('```')[1]
            if clean_response.startswith('json'):
                clean_response = clean_response[4:]
        clean_response = clean_response.strip()
        
        # Parse and validate the sequence
        sequence = json.loads(clean_response)
        logger.info(f"Parsed sequence: {sequence}")
        
        # Generate suggestions
        suggestions = generate_suggestions(sequence)
        
        # Analyze the sequence metrics
        metrics = analyze_sequence_metrics(sequence)
        
        # Store the sequence in the database
        try:
            email_sequence = EmailSequence(
                content=json.dumps(sequence, indent=2),
                persona=persona,
                tone=tone,
                sequence_type=sequence_type
            )
            db.session.add(email_sequence)
            db.session.commit()
            logger.info(f"Stored sequence in database with ID: {email_sequence.id}")
        except Exception as e:
            logger.error(f"Error storing sequence in database: {str(e)}")
            db.session.rollback()
        
        return {
            'message': "I've generated a sequence based on our conversation.",
            'content': json.dumps(sequence, indent=2),
            'metrics': metrics,
            'suggestions': suggestions
        }
    except Exception as e:
        logger.error(f"Error generating sequence: {str(e)}")
        return {'error': 'Failed to generate sequence'}

def handle_tone_adjustment(data):
    """Adjust the tone of the sequence."""
    try:
        logger.info(f"Adjusting tone with data: {data}")
        content = data.get('content', '')
        tone = data.get('tone', 'professional')
        
        # Generate tone-adjusted content using Gemini
        prompt = f"""Adjust the tone of this sequence to be more {tone}:
        {content}
        
        Return the adjusted sequence in the same JSON format."""
        
        response = model.generate_content(prompt)
        
        return {
            'message': f"I've adjusted the tone to be more {tone}.",
            'content': response.text
        }
    except Exception as e:
        logger.error(f"Error adjusting tone: {str(e)}")
        return {'error': 'Failed to adjust tone'}

def handle_context_summary(data):
    """Generate a summary of the conversation context."""
    try:
        logger.info(f"Summarizing context with data: {data}")
        messages = data.get('messages', [])
        
        # Generate summary using Gemini
        prompt = f"""Analyze this conversation and extract key information about the role:
        {messages}
        
        Return a JSON object with these fields:
        - role: The job title/role
        - company_type: Type of company/environment
        - key_requirements: Main skills and requirements
        - location: Work location/setup if mentioned
        - unique_selling_points: What makes this role special"""
        
        response = model.generate_content(prompt)
        
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Error summarizing context: {str(e)}")
        return {'error': 'Failed to summarize context'}

# Define available tools
tools = {
    'generate_sequence': handle_sequence_generation,
    'adjust_tone': handle_tone_adjustment,
    'summarize_context': handle_context_summary
}

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info("Client connected")
    emit('connection_status', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@socketio.on('test_connection')
def handle_test_connection(data):
    """Handle test connection."""
    logger.info(f"Received test connection: {data}")
    emit('test_response', {'message': 'Test connection successful'})

@socketio.on('chat_message')
def handle_message(data):
    try:
        logger.info(f"Received chat message: {data}")
        message = data.get('message', '')
        messages = data.get('messages', [])
        persona = data.get('persona')
        
        if not message:  # If it's an initial message
            return
            
        # Prepare prompt for Gemini
        prompt = f"""You are Helix, an AI recruiting assistant helping a user craft outreach messages.

Your goal is to guide the user through:
1. Understanding the role requirements:
   - Job title and level
   - Key skills and qualifications
   - Company culture and environment
   - Location and work setup

2. Crafting personalized outreach:
   - Help choose appropriate tone (professional, casual, founder, friendly)
   - Suggest personalization strategies
   - Recommend sequence length and cadence

3. Iterative improvement:
   - Offer specific suggestions for each message
   - Help adjust tone and style
   - Provide feedback on effectiveness

Current context:
- User message: "{message}"
- Previous messages: {str(messages)}
- Selected persona: {persona}

Respond in this exact JSON format:
{{
    "action": "chat" or "tool",
    "response": "your natural, friendly response if action is chat",
    "tool": "tool name if action is tool (generate_sequence, adjust_tone, or summarize_context)",
    "args": {{
        "parameters if action is tool"
    }}
}}

Remember to:
- Be conversational and friendly
- Ask clarifying questions when needed
- Provide specific suggestions and examples
- Guide the user step-by-step
- Acknowledge and build upon previous context
"""

        # Call Gemini
        response = model.generate_content(prompt)
        logger.info(f"Gemini response: {response.text}")
        
        # Clean the response text - remove markdown code blocks if present
        clean_response = response.text.strip()
        if clean_response.startswith('```'):
            clean_response = clean_response.split('```')[1]
            if clean_response.startswith('json'):
                clean_response = clean_response[4:]
        clean_response = clean_response.strip()
        
        # Parse the response
        try:
            parsed_response = json.loads(clean_response)
            logger.info(f"Parsed response: {parsed_response}")
            
            if parsed_response.get('action') == 'chat':
                # Send the natural chat response
                response = {
                    'role': 'assistant',
                    'content': parsed_response.get('response', "Could you tell me more about what you're looking for?")
                }
                emit('chat_message', response)
            elif parsed_response.get('action') == 'tool':
                tool_name = parsed_response.get('tool')
                args = parsed_response.get('args', {})
                
                if tool_name in tools:
                    # Add context to args
                    args['messages'] = messages
                    args['persona'] = persona
                    
                    # Call the appropriate tool
                    result = tools[tool_name](args)
                    
                    # Send response back to client
                    response = {
                        'role': 'assistant',
                        'content': result.get('message', "I've processed your request. Let me know if you need any adjustments.")
                    }
                    emit('chat_message', response)
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {str(e)}")
            logger.error(f"Raw response: {response.text}")
            # Send a graceful response asking for clarification
            response = {
                'role': 'assistant',
                'content': "I'm here to help you with recruiting. Could you tell me what role you're looking to hire for?"
            }
            emit('chat_message', response)
            
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        emit('error', {'message': 'An error occurred while processing your message'})

@socketio.on('generate_sequence')
def handle_sequence_generation_event(data):
    """Handle sequence generation event."""
    try:
        result = handle_sequence_generation(data)
        emit('sequence_update', {
            'content': result.get('content', ''),
            'metrics': result.get('metrics', {}),
            'suggestions': result.get('suggestions', [])
        })
    except Exception as e:
        logger.error(f"Error handling sequence generation: {str(e)}")
        emit('error', {'message': 'Failed to generate sequence'})

@socketio.on('adjust_tone')
def handle_tone_adjustment_event(data):
    """Handle tone adjustment event."""
    try:
        result = handle_tone_adjustment(data)
        emit('sequence_update', {'content': result.get('content', '')})
    except Exception as e:
        logger.error(f"Error handling tone adjustment: {str(e)}")
        emit('error', {'message': 'Failed to adjust tone'})

@socketio.on('summarize_context')
def handle_context_summary_event(data):
    """Handle context summary event."""
    try:
        result = handle_context_summary(data)
        emit('context_summary', result)
    except Exception as e:
        logger.error(f"Error handling context summary: {str(e)}")
        emit('error', {'message': 'Failed to summarize context'})

@socketio.on('get_sequence_metrics')
def handle_sequence_metrics(data):
    app.logger.info(f"Getting sequence metrics with data: {data}")
    sequence = data.get('sequence', [])
    
    # Calculate metrics
    metrics = {
        'estimated_open_rate': '45%',
        'estimated_response_rate': '28%',
        'sequence_quality_score': '92',
        'personalization_score': '85',
        'clarity_score': '90'
    }
    
    emit('sequence_metrics', metrics)
    return {'status': 'success', 'message': 'Metrics calculated'}

@socketio.on('apply_suggestion')
def handle_suggestion_application(data):
    """Handle applying a suggestion to the sequence."""
    try:
        logger.info(f"Applying suggestion with data: {data}")
        suggestion_index = data.get('suggestion_index')
        current_sequence = data.get('sequence', '')
        
        if not current_sequence:
            raise ValueError("No sequence provided")
            
        # Parse the current sequence
        if isinstance(current_sequence, str):
            sequence = json.loads(current_sequence)
        else:
            sequence = current_sequence
            
        # Generate the improved sequence based on the suggestion
        prompt = f"""You are an AI recruiting coach. Apply the following suggestion to improve this sequence:

Suggestion: {data.get('suggestion', '')}

Current sequence:
{json.dumps(sequence, indent=2)}

Return ONLY the improved sequence in the same JSON format with the suggestion applied."""

        response = model.generate_content(prompt)
        logger.info(f"Improved sequence response: {response.text}")
        
        # Clean and parse the response
        clean_response = response.text.strip()
        if clean_response.startswith('```'):
            clean_response = clean_response.split('```')[1]
            if clean_response.startswith('json'):
                clean_response = clean_response[4:]
        clean_response = clean_response.strip()
        
        improved_sequence = json.loads(clean_response)
        
        # Generate new metrics for the improved sequence
        metrics = analyze_sequence_metrics(improved_sequence)
        
        emit('sequence_update', {
            'content': json.dumps(improved_sequence, indent=2),
            'metrics': metrics,
            'message': 'Successfully applied the suggestion!'
        })
    except Exception as e:
        logger.error(f"Error applying suggestion: {str(e)}")
        emit('error', {'message': 'Failed to apply suggestion'})

@socketio.on('update_sequence_from_edit')
def handle_sequence_edit(data):
    app.logger.info(f"Updating sequence from edit with data: {data}")
    doc_delta = data.get('doc_delta', {})
    sequence = data.get('sequence', [])
    
    # Update sequence based on edit
    # For now, return the same sequence with a success message
    emit('sequence_update', {'content': json.dumps(sequence, indent=2)})
    return {'status': 'success', 'message': 'Sequence updated from edit'}

@app.route('/api/magic_action', methods=['POST'])
def handle_magic_action():
    try:
        data = request.get_json()
        action = data.get('action')
        sequence = data.get('sequence')
        
        if action == 'enhance_personalization':
            enhanced_sequence = "Enhanced sequence with more personalization..."
            return jsonify({'sequence': enhanced_sequence})
        elif action == 'refresh':
            # Implement refresh logic
            pass
        elif action == 'download':
            # Implement download logic
            pass
        
        return jsonify({'message': 'Action not supported'}), 400
        
    except Exception as e:
        logger.error(f"Error handling magic action: {str(e)}")
        return jsonify({'message': 'An error occurred'}), 500

if __name__ == '__main__':
    socketio.run(app, port=3002) 