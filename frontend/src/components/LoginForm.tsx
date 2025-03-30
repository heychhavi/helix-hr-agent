import React, { useState } from 'react';
import {
  Box,
  Stack,
  TextField,
  Button,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Link,
  Alert,
  SelectChangeEvent
} from '@mui/material';

interface LoginFormProps {
  onLogin: (userData: {
    email: string;
    password: string;
    name?: string;
    company?: {
      name: string;
      industry: string;
      size: string;
      description: string;
      website: string;
    };
  }) => void;
}

const COMPANY_SIZES = [
  '1-10',
  '11-50',
  '51-200',
  '201-500',
  '501-1000',
  '1000+'
];

const INDUSTRIES = [
  'Technology',
  'Healthcare',
  'Finance',
  'Education',
  'Manufacturing',
  'Retail',
  'Other'
];

const LoginForm: React.FC<LoginFormProps> = ({ onLogin }) => {
  const [isSignUp, setIsSignUp] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    companyName: '',
    industry: '',
    size: '',
    description: '',
    website: ''
  });
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Basic validation
    if (!formData.email || !formData.password) {
      setError('Please fill in all required fields');
      return;
    }

    if (isSignUp) {
      // Additional validation for signup
      if (!formData.name || !formData.companyName) {
        setError('Please fill in all required fields');
        return;
      }
    }

    // Submit form
    onLogin({
      email: formData.email,
      password: formData.password,
      ...(isSignUp && {
        name: formData.name,
        company: {
          name: formData.companyName,
          industry: formData.industry,
          size: formData.size,
          description: formData.description,
          website: formData.website
        }
      })
    });
  };

  const handleTextChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSelectChange = (e: SelectChangeEvent) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{
        maxWidth: 600,
        mx: 'auto',
        p: 3,
        bgcolor: 'white',
        borderRadius: 2,
        boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)'
      }}
    >
      <Stack spacing={3}>
        <Typography variant="h5" sx={{ fontWeight: 600 }}>
          {isSignUp ? 'Create Account' : 'Welcome Back'}
        </Typography>

        {error && (
          <Alert severity="error" onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <TextField
          name="email"
          label="Email"
          type="email"
          value={formData.email}
          onChange={handleTextChange}
          required
          fullWidth
        />

        <TextField
          name="password"
          label="Password"
          type="password"
          value={formData.password}
          onChange={handleTextChange}
          required
          fullWidth
        />

        {isSignUp && (
          <>
            <TextField
              name="name"
              label="Your Name"
              value={formData.name}
              onChange={handleTextChange}
              required
              fullWidth
            />

            <TextField
              name="companyName"
              label="Company Name"
              value={formData.companyName}
              onChange={handleTextChange}
              required
              fullWidth
            />

            <FormControl fullWidth>
              <InputLabel>Industry</InputLabel>
              <Select
                name="industry"
                value={formData.industry}
                label="Industry"
                onChange={handleSelectChange}
              >
                {INDUSTRIES.map(industry => (
                  <MenuItem key={industry} value={industry}>
                    {industry}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControl fullWidth>
              <InputLabel>Company Size</InputLabel>
              <Select
                name="size"
                value={formData.size}
                label="Company Size"
                onChange={handleSelectChange}
              >
                {COMPANY_SIZES.map(size => (
                  <MenuItem key={size} value={size}>
                    {size} employees
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <TextField
              name="description"
              label="Company Description"
              value={formData.description}
              onChange={handleTextChange}
              multiline
              rows={3}
              fullWidth
            />

            <TextField
              name="website"
              label="Company Website"
              value={formData.website}
              onChange={handleTextChange}
              fullWidth
            />
          </>
        )}

        <Button
          type="submit"
          variant="contained"
          size="large"
          sx={{
            bgcolor: '#4F46E5',
            '&:hover': {
              bgcolor: '#4338CA'
            }
          }}
        >
          {isSignUp ? 'Create Account' : 'Sign In'}
        </Button>

        <Box sx={{ textAlign: 'center' }}>
          <Link
            component="button"
            type="button"
            onClick={() => setIsSignUp(!isSignUp)}
            sx={{ color: '#4F46E5' }}
          >
            {isSignUp
              ? 'Already have an account? Sign in'
              : "Don't have an account? Sign up"}
          </Link>
        </Box>
      </Stack>
    </Box>
  );
};

export default LoginForm; 