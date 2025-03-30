import React, { useEffect, useState } from 'react';
import { Box, Stack, Typography, Select, MenuItem, SelectChangeEvent, Snackbar, Alert, Chip, Fade, AppBar, Toolbar, Container, CssBaseline, ThemeProvider, createTheme, Button } from '@mui/material';
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

interface Metrics {
  open_rate: string;
  response_rate: string;
  sentiment: string;
  personalization_score: string;
  quality_score: string;
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

const theme = createTheme({
  palette: {
    primary: {
      main: '#4F46E5',
    },
    background: {
      default: '#F3F4F6',
    },
  },
});

const App: React.FC = () => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedPersona, setSelectedPersona] = useState('corporate_pro');
  const [selectedTone, setSelectedTone] = useState('professional');
  const [sequenceType, setSequenceType] = useState('passive');
  const [content, setContent] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [showChat, setShowChat] = useState(false);
  const [metrics, setMetrics] = useState<Metrics | undefined>(undefined);
  const [suggestions, setSuggestions] = useState<string[] | undefined>(undefined);

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

    newSocket.on('sequence_update', (data: { content: string; metrics: Metrics; suggestions: string[] }) => {
      console.log('Received sequence update:', data);
      setContent(data.content);
      setMetrics(data.metrics);
      setSuggestions(data.suggestions);
    });

    newSocket.on('test_response', (data: { message: string }) => {
      console.log('Received test response:', data);
    });

    newSocket.on('context_summary', (data: any) => {
      console.log('Received context summary:', data);
      const summaryMessage: Message = {
        role: 'assistant',
        content: `Here's a summary of the role requirements:\n\n` +
                `Role: ${data.role}\n` +
                `Company Type: ${data.company_type}\n` +
                `Key Requirements: ${data.key_requirements}\n` +
                `Location: ${data.location}\n` +
                `Unique Selling Points: ${data.unique_selling_points}`
      };
      setMessages(prev => [...prev, summaryMessage]);
    });

    return () => {
      newSocket.close();
    };
  }, []);

  const getInitialMessage = (persona: Persona): Message => {
    let content: string;
    
    switch (persona.id) {
      case 'startup_founder':
        content = "Hi there! I'm Helix, your startup-focused recruiting assistant. I'll help you create dynamic and passionate outreach sequences that capture your startup's energy. What role are you looking to fill?";
        break;
      case 'friendly_recruiter':
        content = "Hi! 😊 I'm Helix, your friendly recruiting assistant. I'll help you create warm and personalized outreach sequences that build genuine connections. What role are we recruiting for today?";
        break;
      case 'tech_expert':
        content = "Hello! I'm Helix, your technical recruiting specialist. I'll help you craft detailed outreach sequences that resonate with engineering talent. What type of technical role are you recruiting for?";
        break;
      case 'corporate_pro':
      default:
        content = "Hello! I'm Helix, your professional recruiting assistant. I'll help you craft formal and structured outreach sequences that align with corporate excellence. What type of role are you recruiting for?";
    }

    return {
      role: 'assistant',
      content
    };
  };

  const handleGetStarted = (persona: string) => {
    const selectedPersonaObj = PERSONAS.find(p => p.id === persona);
    if (selectedPersonaObj) {
      setSelectedPersona(persona);
      setSelectedTone(selectedPersonaObj.tone);
      setSequenceType(selectedPersonaObj.sequenceType);
      setShowChat(true);
      
      const initialMessage = getInitialMessage(selectedPersonaObj);
      setMessages([initialMessage]);

      socket?.emit('chat_message', {
        message: '',
        messages: [initialMessage],
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
      
      const initialMessage = getInitialMessage(newPersona);
      setMessages([initialMessage]);

      socket?.emit('chat_message', {
        message: '',
        messages: [initialMessage],
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
    socket.emit('adjust_tone', { 
      content,
      tone,
      sequenceType,
      roleInfo: messages 
    });

    // Add a message to show the tone change
    const message: Message = {
      role: 'assistant',
      content: `I've adjusted the tone to be more ${tone}. Let me know if you'd like any other changes.`
    };
    setMessages(prev => [...prev, message]);
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

    if (action === 'summarize_context') {
      socket.emit('summarize_context', {
        messages,
        persona: selectedPersona
      });
    } else {
      socket.emit('magic_action', { 
        content,
        action,
        tone: selectedTone,
        sequenceType,
        roleInfo: messages 
      });
    }
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

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
        <AppBar position="static" elevation={0} sx={{ bgcolor: 'white', borderBottom: '1px solid #eaecf0' }}>
          <Toolbar sx={{ minHeight: '56px' }}>
            <Stack direction="row" spacing={1} alignItems="center">
              <Typography variant="h6" sx={{ color: '#4F46E5', fontWeight: 600 }}>
                Helix
              </Typography>
            </Stack>
            <Box sx={{ flexGrow: 1 }} />
            <Stack direction="row" spacing={3}>
              <Button sx={{ color: '#6B7280' }}>Docs</Button>
              <Button sx={{ color: '#6B7280' }}>Settings</Button>
              <Button sx={{ color: '#6B7280' }}>JD</Button>
            </Stack>
          </Toolbar>
        </AppBar>

        <Container maxWidth={false} sx={{ flexGrow: 1, py: 0 }}>
          {!showChat ? (
            <LandingPage onGetStarted={handleGetStarted} />
          ) : (
            <Workspace
              messages={messages}
              selectedPersona={selectedPersona}
              selectedTone={selectedTone}
              sequenceType={sequenceType}
              content={content}
              onPersonaChange={handlePersonaChange}
              onSendMessage={handleSendMessage}
              onSequenceUpdate={handleSequenceUpdate}
              onToneChange={handleToneChange}
              onSequenceTypeChange={handleSequenceTypeChange}
              onMagicAction={handleMagicAction}
              onContentChange={handleContentChange}
              onGenerateSequence={handleGenerateSequence}
              personas={PERSONAS}
              currentPersona={currentPersona}
              metrics={metrics}
              suggestions={suggestions}
            />
          )}
        </Container>
      </Box>
    </ThemeProvider>
  );
};

export default App; 