import React, { useState } from 'react';
import {
  Container,
  Box,
  TextField,
  Button,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  CircularProgress,
  Chip,
  Divider,
  Paper
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import axios from 'axios';
import MermaidDiagram from '../components/MermaidDiagram';

const Tutorial = () => {
  const navigate = useNavigate();
  const [repoUrl, setRepoUrl] = useState('');
  const [language, setLanguage] = useState('english');
  const [includePatterns, setIncludePatterns] = useState(['*.py', '*.js']);
  const [excludePatterns, setExcludePatterns] = useState(['tests/*', 'docs/*']);
  const [maxFileSize, setMaxFileSize] = useState(100000);
  const [error, setError] = useState('');
  const [preview, setPreview] = useState(null);

  const { mutate: generateTutorial, isLoading } = useMutation({
    mutationFn: async () => {
      const response = await axios.post('http://localhost:8000/api/generate-tutorial', {
        repoUrl,
        language,
        include_patterns: includePatterns,
        exclude_patterns: excludePatterns,
        max_file_size: maxFileSize
      });
      return response.data;
    },
    onSuccess: (data) => {
      navigate(`/tutorial/${data.id}`);
    },
    onError: (error) => {
      setError(error.response?.data?.message || 'Failed to generate tutorial');
    }
  });

  const handleGenerate = () => {
    if (!repoUrl.trim()) {
      setError('Please enter a repository URL');
      return;
    }

    setError('');
    generateTutorial();
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', py: 8 }}>
      <Container maxWidth="lg">
        <Box sx={{ mb: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom>
            Generate Tutorial
          </Typography>
          <Typography variant="subtitle1" color="text.secondary" paragraph>
            Create a beginner-friendly tutorial for your codebase
          </Typography>
        </Box>

        <Paper sx={{ p: 4 }}>
          {/* Repository URL */}
          <TextField
            fullWidth
            label="GitHub Repository URL"
            variant="outlined"
            value={repoUrl}
            onChange={(e) => setRepoUrl(e.target.value)}
            placeholder="https://github.com/username/repository"
            margin="normal"
          />

          {/* Language Selection */}
          <FormControl fullWidth margin="normal">
            <InputLabel>Language</InputLabel>
            <Select
              value={language}
              label="Language"
              onChange={(e) => setLanguage(e.target.value)}
            >
              <MenuItem value="english">English</MenuItem>
              <MenuItem value="spanish">Spanish</MenuItem>
              <MenuItem value="french">French</MenuItem>
              <MenuItem value="german">German</MenuItem>
            </Select>
          </FormControl>

          {/* File Patterns */}
          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 2 }}>
            <Typography variant="subtitle1">Include Patterns:</Typography>
            {includePatterns.map((pattern, index) => (
              <Chip
                key={index}
                label={pattern}
                onDelete={() => {
                  const newPatterns = [...includePatterns];
                  newPatterns.splice(index, 1);
                  setIncludePatterns(newPatterns);
                }}
                sx={{ mr: 1 }}
              />
            ))}
            <Button
              variant="outlined"
              size="small"
              onClick={() => {
                const newPattern = prompt('Enter new pattern (e.g., *.py)');
                if (newPattern) {
                  setIncludePatterns([...includePatterns, newPattern]);
                }
              }}
            >
              Add Pattern
            </Button>
          </Box>

          <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', mb: 2 }}>
            <Typography variant="subtitle1">Exclude Patterns:</Typography>
            {excludePatterns.map((pattern, index) => (
              <Chip
                key={index}
                label={pattern}
                onDelete={() => {
                  const newPatterns = [...excludePatterns];
                  newPatterns.splice(index, 1);
                  setExcludePatterns(newPatterns);
                }}
                sx={{ mr: 1 }}
              />
            ))}
            <Button
              variant="outlined"
              size="small"
              onClick={() => {
                const newPattern = prompt('Enter new pattern (e.g., tests/*)');
                if (newPattern) {
                  setExcludePatterns([...excludePatterns, newPattern]);
                }
              }}
            >
              Add Pattern
            </Button>
          </Box>

          {/* File Size */}
          <TextField
            fullWidth
            label="Max File Size (bytes)"
            variant="outlined"
            type="number"
            value={maxFileSize}
            onChange={(e) => setMaxFileSize(parseInt(e.target.value) || 100000)}
            margin="normal"
          />

          {/* Generate Button */}
          <Button
            variant="contained"
            size="large"
            onClick={handleGenerate}
            disabled={isLoading}
            sx={{ mt: 2 }}
          >
            {isLoading ? (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <CircularProgress size={20} color="inherit" />
                <span>Generating Tutorial...</span>
              </Box>
            ) : (
              'Generate Tutorial'
            )}
          </Button>

          {/* Error Message */}
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}

          {/* Preview */}
          {preview && (
            <Box sx={{ mt: 4 }}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h5" gutterBottom>
                Preview
              </Typography>
              <Box sx={{ p: 2, bgcolor: 'background.paper' }}>
                <MermaidDiagram diagram={preview.diagram} />
                <Typography variant="body1" sx={{ mt: 2 }}>
                  {preview.content}
                </Typography>
              </Box>
            </Box>
          )}
        </Paper>
      </Container>
    </Box>
  );
};

export default Tutorial;
