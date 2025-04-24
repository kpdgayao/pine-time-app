import React, { useState, useEffect, useRef } from 'react';
import { Box, Skeleton } from '@mui/material';
import { styled, keyframes } from '@mui/material/styles';

// Create a fade-in animation
const fadeIn = keyframes`
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
`;

const StyledImage = styled('img')(() => ({
  width: '100%',
  height: '100%',
  objectFit: 'cover',
  animation: `${fadeIn} 0.3s ease-in-out`,
}));

interface LazyImageProps {
  src: string;
  alt: string;
  placeholderSrc?: string;
  width?: string | number;
  height?: string | number;
  borderRadius?: string | number;
  fallbackSrc?: string;
  style?: React.CSSProperties;
  className?: string;
  loadingHeight?: number | string;
  onLoad?: () => void;
  onError?: () => void;
}

const LazyImage: React.FC<LazyImageProps> = ({
  src,
  alt,
  placeholderSrc = '/event-placeholder.png',
  width = '100%',
  height = '100%',
  borderRadius = 0,
  fallbackSrc = '/event-placeholder.png',
  style = {},
  className = '',
  loadingHeight = 180,
  onLoad,
  onError,
}) => {
  const [isLoading, setIsLoading] = useState(true);
  const [imageSrc, setImageSrc] = useState<string>(placeholderSrc);
  const imageRef = useRef<HTMLImageElement>(null);
  const observer = useRef<IntersectionObserver | null>(null);

  // Handle image load
  const handleLoad = () => {
    setIsLoading(false);
    onLoad?.();
  };

  // Handle image error with robust fallback
  const handleError = () => {
    setIsLoading(false);
    // Use fallback for all error cases
    setImageSrc(fallbackSrc);
    onError?.();
  };

  // Helper function to handle problematic image URLs (like Facebook)
  const getProxiedImageUrl = (url: string): string => {
    if (!url) return fallbackSrc;
    
    // Check if it's a Facebook CDN URL that might have CORS issues
    // Expanded pattern matching for Facebook CDN domains
    const facebookPatterns = [
      'fbcdn.net', 'facebook.com', 'fbsbx.com', 'fbcdn-profile', 
      'fbcdn-video', 'fbcdn-sphotos', 'fbexternal', 'fna.fbcdn.net', 
      'scontent'
    ];
    
    const isFacebookImage = facebookPatterns.some(pattern => url.toLowerCase().includes(pattern));
    
    if (isFacebookImage) {
      // Use our backend proxy for Facebook CDN images
      const apiUrl = '/api/images/proxy';
      const encodedUrl = encodeURIComponent(url);
      const encodedFallback = encodeURIComponent(fallbackSrc);
      return `${apiUrl}?url=${encodedUrl}&fallback=${encodedFallback}`;
    }
    
    // Return the original URL for other images
    return url;
  };
  
  // Set up intersection observer for lazy loading
  useEffect(() => {
    // Process the source URL to handle problematic sources
    const processedSrc = getProxiedImageUrl(src);
    
    // If the image is already in view or we don't have IntersectionObserver, load immediately
    if (!('IntersectionObserver' in window)) {
      setImageSrc(processedSrc);
      return;
    }

    observer.current = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        setImageSrc(getProxiedImageUrl(src));
        if (observer.current && imageRef.current) {
          observer.current.unobserve(imageRef.current);
        }
      }
    }, {
      rootMargin: '100px', // Start loading when image is 100px from viewport
      threshold: 0.01,
    });

    if (imageRef.current) {
      observer.current.observe(imageRef.current);
    }

    return () => {
      if (observer.current && imageRef.current) {
        observer.current.unobserve(imageRef.current);
      }
    };
  }, [src]);

  return (
    <Box
      sx={{
        width,
        height,
        position: 'relative',
        borderRadius,
        overflow: 'hidden',
        backgroundColor: 'rgba(0, 0, 0, 0.04)',
      }}
    >
      {isLoading && (
        <Skeleton
          variant="rectangular"
          width="100%"
          height={loadingHeight}
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
        ref={imageRef}
        src={imageSrc}
        alt={alt}
        onLoad={handleLoad}
        onError={handleError}
        style={{
          ...style,
          opacity: isLoading ? 0 : 1,
          borderRadius,
          display: 'block',
        }}
        className={className}
      />
    </Box>
  );
};

export default React.memo(LazyImage);
