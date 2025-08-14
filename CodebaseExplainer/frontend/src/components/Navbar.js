import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  useTheme,
  useMediaQuery
} from '@mui/material';
import { Link as RouterLink } from 'react-router-dom';

const Navbar = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <AppBar position="static">
      <Toolbar>
        <Typography
          variant="h6"
          component={RouterLink}
          to="/"
          sx={{
            flexGrow: 1,
            textDecoration: 'none',
            color: 'inherit',
            display: 'flex',
            alignItems: 'center',
            gap: 1
          }}
        >
          Codebase Explainer
        </Typography>

        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            color="inherit"
            component={RouterLink}
            to="/"
            sx={{
              '&.Mui-selected': {
                color: 'primary.main'
              }
            }}
          >
            Home
          </Button>
          <Button
            color="inherit"
            component={RouterLink}
            to="/generate"
            sx={{
              '&.Mui-selected': {
                color: 'primary.main'
              }
            }}
          >
            Generate Tutorial
          </Button>
          {!isMobile && (
            <Button
              color="inherit"
              component={RouterLink}
              to="/docs"
              sx={{
                '&.Mui-selected': {
                  color: 'primary.main'
                }
              }}
            >
              Documentation
            </Button>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
