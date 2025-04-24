import React, { Suspense } from 'react';
import { Box, CircularProgress, Typography } from '@mui/material';

/**
 * Loading component shown while lazy-loaded routes are being fetched
 */
const RouteLoadingFallback: React.FC<{ pageName?: string }> = ({ pageName }) => (
  <Box
    sx={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '50vh',
      gap: 2,
    }}
  >
    <CircularProgress
      size={40}
      thickness={4}
      sx={{ color: '#2E7D32' }}
    />
    <Typography variant="body1" color="textSecondary">
      {pageName ? `Loading ${pageName}...` : 'Loading page...'}
    </Typography>
  </Box>
);

/**
 * Component that wraps lazy-loaded routes with a Suspense boundary and loading fallback
 */
interface LazyRouteProps {
  component: React.LazyExoticComponent<React.ComponentType<any>>;
  pageName?: string;
}

const LazyRoute: React.FC<LazyRouteProps> = ({ component: Component, pageName }) => {
  return (
    <Suspense fallback={<RouteLoadingFallback pageName={pageName} />}>
      <Component />
    </Suspense>
  );
};

export default LazyRoute;
