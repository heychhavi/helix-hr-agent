import React from 'react';
import { Box, Stack, Button, ButtonGroup, Select, MenuItem, FormControl, InputLabel, TextField, Typography } from '@mui/material';
import { ContentCopy, Timer, EmojiEmotions } from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';

interface WorkspaceProps {
  content: string;
  onChange: (content: string) => void;
  onToneChange: (tone: string) => void;
  onSequenceTypeChange: (type: string) => void;
  onMagicAction: (action: string) => void;
  selectedTone: string;
  sequenceType: string;
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
  const handleChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange(event.target.value);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column', p: 2 }}>
      <Stack direction="row" spacing={2} sx={{ mb: 2 }}>
        <FormControl size="small" sx={{ minWidth: 200 }}>
          <InputLabel>Sequence Type</InputLabel>
          <Select
            value={sequenceType}
            label="Sequence Type"
            onChange={(e) => onSequenceTypeChange(e.target.value)}
          >
            <MenuItem value="passive">Passive Candidate</MenuItem>
            <MenuItem value="aggressive">Aggressive Outreach</MenuItem>
            <MenuItem value="soft">Soft Ping</MenuItem>
          </Select>
        </FormControl>

        <FormControl size="small" sx={{ minWidth: 150 }}>
          <InputLabel>Tone</InputLabel>
          <Select
            value={selectedTone}
            label="Tone"
            onChange={(e) => onToneChange(e.target.value)}
          >
            <MenuItem value="professional">Professional</MenuItem>
            <MenuItem value="friendly">Friendly</MenuItem>
            <MenuItem value="founder">Founder-style</MenuItem>
            <MenuItem value="playful">Playful</MenuItem>
          </Select>
        </FormControl>
      </Stack>

      <ButtonGroup variant="outlined" size="small" sx={{ mb: 2 }}>
        <Button 
          startIcon={<ContentCopy />}
          onClick={() => onMagicAction('shorter')}
        >
          Make Shorter
        </Button>
        <Button 
          startIcon={<Timer />}
          onClick={() => onMagicAction('urgent')}
        >
          Add Urgency
        </Button>
        <Button 
          startIcon={<EmojiEmotions />}
          onClick={() => onMagicAction('funny')}
        >
          Make it Funny
        </Button>
      </ButtonGroup>

      <Box sx={{ 
        display: 'flex', 
        gap: 2, 
        flexGrow: 1,
        height: 0 // Required for proper scrolling
      }}>
        <Box sx={{ 
          width: '50%',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            Edit
          </Typography>
          <TextField
            multiline
            fullWidth
            variant="outlined"
            value={content}
            onChange={handleChange}
            sx={{ 
              flexGrow: 1,
              '& .MuiInputBase-root': {
                height: '100%',
                '& textarea': {
                  height: '100% !important'
                }
              }
            }}
          />
        </Box>

        <Box sx={{ 
          width: '50%',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <Typography variant="subtitle2" sx={{ mb: 1 }}>
            Preview
          </Typography>
          <Box sx={{ 
            flexGrow: 1,
            overflow: 'auto',
            p: 2,
            bgcolor: '#f8f9fa',
            borderRadius: 1
          }}>
            <ReactMarkdown>{typeof content === 'string' ? content : JSON.stringify(content, null, 2)}</ReactMarkdown>
          </Box>
        </Box>
      </Box>
    </Box>
  );
};

export default Workspace;