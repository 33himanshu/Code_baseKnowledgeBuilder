import React from 'react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { a11yDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import {
  Paper,
  Typography,
  IconButton,
  Box,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Copy as CopyIcon,
  ExternalLink as ExternalLinkIcon
} from '@mui/icons-material';

const CodeSnippet = ({ code, language, description }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [copied, setCopied] = React.useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Paper
      sx={{
        p: 3,
        bgcolor: 'background.paper',
        borderRadius: 2
      }}
    >
      {description && (
        <Typography variant="body2" color="text.secondary" paragraph>
          {description}
        </Typography>
      )}
      <Box sx={{ position: 'relative' }}>
        <Box
          sx={{
            position: 'absolute',
            right: 2,
            top: 2,
            display: 'flex',
            gap: 1
          }}
        >
          <IconButton
            size="small"
            onClick={handleCopy}
            title="Copy code"
          >
            <CopyIcon color={copied ? 'success' : 'inherit'} />
          </IconButton>
          <IconButton
            size="small"
            title="View in new window"
            onClick={() => window.open(`data:text/plain;charset=utf-8,${encodeURIComponent(code)}`, '_blank')}
          >
            <ExternalLinkIcon />
          </IconButton>
        </Box>
        <SyntaxHighlighter
          language={language || 'python'}
          style={a11yDark}
          showLineNumbers
          wrapLines
          customStyle={{
            borderRadius: '8px',
            fontSize: '14px',
            padding: '1rem'
          }}
        >
          {code}
        </SyntaxHighlighter>
      </Box>
    </Paper>
  );
};

export default CodeSnippet;
