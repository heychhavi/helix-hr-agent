import React from 'react';
import {
  Box,
  Paper,
  TextField,
  Typography,
  IconButton,
  Tooltip,
} from '@mui/material';
import SaveIcon from '@mui/icons-material/Save';
import ReactMarkdown from 'react-markdown';

interface WorkspaceProps {
  content: string;
  onChange: (content: string) => void;
}

const Workspace: React.FC<WorkspaceProps> = ({ content, onChange }) => {
  const handleChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange(event.target.value);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" sx={{ flex: 1 }}>
          Recruiting Sequence
        </Typography>
        <Tooltip title="Save">
          <IconButton color="primary">
            <SaveIcon />
          </IconButton>
        </Tooltip>
      </Box>
      <Paper sx={{ flex: 1, p: 2, display: 'flex', gap: 2 }}>
        <Box sx={{ flex: 1 }}>
          <TextField
            fullWidth
            multiline
            rows={20}
            variant="outlined"
            value={content}
            onChange={handleChange}
            placeholder="Your recruiting sequence will appear here..."
            sx={{ height: '100%' }}
          />
        </Box>
        <Box sx={{ flex: 1, p: 2, borderLeft: 1, borderColor: 'divider' }}>
          <Typography variant="subtitle1" gutterBottom>
            Preview
          </Typography>
          <Box sx={{ overflow: 'auto', height: 'calc(100% - 40px)' }}>
            <ReactMarkdown>{content || 'Preview will appear here...'}</ReactMarkdown>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default Workspace; 