import React from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Grid,
  Card,
  CardContent,
  CardMedia,
  CardActions,
  useTheme,
  useMediaQuery
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import CodeIcon from '@mui/icons-material/Code';
import SchoolIcon from '@mui/icons-material/School';
import GitHubIcon from '@mui/icons-material/GitHub';

const Home = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  const features = [
    {
      icon: <CodeIcon sx={{ fontSize: 40 }} />,
      title: 'Code Analysis',
      description: 'Analyze any codebase and understand its structure and patterns.'
    },
    {
      icon: <SchoolIcon sx={{ fontSize: 40 }} />,
      title: 'Beginner-Friendly Tutorials',
      description: 'Generate tutorials that explain complex concepts in simple terms.'
    },
    {
      icon: <GitHubIcon sx={{ fontSize: 40 }} />,
      title: 'GitHub Integration',
      description: 'Directly analyze GitHub repositories and generate tutorials.'
    }
  ];

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', py: 8 }}>
      <Container maxWidth="lg">
        {/* Hero Section */}
        <Box sx={{ textAlign: 'center', mb: 8 }}>
          <Typography variant="h2" component="h1" gutterBottom>
            Codebase Explainer
          </Typography>
          <Typography variant="h5" color="text.secondary" paragraph>
            Turn complex codebases into beginner-friendly tutorials with AI-powered analysis
          </Typography>
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate('/generate')}
            sx={{ mt: 2 }}
          >
            Get Started
          </Button>
        </Box>

        {/* Features Grid */}
        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid item xs={12} md={4} key={index}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
                    {feature.icon}
                  </Box>
                  <Typography gutterBottom variant="h5" component="h2">
                    {feature.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>

        {/* How It Works Section */}
        <Box sx={{ mt: 8, mb: 8 }}>
          <Typography variant="h3" gutterBottom align="center">
            How It Works
          </Typography>
          <Grid container spacing={4}>
            <Grid item xs={12} md={6}>
              <Typography variant="body1" paragraph>
                1. Enter a GitHub repository URL or upload your code
              </Typography>
              <Typography variant="body1" paragraph>
                2. Select your preferred language and configuration options
              </Typography>
              <Typography variant="body1" paragraph>
                3. Get a beginner-friendly tutorial with diagrams and code examples
              </Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box
                sx={{
                  height: '300px',
                  background: 'linear-gradient(45deg, #1976d2 30%, #dc004e 90%)',
                  borderRadius: 2,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  p: 4
                }}
              >
                <Typography variant="h4">
                  AI-Powered Analysis
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Box>

        {/* Demo Examples */}
        <Box sx={{ mt: 8 }}>
          <Typography variant="h3" gutterBottom align="center">
            Demo Examples
          </Typography>
          <Grid container spacing={4}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardMedia
                  component="img"
                  height="200"
                  image="/demo1.png"
                  alt="Example tutorial"
                />
                <CardContent>
                  <Typography variant="h5" gutterBottom>
                    Machine Learning Project
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    A comprehensive tutorial explaining a machine learning project
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button size="small">View Tutorial</Button>
                </CardActions>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardMedia
                  component="img"
                  height="200"
                  image="/demo2.png"
                  alt="Example tutorial"
                />
                <CardContent>
                  <Typography variant="h5" gutterBottom>
                    Web Application
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Step-by-step guide to understanding a web application architecture
                  </Typography>
                </CardContent>
                <CardActions>
                  <Button size="small">View Tutorial</Button>
                </CardActions>
              </Card>
            </Grid>
          </Grid>
        </Box>
      </Container>
    </Box>
  );
};

export default Home;
