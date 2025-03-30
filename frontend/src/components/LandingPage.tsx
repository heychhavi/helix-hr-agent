import React, { useState } from 'react';
import { Box, Button, Typography, Stack, Card, CardContent, Select, MenuItem, FormControl, InputLabel } from '@mui/material';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';

const PERSONAS = [
  {
    id: 'corporate_pro',
    name: 'Corporate Professional',
    emoji: '👔',
    style: 'Formal and structured outreach',
    description: 'Specializes in formal, professional communication with a focus on corporate excellence.',
    tone: 'professional',
    sequenceType: 'passive'
  },
  {
    id: 'startup_founder',
    name: 'Startup Founder',
    emoji: '🚀',
    style: 'Direct and passionate outreach',
    description: 'Brings startup energy and vision, focusing on growth opportunities.',
    tone: 'founder',
    sequenceType: 'aggressive'
  },
  {
    id: 'friendly_recruiter',
    name: 'Friendly Recruiter',
    emoji: '😊',
    style: 'Warm and personable approach',
    description: 'Creates welcoming, personalized messages that build genuine connections.',
    tone: 'friendly',
    sequenceType: 'soft'
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
    <Box sx={{ 
      minHeight: '100vh', 
      bgcolor: 'white', 
      position: 'relative', 
      overflow: 'hidden',
      perspective: '1000px'  // Enable 3D perspective
    }}>
      {/* Header */}
      <Box sx={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center', 
        p: 3,
        position: 'relative',
        zIndex: 2
      }}>
        <Stack direction="row" spacing={1} alignItems="center">
          <Typography variant="h6" sx={{ 
            fontWeight: 600, 
            color: '#4F46E5',
            fontSize: '1.5rem'
          }}>
            Helix
          </Typography>
        </Stack>
        <Button variant="text" sx={{ color: '#111827' }}>
          Login
        </Button>
      </Box>

      {/* Main Content */}
      <Box sx={{ 
        maxWidth: 1200, 
        mx: 'auto', 
        px: 4, 
        pt: 8,
        position: 'relative',
        zIndex: 2,
        transform: 'translateZ(50px)',  // 3D effect
        '& > *': {
          transform: 'translateZ(30px)'  // Nested 3D effect
        }
      }}>
        <Box sx={{ maxWidth: 800, mb: 8 }}>
          <Typography variant="h1" sx={{ 
            fontSize: { xs: '2.5rem', md: '3.5rem' }, 
            fontWeight: 600,
            color: '#111827',
            mb: 3,
            textShadow: '2px 2px 4px rgba(0,0,0,0.1)'  // 3D text effect
          }}>
            The AI-Powered Recruiting Assistant
          </Typography>
          <Typography variant="h5" sx={{ 
            color: '#6B7280',
            mb: 4,
            maxWidth: 600
          }}>
            Transform your recruiting outreach with the power of AI. Helix helps you craft personalized messages, automate follow-ups, and engage top talent effectively.
          </Typography>

          <FormControl sx={{ minWidth: 300, mb: 4 }}>
            <InputLabel>Select Your Persona</InputLabel>
            <Select
              value={selectedPersona}
              label="Select Your Persona"
              onChange={(e) => setSelectedPersona(e.target.value)}
              sx={{
                bgcolor: 'white',
                boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)',
                '& .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#4F46E5',
                },
                '&:hover .MuiOutlinedInput-notchedOutline': {
                  borderColor: '#4338CA',
                },
                transform: 'translateZ(40px)',  // 3D effect
              }}
            >
              {PERSONAS.map((persona) => (
                <MenuItem key={persona.id} value={persona.id}>
                  {persona.emoji} {persona.name} - {persona.style}
                </MenuItem>
              ))}
            </Select>
          </FormControl>

          <Stack direction="row" spacing={2}>
            <Button 
              variant="contained" 
              size="large"
              onClick={handleGetStarted}
              endIcon={<ArrowForwardIcon />}
              sx={{
                bgcolor: '#4F46E5',
                '&:hover': { 
                  bgcolor: '#4338CA',
                  transform: 'translateZ(60px) scale(1.05)'  // 3D hover effect
                },
                px: 4,
                py: 1.5,
                borderRadius: 2,
                transition: 'all 0.3s ease',
                transform: 'translateZ(40px)',  // 3D effect
                boxShadow: '0 10px 20px -5px rgba(79, 70, 229, 0.4)'
              }}
            >
              Get Started
            </Button>
            <Button 
              variant="outlined" 
              size="large"
              sx={{
                color: '#4F46E5',
                borderColor: '#4F46E5',
                '&:hover': { 
                  borderColor: '#4338CA',
                  bgcolor: '#EEF2FF',
                  transform: 'translateZ(60px) scale(1.05)'  // 3D hover effect
                },
                px: 4,
                py: 1.5,
                borderRadius: 2,
                transition: 'all 0.3s ease',
                transform: 'translateZ(40px)',  // 3D effect
              }}
            >
              View Demo
            </Button>
          </Stack>
        </Box>

        {/* Feature Cards */}
        <Box sx={{ 
          display: 'grid', 
          gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' }, 
          gap: 4,
          '& > *': {
            transition: 'transform 0.3s ease',
            '&:hover': {
              transform: 'translateZ(80px) scale(1.05)'  // 3D hover effect
            }
          }
        }}>
          <Card sx={{ 
            bgcolor: 'white', 
            boxShadow: '0px 10px 20px -5px rgba(0, 0, 0, 0.1)',
            borderRadius: 2,
            transform: 'translateZ(60px)'  // 3D effect
          }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                Smart Outreach
              </Typography>
              <Typography variant="body2" color="text.secondary">
                AI-generated personalized messages
              </Typography>
            </CardContent>
          </Card>
          <Card sx={{ 
            bgcolor: 'white', 
            boxShadow: '0px 10px 20px -5px rgba(0, 0, 0, 0.1)',
            borderRadius: 2,
            transform: 'translateZ(60px)'  // 3D effect
          }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                Sequence Builder
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Create multi-touch campaigns
              </Typography>
            </CardContent>
          </Card>
          <Card sx={{ 
            bgcolor: 'white', 
            boxShadow: '0px 10px 20px -5px rgba(0, 0, 0, 0.1)',
            borderRadius: 2,
            transform: 'translateZ(60px)'  // 3D effect
          }}>
            <CardContent>
              <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                Talent Insights
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Understand response patterns
              </Typography>
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Gradient Sphere */}
      <Box
        sx={{
          position: 'absolute',
          top: '50%',
          right: '-20%',
          transform: 'translateY(-50%) translateZ(-100px)',  // 3D effect
          width: '80%',
          paddingBottom: '80%',
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(79, 70, 229, 0.2) 0%, rgba(79, 70, 229, 0.1) 50%, rgba(79, 70, 229, 0) 100%)',
          filter: 'blur(40px)',
          animation: 'float 6s ease-in-out infinite',  // Floating animation
          '@keyframes float': {
            '0%, 100%': {
              transform: 'translateY(-50%) translateZ(-100px)',
            },
            '50%': {
              transform: 'translateY(-45%) translateZ(-80px)',
            },
          },
          zIndex: 1
        }}
      />
    </Box>
  );
};

export default LandingPage; 