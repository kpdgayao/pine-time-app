const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/api\/v1$/, '');

// Default placeholder image
const DEFAULT_PLACEHOLDERS = {
  avatar: '/avatar-placeholder.png',
  event: '/event-placeholder.png'
};

type PlaceholderType = 'avatar' | 'event';

// URL patterns that might have CORS issues
const CORS_PATTERNS = {
  facebook: [
    'fbcdn.net',
    'facebook.com',
    'fbsbx.com',
    'fbcdn-profile',
    'fbcdn-video',
    'fbcdn-sphotos',
    'fbexternal',
    'fna.fbcdn.net',
    'scontent'
  ],
  google: [
    'drive.google.com',
    'docs.google.com'
  ]
};

// Proxy configuration
const PROXY_ENDPOINT = '/api/v1/images/proxy';

/**
 * Constructs a full URL for an image path from the API
 * @param path - The relative path to the image
 * @returns The full URL to the image
 */
export const getImageUrl = (path: string | null | undefined, type: PlaceholderType = 'event'): string => {
  console.log('getImageUrl input:', path);
  
  if (!path || path === 'undefined' || path === 'null') {
    const placeholder = DEFAULT_PLACEHOLDERS[type];
    console.log('getImageUrl output (default):', placeholder);
    return placeholder;
  }

  // If the path is already a full URL
  if (path.startsWith('http://') || path.startsWith('https://')) {
    const lowercasePath = path.toLowerCase();
    
    // Check if URL needs proxying
    const needsProxy = 
      CORS_PATTERNS.facebook.some(pattern => lowercasePath.includes(pattern)) ||
      CORS_PATTERNS.google.some(pattern => lowercasePath.includes(pattern));

    if (needsProxy) {
      // For Google Drive, convert to direct download URL if possible
      let modifiedPath = path;
      if (lowercasePath.includes('drive.google.com')) {
        const fileId = path.match(/\/d\/([^\/]+)/)?.[1];
        if (fileId) {
          modifiedPath = `https://drive.google.com/uc?export=view&id=${fileId}`;
          console.log('Converted Google Drive URL:', modifiedPath);
        }
      }

      // Add a timestamp to prevent caching issues
      const timestamp = new Date().getTime();
      
      // Ensure URL is properly encoded while preserving the protocol
      const encodedUrl = encodeURIComponent(modifiedPath);
      
      // For fallback, use absolute URL pointing to our public assets
      // First determine the origin (protocol + domain + port) from API_BASE_URL
      const originRegex = /^(https?:\/\/[^/]+)/;
      const originMatch = API_BASE_URL.match(originRegex);
      const origin = originMatch ? originMatch[1] : window.location.origin;
      
      // Use absolute URL for fallback image
      const fallbackUrl = encodeURIComponent(`${origin}${DEFAULT_PLACEHOLDERS[type]}`);
      const proxyUrl = `${API_BASE_URL}${PROXY_ENDPOINT}?url=${encodedUrl}&fallback=${fallbackUrl}&_t=${timestamp}`;
      console.log('getImageUrl output (proxied):', proxyUrl);
      
      // Create an image element to test the URL
      const img = new Image();
      img.onerror = () => {
        console.error(`Image proxy failed for: ${modifiedPath}, falling back to default`);
        // We don't need to do anything here, the fallback URL will be used by the proxy
      };
      
      return proxyUrl;
    }

    console.log('getImageUrl output (full url):', path);
    return path;
  }

  // Remove any leading slashes and api/v1 prefix
  let cleanPath = path.replace(/^\/+/, '').replace(/^api\/v1\//, '');

  // Construct the final URL based on path type
  let finalUrl: string;

  if (cleanPath.startsWith('avatars/')) {
    // Avatar images are served directly from public/avatars
    finalUrl = `/${cleanPath}`;
  } else if (cleanPath.startsWith('media/') || cleanPath.startsWith('images/')) {
    // Media files are served from the API
    finalUrl = `${API_BASE_URL}/${cleanPath}`;
  } else if (cleanPath.includes('avatar') || cleanPath.includes('profile')) {
    // Profile-related endpoints go through the API
    finalUrl = `${API_BASE_URL}/api/v1/${cleanPath}`;
  } else {
    // For other paths, try the direct URL
    finalUrl = `${API_BASE_URL}/${cleanPath}`;
  }

  console.log('getImageUrl output:', finalUrl);
  return finalUrl;
};
