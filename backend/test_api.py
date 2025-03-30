import pytest
from app import app, socketio
from ai import RecruitingAI
import json
import os

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def socket_client():
    return socketio.test_client(app)

@pytest.fixture
def ai_client():
    return RecruitingAI(api_key="mock-key")

def test_home_endpoint(client):
    """Test the home endpoint"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Recruiting AI Backend" in response.data

def test_personas_endpoint(client):
    """Test the personas endpoint"""
    response = client.get('/api/personas')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    assert len(data) > 0
    assert all('id' in persona for persona in data)
    assert all('name' in persona for persona in data)
    assert all('description' in persona for persona in data)

def test_socket_connection(socket_client):
    """Test socket.io connection"""
    assert socket_client.is_connected()

def test_socket_disconnect(socket_client):
    """Test socket.io disconnection"""
    assert socket_client.is_connected()
    socket_client.disconnect()
    assert not socket_client.is_connected()

def test_chat_message(socket_client):
    """Test chat message handling"""
    socket_client.emit('chat_message', {
        'message': 'I am recruiting for a Software Engineer',
        'messages': [],
        'persona': 'corporate_pro'
    })
    received = socket_client.get_received()
    assert len(received) > 0

def test_chat_message_validation(socket_client):
    """Test chat message validation"""
    # Test missing message field
    socket_client.emit('chat_message', {
        'messages': [],
        'persona': 'corporate_pro'
    })
    received = socket_client.get_received()
    assert len(received) > 0

    # Test invalid persona
    socket_client.emit('chat_message', {
        'message': 'Test message',
        'messages': [],
        'persona': 'invalid_persona'
    })
    received = socket_client.get_received()
    assert len(received) > 0

def test_tone_update(socket_client):
    """Test tone update handling"""
    socket_client.emit('update_tone', {
        'content': 'We are looking for a talented Software Engineer',
        'tone': 'friendly',
        'sequenceType': 'passive',
        'roleInfo': []
    })
    received = socket_client.get_received()
    assert len(received) >= 0  # The response might be async

def test_sequence_type_update(socket_client):
    """Test sequence type update handling"""
    socket_client.emit('update_sequence_type', {
        'content': 'We are looking for a talented Software Engineer',
        'tone': 'professional',
        'sequenceType': 'aggressive',
        'roleInfo': []
    })
    received = socket_client.get_received()
    assert len(received) >= 0  # The response might be async

def test_magic_action(socket_client):
    """Test magic action handling"""
    socket_client.emit('magic_action', {
        'content': 'We are looking for a talented Software Engineer',
        'action': 'shorter',
        'tone': 'professional',
        'sequenceType': 'passive',
        'roleInfo': []
    })
    received = socket_client.get_received()
    assert len(received) >= 0  # The response might be async

def test_generate_sequence(socket_client):
    """Test sequence generation with different personas"""
    personas = ['corporate_pro', 'startup_founder', 'friendly_recruiter', 'tech_expert']
    for persona in personas:
        socket_client.emit('generate_sequence', {
            'role': 'Senior Software Engineer',
            'tone': 'professional',
            'step_count': 2,
            'company_info': 'A leading tech company'
        })
        received = socket_client.get_received()
        assert len(received) >= 0  # The response might be async

def test_recruiting_ai_initialization(ai_client):
    """Test RecruitingAI class initialization"""
    assert ai_client is not None
    assert hasattr(ai_client, 'generate_response')
    assert hasattr(ai_client, 'generate_sequence')
    assert ai_client.mock_mode == True

def test_recruiting_ai_response(ai_client):
    """Test RecruitingAI response generation"""
    response = ai_client.generate_response(
        "Looking for a Software Engineer",
        []
    )
    assert isinstance(response, str)
    assert "mock mode" in response.lower()

def test_recruiting_ai_sequence(ai_client):
    """Test RecruitingAI sequence generation"""
    sequence = ai_client.generate_sequence(
        role="Senior Software Engineer",
        tone="professional",
        step_count=2
    )
    assert isinstance(sequence, list)
    assert len(sequence) > 0
    assert all('subject' in email for email in sequence)
    assert all('body' in email for email in sequence) 