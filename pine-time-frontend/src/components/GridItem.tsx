import React from 'react';
import { Grid, GridProps } from '@mui/material';

/**
 * A wrapper component for Material-UI Grid that properly handles both container and item props.
 * This resolves TypeScript errors when using both container and item props together.
 */
type GridItemProps = GridProps & {
  // We're explicitly allowing both item and container props
  item?: boolean;
  container?: boolean;
};

const GridItem: React.FC<GridItemProps> = (props) => {
  // We're using a regular Grid component but with proper typing
  // This is a workaround for TypeScript errors when using both container and item props
  return <Grid {...props} />;
};

export default GridItem;
