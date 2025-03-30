import React, { useEffect, useState } from 'react';
import { Box, Stack, Typography, Select, MenuItem, SelectChangeEvent, Snackbar, Alert, Chip, Fade, AppBar, Toolbar } from '@mui/material';
import { io, Socket } from 'socket.io-client';
import ChatInterface from './components/ChatInterface';
import Workspace from './components/Workspace';
import LandingPage from './components/LandingPage';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface Persona {
  id: string;
  name: string;
  emoji: string;
  style: string;
  description: string;
  tone: string;
  sequenceType: string;
}

const PERSONAS: Persona[] = [
  {
    id: 'corporate_pro',
    name: 'Corporate Professional',
    emoji: '👔',
    style: 'Formal and structured outreach',
    description: 'Specializes in formal, professional communication with a focus on corporate excellence and structured outreach sequences.',
    tone: 'professional',
    sequenceType: 'passive'
  },
  {
    id: 'startup_founder',
    name: 'Startup Founder',
    emoji: '🚀',
    style: 'Direct and passionate outreach',
    description: 'Brings startup energy and vision, focusing on growth opportunities and innovative challenges.',
    tone: 'founder',
    sequenceType: 'aggressive'
  },
  {
    id: 'friendly_recruiter',
    name: 'Friendly Recruiter',
    emoji: '😊',
    style: 'Warm and personable approach',
    description: 'Creates welcoming, personalized messages that build genuine connections with candidates.',
    tone: 'friendly',
    sequenceType: 'soft'
  },
  {
    id: 'tech_expert',
    name: 'Tech Expert',
    emoji: '💻',
    style: 'Technical and detailed outreach',
    description: 'Focuses on technical depth and engineering challenges, speaking the language of developers.',
    tone: 'professional',
    sequenceType: 'passive'
  }
];

function App() {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedPersona, setSelectedPersona] = useState('corporate_pro');
  const [selectedTone, setSelectedTone] = useState('professional');
  const [sequenceType, setSequenceType] = useState('passive');
  const [content, setContent] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [showChat, setShowChat] = useState(false);

  useEffect(() => {
    const newSocket = io('http://localhost:3002', {
      reconnection: true,
      reconnectionAttempts: Infinity,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      timeout: 60000,
      transports: ['websocket', 'polling'],
      withCredentials: true,
      forceNew: true
    });
    setSocket(newSocket);

    newSocket.on('connect', () => {
      console.log('Connected to server');
      setError(null);
      // Test emit on connect
      newSocket.emit('test_connection', { message: 'Test connection' });
    });

    newSocket.on('connect_error', (error) => {
      console.error('Connection error:', error);
      setError('Connection error. Retrying...');
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from server');
      setError('Disconnected from server. Attempting to reconnect...');
    });

    newSocket.on('chat_message', (message: Message) => {
      console.log('Received chat message:', message);
      setMessages(prev => [...prev, message]);
    });

    newSocket.on('sequence_update', (data: { content: string }) => {
      console.log('Received sequence update:', data);
      setContent(data.content);
    });

    newSocket.on('test_response', (data: { message: string }) => {
      console.log('Received test response:', data);
    });

    return () => {
      newSocket.close();
    };
  }, []);

  const handleGetStarted = (persona: string) => {
    const selectedPersonaObj = PERSONAS.find(p => p.id === persona);
    if (selectedPersonaObj) {
      setSelectedPersona(persona);
      setSelectedTone(selectedPersonaObj.tone);
      setSequenceType(selectedPersonaObj.sequenceType);
      setShowChat(true);
      socket?.emit('chat_message', {
        message: '',
        messages: [],
        persona: persona
      });
    }
  };

  const handlePersonaChange = (event: SelectChangeEvent) => {
    const newPersona = PERSONAS.find(p => p.id === event.target.value);
    if (newPersona) {
      setSelectedPersona(newPersona.id);
      setSelectedTone(newPersona.tone);
      setSequenceType(newPersona.sequenceType);
      setMessages([]);
      socket?.emit('chat_message', {
        message: '',
        messages: [],
        persona: newPersona.id
      });
    }
  };

  const handleSendMessage = (message: string) => {
    if (!socket?.connected) {
      setError('Not connected to server. Please wait for reconnection.');
      return;
    }

    const newMessage: Message = {
      role: 'user' as const,
      content: message
    };

    setMessages(prev => [...prev, newMessage]);

    socket.emit('chat_message', {
      message,
      messages: [...messages, newMessage],
      persona: selectedPersona,
      sequence_generated: content !== '' // Track if sequence has been generated
    });
  };

  const handleSequenceUpdate = (data: { content: string }) => {
    console.log('Received sequence update:', data);
    setContent(data.content);
  };

  const handleToneChange = (tone: string) => {
    if (!socket?.connected) {
      setError('Not connected to server. Please wait for reconnection.');
      return;
    }
    setSelectedTone(tone);
    socket.emit('update_tone', { 
      content,
      tone,
      sequenceType,
      roleInfo: messages 
    });
  };

  const handleSequenceTypeChange = (type: string) => {
    if (!socket?.connected) {
      setError('Not connected to server. Please wait for reconnection.');
      return;
    }
    setSequenceType(type);
    socket.emit('update_sequence_type', { 
      content,
      tone: selectedTone,
      sequenceType: type,
      roleInfo: messages 
    });
  };

  const handleMagicAction = (action: string) => {
    if (!socket?.connected) {
      setError('Not connected to server. Please wait for reconnection.');
      return;
    }
    socket.emit('magic_action', { 
      content,
      action,
      tone: selectedTone,
      sequenceType,
      roleInfo: messages 
    });
  };

  const handleContentChange = (newContent: string) => {
    setContent(newContent);
    if (socket?.connected) {
      socket.emit('sequence_update', { 
        content: newContent,
        tone: selectedTone,
        sequenceType,
        roleInfo: messages 
      });
    }
  };

  const handleGenerateSequence = () => {
    if (!socket?.connected) {
      setError('Not connected to server. Please wait for reconnection.');
      return;
    }
    socket.emit('generate_sequence', {
      messages,
      tone: selectedTone,
      sequenceType,
      persona: selectedPersona
    });
  };

  const currentPersona = PERSONAS.find(p => p.id === selectedPersona);

  if (!showChat) {
    return <LandingPage onGetStarted={handleGetStarted} />;
  }

  return (
    <Fade in={showChat} timeout={800}>
      <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column', bgcolor: '#f8f9fc' }}>
        <AppBar position="static" elevation={0} sx={{ bgcolor: 'white', borderBottom: '1px solid #eaecf0' }}>
          <Toolbar>
            <Stack direction="row" spacing={1} alignItems="center">
              <Typography 
                variant="h6" 
                component="div" 
                sx={{ 
                  color: '#4F46E5',
                  fontWeight: 600,
                  fontSize: '1.5rem'
                }}
              >
                Helix
              </Typography>
            </Stack>
            <Box sx={{ flexGrow: 1 }} />
            <Stack direction="row" spacing={2}>
              <Typography 
                variant="body2" 
                sx={{ 
                  color: '#6B7280',
                  '&:hover': { color: '#4F46E5' },
                  cursor: 'pointer'
                }}
              >
                Docs
              </Typography>
              <Typography 
                variant="body2" 
                sx={{ 
                  color: '#6B7280',
                  '&:hover': { color: '#4F46E5' },
                  cursor: 'pointer'
                }}
              >
                Settings
              </Typography>
            </Stack>
          </Toolbar>
        </AppBar>

        <Box sx={{ 
          display: 'flex', 
          flexGrow: 1,
          gap: 0,
          overflow: 'hidden'
        }}>
          <Box sx={{ 
            width: '40%',
            display: 'flex',
            flexDirection: 'column',
            borderRight: '1px solid #eaecf0',
            bgcolor: 'white',
          }}>
            <Box sx={{ p: 3, borderBottom: '1px solid #eaecf0' }}>
              <Stack spacing={1}>
                <Stack direction="row" spacing={1} alignItems="center">
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Chat with Helix
                  </Typography>
                </Stack>
                <Typography variant="body2" color="text.secondary">
                  I'll help you craft the perfect recruiting sequence
                </Typography>
              </Stack>
            </Box>
            <ChatInterface
              messages={messages}
              onSendMessage={handleSendMessage}
              onGenerateSequence={handleGenerateSequence}
            />
          </Box>
          
          <Box sx={{ 
            width: '60%',
            display: 'flex',
            flexDirection: 'column',
            bgcolor: 'white',
          }}>
            <Box sx={{ p: 3, borderBottom: '1px solid #eaecf0' }}>
              <Stack spacing={1}>
                <Stack direction="row" spacing={2} alignItems="center">
                  <Typography variant="h6" sx={{ fontWeight: 600 }}>
                    Recruiting Sequence
                  </Typography>
                  <Box sx={{ flexGrow: 1 }} />
                  <Select
                    value={selectedPersona}
                    onChange={handlePersonaChange}
                    size="small"
                    sx={{ 
                      minWidth: 200,
                      '& .MuiOutlinedInput-notchedOutline': {
                        borderColor: '#E5E7EB',
                      },
                      '&:hover .MuiOutlinedInput-notchedOutline': {
                        borderColor: '#4F46E5',
                      },
                    }}
                  >
                    {PERSONAS.map((persona) => (
                      <MenuItem key={persona.id} value={persona.id}>
                        {persona.emoji} {persona.name}
                      </MenuItem>
                    ))}
                  </Select>
                </Stack>
                {currentPersona && (
                  <Typography variant="body2" color="text.secondary">
                    {currentPersona.description}
                  </Typography>
                )}
              </Stack>
            </Box>
            <Workspace 
              content={content}
              onChange={handleContentChange}
              onToneChange={handleToneChange}
              onSequenceTypeChange={handleSequenceTypeChange}
              onMagicAction={handleMagicAction}
              selectedTone={selectedTone}
              sequenceType={sequenceType}
            />
          </Box>
        </Box>

        <Snackbar 
          open={!!error} 
          autoHideDuration={6000} 
          onClose={() => setError(null)}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        </Snackbar>
      </Box>
    </Fade>
  );
}

export default App; 