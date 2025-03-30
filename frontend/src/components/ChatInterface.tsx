import React, { useState, useRef, useEffect } from 'react';
import { Box, Stack, TextField, IconButton, Typography, Avatar } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  onGenerateSequence: () => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onSendMessage,
  onGenerateSequence
}) => {
  const [message, setMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  return (
    <Box sx={{ 
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
    }}>
      <Box sx={{ 
        flexGrow: 1, 
        overflow: 'auto',
        p: 3,
        display: 'flex',
        flexDirection: 'column',
        gap: 2
      }}>
        {messages.map((msg, index) => (
          <Stack
            key={index}
            direction="row"
            spacing={2}
            alignItems="flex-start"
            sx={{
              alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '80%'
            }}
          >
            {msg.role === 'assistant' && (
              <Avatar 
                sx={{ 
                  bgcolor: '#4F46E5',
                  width: 32,
                  height: 32
                }}
              >
                H
              </Avatar>
            )}
            <Box
              sx={{
                bgcolor: msg.role === 'user' ? '#4F46E5' : '#F3F4F6',
                color: msg.role === 'user' ? 'white' : 'text.primary',
                p: 2,
                borderRadius: 2,
                borderTopLeftRadius: msg.role === 'assistant' ? 0 : 2,
                borderTopRightRadius: msg.role === 'user' ? 0 : 2,
              }}
            >
              <Typography variant="body1">
                {msg.content}
              </Typography>
            </Box>
            {msg.role === 'user' && (
              <Avatar 
                sx={{ 
                  bgcolor: '#E5E7EB',
                  color: '#4B5563',
                  width: 32,
                  height: 32
                }}
              >
                U
              </Avatar>
            )}
          </Stack>
        ))}
        <div ref={messagesEndRef} />
      </Box>

      <Box
        component="form"
        onSubmit={handleSubmit}
        sx={{
          p: 2,
          borderTop: '1px solid #E5E7EB',
          bgcolor: 'white'
        }}
      >
        <Stack direction="row" spacing={1}>
          <TextField
            fullWidth
            size="small"
            placeholder="Type your message..."
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            sx={{
              '& .MuiOutlinedInput-root': {
                bgcolor: '#F9FAFB',
                '& fieldset': {
                  borderColor: '#E5E7EB',
                },
                '&:hover fieldset': {
                  borderColor: '#4F46E5',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#4F46E5',
                },
              },
            }}
          />
          <IconButton 
            type="submit" 
            sx={{ 
              bgcolor: '#4F46E5',
              color: 'white',
              '&:hover': {
                bgcolor: '#4338CA',
              },
            }}
          >
            <SendIcon />
          </IconButton>
        </Stack>
        <Typography 
          variant="caption" 
          color="text.secondary"
          sx={{ mt: 1, display: 'block' }}
        >
          Press Enter to send, Shift+Enter for a new line
        </Typography>
      </Box>
    </Box>
  );
};

export default ChatInterface; 