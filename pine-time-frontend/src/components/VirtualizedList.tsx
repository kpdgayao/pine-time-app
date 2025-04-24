import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Box } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import useMediaQuery from '@mui/material/useMediaQuery';

interface VirtualizedListProps<T = any> {
  items: T[];
  renderItem: (item: T, index: number) => React.ReactNode;
  itemHeight?: number;
  overscan?: number;
  gap?: number;
  gridColumns?: { xs?: number; sm?: number; md?: number; lg?: number; xl?: number };
  containerStyle?: React.CSSProperties;
  onEndReached?: () => void;
  endReachedThreshold?: number;
  keyExtractor?: (item: T, index: number) => string;
}

function VirtualizedList<T = any>({
  items,
  renderItem,
  itemHeight = 350, // Default height for an item
  overscan = 5, // Number of items to render beyond visible area
  gap = 16,
  gridColumns = { xs: 1, sm: 2, md: 3, lg: 4, xl: 4 },
  containerStyle = {},
  onEndReached,
  endReachedThreshold = 200,
  keyExtractor = (_, index) => `virtualized-item-${index}`,
}: VirtualizedListProps<T>) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [visibleRange, setVisibleRange] = useState({ start: 0, end: 20 });
  const [containerWidth, setContainerWidth] = useState(0);
  const theme = useTheme();
  
  // Determine columns based on current breakpoint
  const isXs = useMediaQuery(theme.breakpoints.only('xs'));
  const isSm = useMediaQuery(theme.breakpoints.only('sm'));
  const isMd = useMediaQuery(theme.breakpoints.only('md'));
  const isLg = useMediaQuery(theme.breakpoints.only('lg'));
  
  const getColumns = useCallback(() => {
    if (isXs) return gridColumns.xs || 1;
    if (isSm) return gridColumns.sm || 2;
    if (isMd) return gridColumns.md || 3;
    if (isLg) return gridColumns.lg || 4;
    return gridColumns.xl || 4;
  }, [isXs, isSm, isMd, isLg, gridColumns]);
  
  const columns = getColumns();
  
  // Calculate item width based on container width, columns, and gap
  const getItemWidth = useCallback(() => {
    if (!containerWidth) return '100%';
    return `calc((100% - ${gap * (columns - 1)}px) / ${columns})`;
  }, [containerWidth, columns, gap]);
  
  // Calculate total height of the list
  const getTotalHeight = useCallback(() => {
    const rows = Math.ceil(items.length / columns);
    return rows * (itemHeight + gap) - gap;
  }, [items.length, columns, itemHeight, gap]);
  
  // Update visible range when scroll position changes
  const updateVisibleRange = useCallback(() => {
    if (!containerRef.current) return;
    
    const scrollTop = window.scrollY;
    
    const viewportHeight = window.innerHeight;
    const rowHeight = itemHeight + gap;
    
    // Calculate visible rows
    const startRow = Math.floor(scrollTop / rowHeight);
    const endRow = Math.ceil((scrollTop + viewportHeight) / rowHeight);
    
    // Calculate visible items
    const startIndex = Math.max(0, startRow * columns - overscan);
    const endIndex = Math.min(items.length, (endRow + 1) * columns + overscan);
    
    setVisibleRange({ start: startIndex, end: endIndex });
    
    // Check if we're close to the end of the list
    if (onEndReached && scrollTop + viewportHeight + endReachedThreshold >= getTotalHeight()) {
      onEndReached();
    }
  }, [columns, itemHeight, gap, items.length, overscan, onEndReached, endReachedThreshold, getTotalHeight]);
  
  // Measure container width on mount and resize
  useEffect(() => {
    const updateWidth = () => {
      if (containerRef.current) {
        setContainerWidth(containerRef.current.offsetWidth);
      }
    };
    
    updateWidth();
    window.addEventListener('resize', updateWidth);
    return () => window.removeEventListener('resize', updateWidth);
  }, []);
  
  // Add scroll listener
  useEffect(() => {
    window.addEventListener('scroll', updateVisibleRange);
    return () => window.removeEventListener('scroll', updateVisibleRange);
  }, [updateVisibleRange]);
  
  // Update visible range when dependencies change
  useEffect(() => {
    updateVisibleRange();
  }, [items.length, columns, updateVisibleRange]);
  
  // Get visible items
  const visibleItems = items.slice(visibleRange.start, visibleRange.end);
  
  return (
    <Box
      ref={containerRef}
      sx={{
        position: 'relative',
        height: getTotalHeight(),
        width: '100%',
        ...containerStyle,
      }}
    >
      <Box
        sx={{
          display: 'flex',
          flexWrap: 'wrap',
          gap: `${gap}px`,
          position: 'absolute',
          width: '100%',
        }}
      >
        {visibleItems.map((item, index) => {
          const actualIndex = visibleRange.start + index;
          const row = Math.floor(actualIndex / columns);
          
          return (
            <Box
              key={keyExtractor(item, actualIndex)}
              sx={{
                width: getItemWidth(),
                height: itemHeight,
                position: 'absolute',
                top: row * (itemHeight + gap),
                left: `calc((${getItemWidth()} + ${gap}px) * ${actualIndex % columns})`,
                transition: 'transform 0.2s ease',
              }}
            >
              {renderItem(item, actualIndex)}
            </Box>
          );
        })}
      </Box>
    </Box>
  );
}

export default React.memo(VirtualizedList);
