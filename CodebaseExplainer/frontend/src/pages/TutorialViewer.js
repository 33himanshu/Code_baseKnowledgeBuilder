import React from 'react';
import {
  Container,
  Box,
  Typography,
  Paper,
  Tabs,
  Tab,
  Button,
  IconButton,
  Menu,
  MenuItem,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Code as CodeIcon,
  Share as ShareIcon,
  Download as DownloadIcon,
  MoreVert as MoreIcon
} from '@mui/icons-material';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import MermaidDiagram from '../components/MermaidDiagram';
import CodeSnippet from '../components/CodeSnippet';

const TutorialViewer = () => {
  const { id } = useParams();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [tab, setTab] = useState(0);
  const [menuAnchor, setMenuAnchor] = useState(null);

  const { data: tutorial, isLoading } = useQuery({
    queryKey: ['tutorial', id],
    queryFn: async () => {
      const response = await axios.get(`http://localhost:8000/api/tutorials/${id}`);
      return response.data;
    }
  });

  const handleTabChange = (event, newValue) => {
    setTab(newValue);
  };

  const handleShare = () => {
    // Implementation for sharing
  };

  const handleDownload = () => {
    // Implementation for downloading
  };

  const handleMenuClick = (event) => {
    setMenuAnchor(event.currentTarget);
  };

  const handleCloseMenu = () => {
    setMenuAnchor(null);
  };

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '80vh' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', py: 8 }}>
      <Container maxWidth="lg">
        <Box sx={{ mb: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom>
            {tutorial?.title || 'Tutorial'}
          </Typography>
          <Typography variant="subtitle1" color="text.secondary" paragraph>
            Generated on {new Date(tutorial?.generated_at).toLocaleDateString()}
          </Typography>
        </Box>

        <Paper sx={{ p: 4 }}>
          {/* Header Actions */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Box>
              <Button
                variant="outlined"
                startIcon={<ShareIcon />}
                onClick={handleShare}
              >
                Share
              </Button>
              <Button
                variant="outlined"
                startIcon={<DownloadIcon />}
                onClick={handleDownload}
                sx={{ ml: 2 }}
              >
                Download
              </Button>
            </Box>
            <IconButton
              size="small"
              onClick={handleMenuClick}
              sx={{ ml: 1 }}
            >
              <MoreIcon />
            </IconButton>
          </Box>

          {/* Menu */}
          <Menu
            anchorEl={menuAnchor}
            open={Boolean(menuAnchor)}
            onClose={handleCloseMenu}
          >
            <MenuItem onClick={handleShare}>Share</MenuItem>
            <MenuItem onClick={handleDownload}>Download</MenuItem>
          </Menu>

          {/* Tabs */}
          <Tabs
            value={tab}
            onChange={handleTabChange}
            sx={{ mb: 2 }}
          >
            <Tab label="Chapters" />
            <Tab label="Diagrams" />
            <Tab label="Code Snippets" />
          </Tabs>

          {/* Content */}
          <Box sx={{ mt: 2 }}>
            {tab === 0 && (
              <Box>
                {tutorial?.chapters?.map((chapter, index) => (
                  <Paper
                    key={index}
                    sx={{
                      p: 3,
                      mb: 3,
                      bgcolor: 'background.paper'
                    }}
                  >
                    <Typography variant="h4" gutterBottom>
                      {chapter.title}
                    </Typography>
                    <Typography variant="body1">
                      {chapter.content}
                    </Typography>
                  </Paper>
                ))}
              </Box>
            )}

            {tab === 1 && (
              <Box>
                {tutorial?.diagrams?.map((diagram, index) => (
                  <Paper
                    key={index}
                    sx={{
                      p: 3,
                      mb: 3,
                      bgcolor: 'background.paper'
                    }}
                  >
                    <Typography variant="h5" gutterBottom>
                      {diagram.title}
                    </Typography>
                    <MermaidDiagram diagram={diagram.content} />
                    <Typography variant="body1" sx={{ mt: 2 }}>
                      {diagram.description}
                    </Typography>
                  </Paper>
                ))}
              </Box>
            )}

            {tab === 2 && (
              <Box>
                {tutorial?.code_snippets?.map((snippet, index) => (
                  <Paper
                    key={index}
                    sx={{
                      p: 3,
                      mb: 3,
                      bgcolor: 'background.paper'
                    }}
                  >
                    <Typography variant="h5" gutterBottom>
                      {snippet.title}
                    </Typography>
                    <CodeSnippet
                      code={snippet.code}
                      language={snippet.language}
                      description={snippet.description}
                    />
                  </Paper>
                ))}
              </Box>
            )}
          </Box>
        </Paper>
      </Container>
    </Box>
  );
};

export default TutorialViewer;
