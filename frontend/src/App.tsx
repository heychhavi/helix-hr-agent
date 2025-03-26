import React, { useState, useEffect } from 'react';
import { Box, CssBaseline, ThemeProvider, createTheme, Snackbar, Alert } from '@mui/material';
import ChatInterface from './components/ChatInterface';
import Workspace from './components/Workspace';
import { io, Socket } from 'socket.io-client';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2196f3',
    },
    secondary: {
      main: '#f50057',
    },
  },
});

// Ensure we're connecting to the correct port
const BACKEND_URL = 'http://localhost:5001';
console.log('Connecting to backend at:', BACKEND_URL);

type Message = {
  role: 'user' | 'assistant';
  content: string;
};

function App() {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [sequence, setSequence] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [error, setError] = useState<string>('');
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Initialize socket connection
    const newSocket = io(BACKEND_URL, {
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
      transports: ['websocket', 'polling'], // Try different transports
    });

    newSocket.on('connect', () => {
      console.log('Connected to server');
      setIsConnected(true);
      setError('');
    });

    newSocket.on('connect_error', (err) => {
      console.error('Connection error:', err);
      setError('Failed to connect to server. Please check if the backend is running.');
      setIsConnected(false);
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from server');
      setIsConnected(false);
      setError('Disconnected from server. Attempting to reconnect...');
    });

    newSocket.on('chat_message', (data: Message) => {
      console.log('Received message:', data);
      setMessages(prev => [...prev, data]);
    });

    newSocket.on('sequence_update', (data: { content: string }) => {
      console.log('Received sequence update:', data);
      setSequence(data.content);
    });

    setSocket(newSocket);

    // Clean up on unmount
    return () => {
      newSocket.close();
    };
  }, []);

  const handleSendMessage = (message: string) => {
    if (!socket?.connected) {
      setError('Not connected to server. Please wait for reconnection.');
      return;
    }

    const newMessage: Message = { role: 'user', content: message };
    const newMessages = [...messages, newMessage];
    setMessages(newMessages);
    
    console.log('Sending message:', { message, messages: newMessages });
    socket.emit('chat_message', { 
      message,
      messages: newMessages
    });
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', height: '100vh', flexDirection: 'column' }}>
        {!isConnected && (
          <Box sx={{ p: 1, bgcolor: 'warning.main', color: 'warning.contrastText', textAlign: 'center' }}>
            Connecting to server...
          </Box>
        )}
        <Box sx={{ display: 'flex', flex: 1 }}>
          <Box sx={{ width: '40%', borderRight: 1, borderColor: 'divider' }}>
            <ChatInterface
              messages={messages}
              onSendMessage={handleSendMessage}
              isConnected={isConnected}
            />
          </Box>
          <Box sx={{ width: '60%', p: 2 }}>
            <Workspace
              content={sequence}
              onChange={(newContent) => {
                setSequence(newContent);
                socket?.emit('sequence_update', { content: newContent });
              }}
            />
          </Box>
        </Box>
        <Snackbar 
          open={!!error} 
          autoHideDuration={6000} 
          onClose={() => setError('')}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert severity="error" onClose={() => setError('')}>
            {error}
          </Alert>
        </Snackbar>
      </Box>
    </ThemeProvider>
  );
}

export default App; 