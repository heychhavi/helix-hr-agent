import React, { useState, useRef, useEffect } from 'react';
import { Box, Stack, TextField, IconButton, Typography, Avatar, Paper, Button } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import { InputAdornment } from '@mui/material';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  onGenerateSequence: () => void;
  onToneChange?: (tone: string) => void;
  onSummarizeContext?: () => void;
  persona: any;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onSendMessage,
  onGenerateSequence,
  onToneChange,
  onSummarizeContext,
  persona
}) => {
  const [message, setMessage] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleCommand = (command: string, args: string) => {
    switch (command) {
      case 'adjust_tone':
        if (onToneChange) {
          onToneChange(args.trim());
          return true;
        }
        break;
      case 'summarize_context':
        if (onSummarizeContext) {
          onSummarizeContext();
          return true;
        }
        break;
      default:
        return false;
    }
    return false;
  };

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim()) {
      // Check for slash commands
      if (message.startsWith('/')) {
        const [command, ...args] = message.slice(1).split(' ');
        const handled = handleCommand(command, args.join(' '));
        if (handled) {
          setMessage('');
          return;
        }
      }
      onSendMessage(message);
      setMessage('');
    }
  };

  return (
    <Box sx={{ 
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
      overflow: 'hidden',
    }}>
      <Box sx={{ 
        flexGrow: 1,
        overflowY: 'auto',
        p: 2,
        display: 'flex',
        flexDirection: 'column',
        gap: 2,
        minHeight: 0,
        '&::-webkit-scrollbar': {
          width: '6px',
        },
        '&::-webkit-scrollbar-track': {
          background: '#f1f1f1',
          borderRadius: '4px',
        },
        '&::-webkit-scrollbar-thumb': {
          background: '#c1c1c1',
          borderRadius: '4px',
          '&:hover': {
            background: '#a8a8a8',
          },
        },
      }}>
        {messages.map((msg, index) => (
          <Box
            key={index}
            sx={{
              alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '80%',
            }}
          >
            <Paper
              elevation={0}
              sx={{
                p: 2,
                bgcolor: msg.role === 'user' ? '#4F46E5' : '#F9FAFB',
                color: msg.role === 'user' ? 'white' : 'inherit',
                borderRadius: 2,
              }}
            >
              <Typography variant="body1">
                {msg.content}
              </Typography>
            </Paper>
            <Typography 
              variant="caption" 
              sx={{ 
                mt: 0.5, 
                display: 'block',
                color: 'text.secondary',
                textAlign: msg.role === 'user' ? 'right' : 'left'
              }}
            >
              {msg.role === 'user' ? 'You' : 'Helix AI'} • Just now
            </Typography>
          </Box>
        ))}
        <div ref={messagesEndRef} />
      </Box>
      <Box sx={{ 
        p: 2, 
        borderTop: '1px solid #eaecf0',
        bgcolor: 'white',
      }}>
        <Button
          fullWidth
          variant="outlined"
          onClick={onGenerateSequence}
          sx={{
            mb: 2,
            color: '#4F46E5',
            borderColor: '#E0E7FF',
            '&:hover': {
              borderColor: '#4F46E5',
              bgcolor: '#F5F3FF'
            }
          }}
        >
          Generate Sequence
        </Button>
        <form onSubmit={handleSendMessage}>
          <TextField
            fullWidth
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Type your message... (Try /adjust_tone or /summarize_context)"
            variant="outlined"
            size="small"
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton 
                    type="submit"
                    disabled={!message.trim()}
                    color="primary"
                  >
                    <SendIcon />
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
        </form>
      </Box>
    </Box>
  );
};

export default ChatInterface; 