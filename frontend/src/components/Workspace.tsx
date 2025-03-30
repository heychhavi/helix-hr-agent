import React, { useState, useEffect } from 'react';
import { Box, Stack, Typography, TextField, Button, Chip, IconButton, Select, MenuItem, SelectChangeEvent, Snackbar, Alert, AppBar, Toolbar } from '@mui/material';
import { Add as AddIcon, Refresh as RefreshIcon, Download as DownloadIcon } from '@mui/icons-material';
import { io, Socket } from 'socket.io-client';
import ChatInterface from './ChatInterface';

interface EmailStep {
  subject: string;
  body: string;
}

interface WorkspaceProps {
  messages: any[];
  selectedPersona: string;
  selectedTone: string;
  sequenceType: string;
  content: string;
  onPersonaChange: (event: SelectChangeEvent<string>) => void;
  onSendMessage: (message: string) => void;
  onSequenceUpdate: (data: { content: string }) => void;
  onToneChange: (tone: string) => void;
  onSequenceTypeChange: (type: string) => void;
  onMagicAction: (action: string) => void;
  onContentChange: (content: string) => void;
  onGenerateSequence: () => void;
  personas: any[];
  currentPersona: any;
  metrics?: {
    open_rate: string;
    response_rate: string;
    sentiment: string;
    personalization_score: string;
    quality_score: string;
  };
  suggestions?: string[];
}

const Workspace: React.FC<WorkspaceProps> = ({
  messages,
  selectedPersona,
  selectedTone,
  sequenceType,
  content,
  onPersonaChange,
  onSendMessage,
  onSequenceUpdate,
  onToneChange,
  onSequenceTypeChange,
  onMagicAction,
  onContentChange,
  onGenerateSequence,
  personas,
  currentPersona,
  metrics,
  suggestions
}) => {
  const [error, setError] = useState<string | null>(null);
  const [socket, setSocket] = useState<Socket | null>(null);

  useEffect(() => {
    const newSocket = io('http://localhost:3002', {
      reconnection: true,
      reconnectionAttempts: Infinity,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      timeout: 60000,
      transports: ['websocket', 'polling'],
      withCredentials: true
    });
    setSocket(newSocket);

    return () => {
      newSocket.close();
    };
  }, []);

  const handleAddStep = () => {
    const newStep: EmailStep = {
      subject: `Follow-up ${sequence.length + 1}`,
      body: "Hi {{answers.candidate_name}},\n\nI hope this email finds you well..."
    };
    const newSequence = [...sequence, newStep];
    onContentChange(JSON.stringify(newSequence, null, 2));
  };

  const handleApplySuggestion = (suggestion: string) => {
    try {
      if (socket?.connected) {
        socket.emit('apply_suggestion', {
          suggestion,
          sequence: content
        });
      } else {
        setError('Not connected to server');
      }
    } catch (e) {
      setError('Failed to apply suggestion');
      console.error('Apply suggestion error:', e);
    }
  };

  const handleToneCommand = (tone: string) => {
    // Extract tone from command (e.g., "/adjust_tone casual" -> "casual")
    const toneArg = tone.replace('/adjust_tone', '').trim().toLowerCase();
    
    // Validate tone
    const validTones = ['professional', 'casual', 'founder', 'friendly'];
    if (!validTones.includes(toneArg)) {
      setError(`Invalid tone. Available tones: ${validTones.join(', ')}`);
      return;
    }
    onToneChange(toneArg);
  };

  const handleSummarizeContext = () => {
    // Use the existing onMagicAction prop to handle context summarization
    onMagicAction('summarize_context');
  };

  const handleDownload = () => {
    try {
      const sequence = parseContent(content);
      
      // Create a formatted document
      let docContent = "# Recruiting Sequence\n\n";
      
      sequence.forEach((step, index) => {
        docContent += `### ${index === 0 ? 'Initial Outreach' : `Follow-up ${index}`} (Day ${index + 1})\n\n`;
        docContent += `${step.body}\n\n`;
      });

      // Create a blob and download
      const blob = new Blob([docContent], { type: 'text/markdown' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'recruiting_sequence.md';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (e) {
      setError('Failed to download sequence');
      console.error('Download error:', e);
    }
  };

  const handleRefresh = () => {
    try {
      onGenerateSequence();
    } catch (e) {
      setError('Failed to refresh sequence');
      console.error('Refresh error:', e);
    }
  };

  // Parse JSON content into EmailStep array
  const parseContent = (jsonString: string): EmailStep[] => {
    try {
      // Remove markdown code block syntax if present
      const cleanJson = jsonString.replace(/```json\n|\n```/g, '');
      return JSON.parse(cleanJson);
    } catch (e) {
      console.error('Failed to parse sequence:', e);
      return [];
    }
  };

  const sequence = parseContent(content);

  return (
    <Box sx={{ 
      height: 'calc(100vh - 56px)', // Account for top navbar
      display: 'flex',
      overflow: 'hidden'
    }}>
      {/* Chat Section */}
      <Box sx={{ 
        width: '40%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        borderRight: '1px solid #eaecf0',
        bgcolor: 'white',
        overflow: 'hidden'
      }}>
        {/* Chat Header */}
        <Box sx={{ 
          p: 3, 
          borderBottom: '1px solid #eaecf0',
          bgcolor: 'white',
          zIndex: 2,
          position: 'sticky',
          top: 0
        }}>
          <Stack spacing={1}>
            <Stack direction="row" spacing={1} alignItems="center">
              <Box component="span" sx={{ color: '#4F46E5', fontSize: '1.5rem' }}>⚡</Box>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Chat with Helix
              </Typography>
            </Stack>
            <Typography variant="body2" color="text.secondary">
              I'll help you craft the perfect recruiting sequence
            </Typography>
          </Stack>
        </Box>

        {/* Chat Messages Area */}
        <Box sx={{ 
          flexGrow: 1,
          minHeight: 0, // Important for flex child scrolling
          overflow: 'hidden',
          display: 'flex'
        }}>
          <ChatInterface
            messages={messages}
            onSendMessage={onSendMessage}
            persona={currentPersona}
            onGenerateSequence={onGenerateSequence}
            onToneChange={handleToneCommand}
            onSummarizeContext={handleSummarizeContext}
          />
        </Box>
      </Box>
      
      {/* Sequence Section */}
      <Box sx={{ 
        width: '60%',
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: 'white',
        overflow: 'hidden',
        borderLeft: '1px solid #eaecf0'
      }}>
        {/* Sequence Header */}
        <Box sx={{ 
          p: 3, 
          borderBottom: '1px solid #eaecf0',
          bgcolor: 'white',
          zIndex: 2,
          position: 'sticky',
          top: 0,
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)'
        }}>
          <Stack direction="row" spacing={2} alignItems="center">
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Recruiting Sequence
            </Typography>
            <Box sx={{ flexGrow: 1 }} />
            <IconButton
              onClick={handleRefresh}
              sx={{ 
                color: '#4F46E5',
                '&:hover': {
                  bgcolor: '#F5F3FF'
                }
              }}
              title="Regenerate sequence"
            >
              <RefreshIcon />
            </IconButton>
            <IconButton
              onClick={handleDownload}
              sx={{ 
                color: '#4F46E5',
                '&:hover': {
                  bgcolor: '#F5F3FF'
                }
              }}
              title="Download sequence"
            >
              <DownloadIcon />
            </IconButton>
          </Stack>
        </Box>

        {/* Sequence Content Area */}
        <Box sx={{ 
          flexGrow: 1,
          minHeight: 0, // Important for flex child scrolling
          overflow: 'auto',
          '&::-webkit-scrollbar': {
            width: '8px',
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
          background: `linear-gradient(to right, #f9fafb 1px, transparent 1px),
                      linear-gradient(to bottom, #f9fafb 1px, transparent 1px)`,
          backgroundSize: '20px 20px'
        }}>
          <Box sx={{ p: 3 }}>
            <Stack spacing={4}>
              {content && sequence.map((step, index) => (
                <Box 
                  key={index}
                  sx={{
                    p: 3,
                    borderRadius: 2,
                    bgcolor: '#f8f9fc',
                    border: '1px solid #eaecf0',
                    transition: 'all 0.2s ease-in-out',
                    '&:hover': {
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                      borderColor: '#4F46E5'
                    }
                  }}
                >
                  <Stack spacing={2}>
                    <Stack direction="row" spacing={1} alignItems="center">
                      <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                        {index === 0 ? 'Initial Outreach' : `Follow-up ${index}`}
                      </Typography>
                      <Chip 
                        label={`Day ${index + 1}`} 
                        size="small"
                        sx={{ 
                          bgcolor: '#E0E7FF',
                          color: '#4F46E5',
                          fontWeight: 500
                        }}
                      />
                    </Stack>
                    <TextField
                      fullWidth
                      multiline
                      minRows={4}
                      value={step.body}
                      onChange={(e) => {
                        const newSequence = [...sequence];
                        newSequence[index].body = e.target.value;
                        onContentChange(JSON.stringify(newSequence, null, 2));
                      }}
                      sx={{
                        '& .MuiOutlinedInput-root': {
                          bgcolor: 'white'
                        }
                      }}
                    />
                  </Stack>
                </Box>
              ))}

              <Button
                startIcon={<AddIcon />}
                onClick={handleAddStep}
                sx={{
                  color: '#4F46E5',
                  borderStyle: 'dashed',
                  borderWidth: 1,
                  borderColor: '#4F46E5',
                  borderRadius: 2,
                  p: 2,
                  '&:hover': { bgcolor: '#F5F3FF' }
                }}
              >
                Add Sequence Step
              </Button>

              {/* AI Suggestions Section */}
              <Box>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                  AI SUGGESTIONS
                </Typography>
                <Stack spacing={2}>
                  {suggestions && suggestions.map((suggestion, index) => (
                    <Box
                      key={index}
                      sx={{
                        p: 3,
                        borderRadius: 2,
                        bgcolor: '#F5F3FF',
                        border: '1px solid #E0E7FF'
                      }}
                    >
                      <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                        <Box component="span" sx={{ color: '#4F46E5' }}>💡</Box>
                        <Typography variant="subtitle2" sx={{ color: '#4F46E5' }}>
                          Suggestion {index + 1}
                        </Typography>
                        <Chip 
                          label="AI Generated" 
                          size="small"
                          sx={{ 
                            bgcolor: '#E0E7FF',
                            color: '#4F46E5',
                            height: 20
                          }}
                        />
                      </Stack>
                      <Typography variant="body2" sx={{ mb: 2, color: '#6B7280', fontStyle: 'italic' }}>
                        "{suggestion}"
                      </Typography>
                      <Button
                        variant="outlined"
                        size="small"
                        onClick={() => handleApplySuggestion(suggestion)}
                        sx={{
                          color: '#4F46E5',
                          borderColor: '#E0E7FF',
                          '&:hover': {
                            borderColor: '#4F46E5',
                            bgcolor: '#F5F3FF'
                          }
                        }}
                      >
                        Apply Suggestion
                      </Button>
                    </Box>
                  ))}
                  {(!suggestions || suggestions.length === 0) && (
                    <Box
                      sx={{
                        p: 3,
                        borderRadius: 2,
                        bgcolor: '#F5F3FF',
                        border: '1px solid #E0E7FF',
                        textAlign: 'center'
                      }}
                    >
                      <Typography variant="body2" sx={{ color: '#6B7280' }}>
                        Generate a sequence to get AI suggestions
                      </Typography>
                    </Box>
                  )}
                </Stack>
              </Box>

              <Box>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                  SEQUENCE ANALYTICS
                </Typography>
                <Stack spacing={2}>
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Typography variant="body1">Estimated open rate:</Typography>
                    <Typography variant="h6" sx={{ color: '#4F46E5' }}>{metrics?.open_rate || 'N/A'}</Typography>
                  </Stack>
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Typography variant="body1">Estimated response rate:</Typography>
                    <Typography variant="h6" sx={{ color: '#4F46E5' }}>{metrics?.response_rate || 'N/A'}</Typography>
                  </Stack>
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Typography variant="body1">Sentiment analysis:</Typography>
                    <Typography variant="h6" sx={{ 
                      color: metrics?.sentiment === 'Positive' ? '#16A34A' : 
                             metrics?.sentiment === 'Negative' ? '#DC2626' : '#4B5563'
                    }}>
                      {metrics?.sentiment || 'N/A'}
                    </Typography>
                  </Stack>
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Typography variant="body1">Personalization score:</Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="h6" sx={{ color: '#4F46E5' }}>
                        {metrics?.personalization_score || 'N/A'}
                      </Typography>
                      {metrics?.personalization_score && (
                        <Typography variant="body2" sx={{ color: '#6B7280' }}>/100</Typography>
                      )}
                    </Box>
                  </Stack>
                  <Stack direction="row" justifyContent="space-between" alignItems="center">
                    <Typography variant="body1">Quality score:</Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="h6" sx={{ color: '#4F46E5' }}>
                        {metrics?.quality_score || 'N/A'}
                      </Typography>
                      {metrics?.quality_score && (
                        <Typography variant="body2" sx={{ color: '#6B7280' }}>/100</Typography>
                      )}
                    </Box>
                  </Stack>
                </Stack>
              </Box>
            </Stack>
          </Box>
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
  );
};

export default Workspace;