import React from 'react';
import { Box, Stack, Typography, TextField, Button, Chip, IconButton } from '@mui/material';
import { Add as AddIcon, Refresh as RefreshIcon, Download as DownloadIcon } from '@mui/icons-material';

interface WorkspaceProps {
  content: string;
  onChange: (content: string) => void;
  onToneChange: (tone: string) => void;
  onSequenceTypeChange: (type: string) => void;
  onMagicAction: (action: string) => void;
  selectedTone: string;
  sequenceType: string;
}

interface EmailStep {
  subject: string;
  body: string;
}

const Workspace: React.FC<WorkspaceProps> = ({
  content,
  onChange,
  onToneChange,
  onSequenceTypeChange,
  onMagicAction,
  selectedTone,
  sequenceType
}) => {
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

  const handleAddStep = () => {
    const newStep: EmailStep = {
      subject: `Follow-up ${sequence.length + 1}`,
      body: "Hi {{answers.candidate_name}},\n\nI hope this email finds you well..."
    };
    const newSequence = [...sequence, newStep];
    onChange(JSON.stringify(newSequence, null, 2));
  };

  const handleApplySuggestion = () => {
    onMagicAction('enhance_personalization');
  };

  return (
    <Box sx={{ p: 3, height: 'calc(100vh - 140px)', overflow: 'auto' }}>
      <Stack spacing={4}>
        <Box>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
            SEQUENCE STEPS
          </Typography>
          <Stack spacing={3}>
            {sequence.map((step, index) => (
              <Box 
                key={index}
                sx={{
                  p: 3,
                  borderRadius: 2,
                  bgcolor: '#f8f9fc',
                  border: '1px solid #eaecf0'
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
                    label="Subject"
                    value={step.subject}
                    onChange={(e) => {
                      const newSequence = [...sequence];
                      newSequence[index].subject = e.target.value;
                      onChange(JSON.stringify(newSequence, null, 2));
                    }}
                    sx={{
                      '& .MuiOutlinedInput-root': {
                        bgcolor: 'white'
                      }
                    }}
                  />
                  <TextField
                    fullWidth
                    multiline
                    minRows={4}
                    label="Email Body"
                    value={step.body}
                    onChange={(e) => {
                      const newSequence = [...sequence];
                      newSequence[index].body = e.target.value;
                      onChange(JSON.stringify(newSequence, null, 2));
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
                '&:hover': { bgcolor: '#F5F3FF' }
              }}
            >
              Add Step
            </Button>
          </Stack>
        </Box>

        <Box>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
            AI SUGGESTIONS
          </Typography>
          <Box
            sx={{
              p: 3,
              borderRadius: 2,
              bgcolor: '#F5F3FF',
              border: '1px solid #E0E7FF'
            }}
          >
            <Typography variant="subtitle2" sx={{ color: '#4F46E5', mb: 1 }}>
              Suggested Follow-up
            </Typography>
            <Typography variant="body2" sx={{ mb: 2, color: '#6B7280' }}>
              Consider adding a more personalized touch by mentioning specific projects or technologies that align with their experience.
            </Typography>
            <Button
              variant="outlined"
              size="small"
              onClick={handleApplySuggestion}
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
        </Box>

        <Box>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
            SEQUENCE ANALYTICS
          </Typography>
          <Stack direction="row" spacing={2}>
            <Box
              sx={{
                p: 2,
                borderRadius: 2,
                bgcolor: '#F0FDF4',
                border: '1px solid #DCFCE7',
                flex: 1
              }}
            >
              <Typography variant="subtitle2" sx={{ color: '#16A34A' }}>
                Estimated Open Rate
              </Typography>
              <Typography variant="h4" sx={{ color: '#16A34A', fontWeight: 600 }}>
                65%
              </Typography>
            </Box>
            <Box
              sx={{
                p: 2,
                borderRadius: 2,
                bgcolor: '#F0F9FF',
                border: '1px solid #DBEAFE',
                flex: 1
              }}
            >
              <Typography variant="subtitle2" sx={{ color: '#2563EB' }}>
                Response Rate
              </Typography>
              <Typography variant="h4" sx={{ color: '#2563EB', fontWeight: 600 }}>
                28%
              </Typography>
            </Box>
          </Stack>
        </Box>

        <Stack direction="row" spacing={1} sx={{ pt: 2 }}>
          <IconButton
            onClick={() => onMagicAction('refresh')}
            sx={{
              color: '#4F46E5',
              '&:hover': { bgcolor: '#F5F3FF' }
            }}
          >
            <RefreshIcon />
          </IconButton>
          <IconButton
            onClick={() => onMagicAction('download')}
            sx={{
              color: '#4F46E5',
              '&:hover': { bgcolor: '#F5F3FF' }
            }}
          >
            <DownloadIcon />
          </IconButton>
        </Stack>
      </Stack>
    </Box>
  );
};

export default Workspace;