import React, { useState, useEffect } from 'react';
import { getImageUrl } from '../utils/image';
import { Avatar, AvatarProps, Box } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';

// Built-in base64 data URI fallback that will ALWAYS work
const FALLBACK_AVATAR_DATA_URI = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iIzJFN0QzMiIgZD0iTTEyIDJDNi40OCAyIDIgNi40OCAyIDEyczQuNDggMTAgMTAgMTAgMTAtNC40OCAxMC0xMFMxNy41MiAyIDEyIDJ6bTAgM2MyLjY3IDAgOCAyIDggNHY2Yy02IDAtOCAyLTggMnMtMi0yLTgtMnYtNmMwLTIgNS4zMy00IDgtNHptMCAxMWM1LjI0IDAgOS41My0xLjg4IDEwLS4wM0YyMC41NyAxNmEuOTk3Ljk5NyAwIDAgMC0uNDYuMjRjLS41OS41OS0xLjM4LjkzLTIuMjEuOTMtLjctLjAxLTEuMzYtLjI4LTEuODYtLjc4YTEuMTcgMS4xNyAwIDAgMC0uOS0uMzljLS40IDAtLjc4LjE3LTEuMDYuNDVDOC4xNSAxNi45OCA3LjU5IDE3LjI2IDcgMTcuMzFjLTEuMTYuMDktMi4yNi0uMzUtMy0xLjIyYTEuMTQgMS4xNCAwIDAgMC0uOTEtLjQ2Yy0uMy0uMDEtLjYuMDctLjg0LjI5LS4zOC4zNC0uODQuNTQtMS4zMS43MWE4Ljk4IDguOTggMCAwIDAgMTIuMDYgNC4yMmExMC40NCAxMC40NCAwIDAgMS0yLTEuNDhjLjA1LS4wNy4xLS4xNS4xNC0uMjMuNTktLjk3IDEuNzgtMS4xNiAyLjY5LS40MmExLjA0IDEuMDQgMCAwIDAgMS4zNy0uMDNjLjE4LS4xOS40Mi0uMy42Ny0uMzFoLjA2Yy40MyAwIC44My4yMSAxLjA3LjU4LjQzLjY1IDEuMTcgMS4wMSAxLjk1IDEuMDFoLjA1Yy41IDAgLjk4LS4xOSAxLjM0LS41M2EyLjM2IDIuMzYgMCAwIDEgMy4zIDAgOC45IDguOSAwIDAgMCAyLjA2LTMuMTFjLS40MS0uMDgtLjc5LS4yMy0xLjEzLS40NHYtLjFjLjA0LS4yLjA2LS40MS4wNi0uNjN2LTQuMTNjLjAzLS4zOC0uNDgtMi4xMy0xMC0yLjEzeiI+PC9wYXRoPjwvc3ZnPg==';

interface LazyAvatarProps extends AvatarProps {
  fallbackSrc?: string;
}

// Multiple fallback paths for avatars
const AVATAR_FALLBACKS = [
  '/avatar-placeholder.png',               // Primary fallback in public root
  '/images/placeholders/avatars/default.png' // Secondary fallback in subdirectory
];

/**
 * LazyAvatar: MUI Avatar with robust fallback image handling.
 * Uses multiple fallback layers to ensure avatars always display properly.
 */
const LazyAvatar: React.FC<LazyAvatarProps> = ({ src, alt, fallbackSrc = AVATAR_FALLBACKS[0], ...rest }) => {
  // Track fallback stages with useState
  const [fallbackStage, setFallbackStage] = useState<0 | 1 | 2 | 3>(0); // 0: original, 1: primary fallback, 2: secondary fallback, 3: data URI
  const [imageSrc, setImageSrc] = useState<string>(src || '');
  
  // Set up fallback image sources
  useEffect(() => {
    if (!src) {
      // No source provided, use fallback immediately
      setFallbackStage(1);
      setImageSrc(fallbackSrc);
    } else {
      // Process with image utility
      setFallbackStage(0);
      setImageSrc(getImageUrl(src, 'avatar'));
    }
  }, [src, fallbackSrc]);

  // Handle image load errors with progressive fallbacks
  const handleError = () => {
    console.log('LazyAvatar image error:', imageSrc);
    
    if (fallbackStage === 0) {
      // First error: try the primary fallback
      setFallbackStage(1);
      setImageSrc(AVATAR_FALLBACKS[0]);
    } else if (fallbackStage === 1) {
      // Second error: try the secondary fallback in subdirectory
      setFallbackStage(2);
      setImageSrc(AVATAR_FALLBACKS[1]);
    } else if (fallbackStage === 2) {
      // Third error: use embedded data URI as last resort
      setFallbackStage(3);
      setImageSrc(FALLBACK_AVATAR_DATA_URI);
    }
    // Stage 3 shouldn't error as it's embedded
  };

  // If we're at the final fallback stage, also render a backup initials fallback
  if (fallbackStage === 3) {
    return (
      <Box position="relative">
        <Avatar
          src={FALLBACK_AVATAR_DATA_URI}
          alt={alt}
          {...rest}
        >
          {/* Final fallback to initials or PersonIcon */}
          <PersonIcon fontSize="large" color="disabled" />
        </Avatar>
      </Box>
    );
  }

  return (
    <Avatar
      src={imageSrc}
      alt={alt}
      onError={handleError}
      {...rest}
    >
      {/* If no image, fallback to initials or children */}
      {rest.children}
    </Avatar>
  );
};

export default LazyAvatar;
