import React, { useState } from 'react';
import { Box, Button, Typography, keyframes, Select, MenuItem, FormControl, InputLabel, Stack } from '@mui/material';
import { styled } from '@mui/material/styles';

const fadeIn = keyframes`
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const scaleIn = keyframes`
  from {
    transform: scale(0.8);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
`;

const AnimatedBox = styled(Box)`
  animation: ${fadeIn} 1s ease-out;
`;

const LogoBox = styled(Box)`
  animation: ${scaleIn} 1.2s ease-out;
`;

const GradientText = styled(Typography)`
  background: linear-gradient(45deg, #2196F3 30%, #21CBF3 90%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
`;

const PERSONAS = [
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

interface LandingPageProps {
  onGetStarted: (persona: string) => void;
}

const LandingPage: React.FC<LandingPageProps> = ({ onGetStarted }) => {
  const [selectedPersona, setSelectedPersona] = useState('corporate_pro');

  const handleGetStarted = () => {
    onGetStarted(selectedPersona);
  };

  return (
    <Box
      sx={{
        height: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: '#fafafa',
        gap: 4,
      }}
    >
      <LogoBox>
        <GradientText variant="h1" sx={{ fontSize: '4.5rem', fontWeight: 'bold', mb: 2 }}>
          Helix
        </GradientText>
      </LogoBox>
      
      <AnimatedBox sx={{ textAlign: 'center', maxWidth: '600px', px: 3 }}>
        <Typography variant="h5" color="text.secondary" sx={{ mb: 4 }}>
          Your AI-powered recruiting assistant that helps find and engage top talent through intelligent workflows
        </Typography>
        
        <Stack spacing={3} alignItems="center">
          <FormControl sx={{ minWidth: 300 }}>
            <InputLabel>Select Your Persona</InputLabel>
            <Select
              value={selectedPersona}
              label="Select Your Persona"
              onChange={(e) => setSelectedPersona(e.target.value)}
              sx={{
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#2196F3',
                },
                '&:hover .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#21CBF3',
                },
              }}
            >
              {PERSONAS.map((persona) => (
                <MenuItem key={persona.id} value={persona.id}>
                  {persona.emoji} {persona.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Button
            variant="contained"
            size="large"
            onClick={handleGetStarted}
            sx={{
              px: 6,
              py: 2,
              fontSize: '1.2rem',
              borderRadius: '30px',
              background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
              boxShadow: '0 3px 5px 2px rgba(33, 203, 243, .3)',
              '&:hover': {
                background: 'linear-gradient(45deg, #1976D2 30%, #21CBF3 90%)',
                transform: 'scale(1.05)',
                transition: 'transform 0.2s',
              },
            }}
          >
            Get Started
          </Button>
        </Stack>
      </AnimatedBox>
      
      <Box
        sx={{
          position: 'absolute',
          bottom: 24,
          display: 'flex',
          gap: 2,
          opacity: 0.7,
        }}
      >
        <Typography variant="body2" color="text.secondary">
          Powered by AI
        </Typography>
        <Typography variant="body2" color="text.secondary">
          •
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Built for Recruiters
        </Typography>
      </Box>
    </Box>
  );
};

export default LandingPage; 