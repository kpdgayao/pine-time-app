import React, { useState, useEffect } from 'react';
import { Box, Skeleton, Typography } from '@mui/material';
import { Event } from '../types/events';
import { styled, keyframes } from '@mui/material/styles';
import { getImageUrl } from '../utils/image';

// Create a fade-in animation
const fadeIn = keyframes`
  from { opacity: 0; }
  to { opacity: 1; }
`;

const StyledImage = styled('img')(() => ({
  width: '100%',
  height: '100%',
  objectFit: 'cover',
  animation: `${fadeIn} 0.5s ease-in-out`,
}));

// Staged fallback images from most specific to most generic
const FALLBACK_IMAGES = [
  '/event-placeholder.png',      // Default fallback
  '/images/placeholders/events/default-event.jpg',  // Secondary fallback path
];

interface EventImageProps {
  event: Event;
  width?: string | number;
  height?: string | number;
  aspectRatio?: string;
  borderRadius?: string | number;
  className?: string;
  showPlaceholderInfo?: boolean;
  showLoading?: boolean;
}

/**
 * EventImage component - Specialized component for displaying event images with robust
 * fallback handling, error recovery, and type-specific placeholders.
 */
const EventImage: React.FC<EventImageProps> = ({
  event,
  width = '100%',
  height = '100%',
  aspectRatio = '16/9',
  borderRadius = 0,
  className = '',
  showPlaceholderInfo = false,
  showLoading = true,
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);
  const [currentFallbackIndex, setCurrentFallbackIndex] = useState(-1);
  const [imageSrc, setImageSrc] = useState<string>('');
  
  // Get event-type specific fallback if available
  const getTypeFallback = (type: string): string | null => {
    const normalizedType = type.toLowerCase().replace(/\s+/g, '');
    
    // Return type-specific fallback if it exists in our array
    const typeMatch = FALLBACK_IMAGES.find(path => 
      path.includes(`type-${normalizedType}`)
    );
    
    return typeMatch || null;
  };

  // Try the next fallback image in sequence
  const tryNextFallback = () => {
    // If we've exhausted all fallbacks, stay with the last one
    if (currentFallbackIndex >= FALLBACK_IMAGES.length - 1) {
      return;
    }
    
    const nextIndex = currentFallbackIndex + 1;
    setCurrentFallbackIndex(nextIndex);
    setImageSrc(FALLBACK_IMAGES[nextIndex]);
  };

  // Use the imported getImageUrl utility

  // Initialize image source
  useEffect(() => {
    setIsLoading(true);
    setHasError(false);
    
    // First, try using the event's image URL
    if (event?.image_url) {
      setImageSrc(getImageUrl(event.image_url, 'event'));
      return;
    }
    
    // If no image URL, try event type specific fallback
    if (event?.event_type) {
      const typeFallback = getTypeFallback(event.event_type);
      if (typeFallback) {
        setCurrentFallbackIndex(FALLBACK_IMAGES.indexOf(typeFallback));
        setImageSrc(typeFallback);
        return;
      }
    }
    
    // Otherwise use default fallback
    setCurrentFallbackIndex(0);
    setImageSrc(FALLBACK_IMAGES[0]);
  }, [event?.image_url, event?.event_type]);

  // Handle image load success
  const handleLoad = () => {
    setIsLoading(false);
    setHasError(false);
  };

  // Handle image load error
  const handleError = () => {
    setIsLoading(false);
    setHasError(true);
    
    // If already using a fallback, try the next one
    if (currentFallbackIndex >= 0) {
      tryNextFallback();
    } else {
      // If using main image and it failed, switch to first fallback
      setCurrentFallbackIndex(0);
      setImageSrc(FALLBACK_IMAGES[0]);
    }
  };

  return (
    <Box
      sx={{
        width,
        height,
        position: 'relative',
        borderRadius,
        overflow: 'hidden',
        aspectRatio,
        backgroundColor: 'rgba(0, 0, 0, 0.05)',
      }}
      className={className}
    >
      {isLoading && showLoading && (
        <Skeleton
          variant="rectangular"
          width="100%"
          height="100%"
          animation="wave"
          sx={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            zIndex: 1,
            borderRadius,
          }}
        />
      )}
      
      <StyledImage
        src={imageSrc}
        alt={event?.title ? `Image for ${event.title}` : 'Event image'}
        onLoad={handleLoad}
        onError={handleError}
        style={{
          opacity: isLoading ? 0 : 1,
          borderRadius,
          display: 'block',
        }}
      />
      
      {/* Optional placeholder info indicator */}
      {showPlaceholderInfo && hasError && (
        <Box
          sx={{
            position: 'absolute',
            bottom: 0,
            right: 0,
            background: 'rgba(0,0,0,0.5)',
            color: 'white',
            padding: '2px 6px',
            borderRadius: '4px 0 0 0',
            fontSize: '10px',
          }}
        >
          <Typography variant="caption" sx={{ opacity: 0.8 }}>
            {currentFallbackIndex === 0 ? 'Default image' : 
              event?.event_type ? `${event.event_type} image` : 'Fallback image'}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default React.memo(EventImage);
