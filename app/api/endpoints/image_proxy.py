import base64
import httpx
import logging
from fastapi import APIRouter, Response, HTTPException
from typing import Optional
from urllib.parse import urlparse, unquote

router = APIRouter()

@router.get("/proxy")
async def proxy_image(url: str, fallback: Optional[str] = None):
    """
    Proxy for images that might have CORS restrictions.
    
    Args:
        url: The URL of the image to proxy
        fallback: Optional fallback image URL if the requested image fails
        
    Returns:
        The image content with appropriate content type
    """
    if not url:
        if fallback:
            url = fallback
        else:
            raise HTTPException(status_code=400, detail="No URL provided")
    
    # Decode URL if it's base64 encoded
    try:
        if url.startswith('b64:'):
            url = base64.b64decode(url[4:]).decode('utf-8')
        else:
            url = unquote(url)
    except Exception:
        pass
    
    # Validate URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            raise HTTPException(status_code=400, detail="Invalid URL")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid URL format")
    
    # Try to fetch the image
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        try:
            # Determine if this is a Facebook CDN URL
            is_facebook_url = any(fb_domain in url.lower() for fb_domain in [
                'fbcdn.net', 'facebook.com', 'fbsbx.com', 'fbcdn-profile', 'fbcdn-video',
                'fbcdn-sphotos', 'fbexternal', 'fna.fbcdn.net', 'scontent'
            ])
            
            # Set appropriate headers based on the image source
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Sec-Fetch-Dest": "image",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "cross-site"
            }
            
            # Add specific referrer for Facebook CDN images
            if is_facebook_url:
                headers["Referer"] = "https://www.facebook.com/"
            else:
                headers["Referer"] = "https://www.google.com/"
            
            response = await client.get(url, headers=headers)
            
            if response.status_code != 200:
                if fallback:
                    # Try the fallback URL
                    response = await client.get(fallback, headers=headers)
                    if response.status_code != 200:
                        raise HTTPException(status_code=404, detail="Image not found")
                else:
                    raise HTTPException(status_code=response.status_code, detail="Failed to fetch image")
            
            # Determine content type
            content_type = response.headers.get("content-type", "image/jpeg")
            
            # Return the image with the correct content type and caching headers
            return Response(
                content=response.content, 
                media_type=content_type,
                headers={
                    "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
                    "Content-Type": content_type
                }
            )
            
        except httpx.RequestError as e:
            logging.error(f"Request error when proxying image: {str(e)} for URL: {url}")
            if fallback:
                try:
                    response = await client.get(fallback, headers=headers)
                    if response.status_code == 200:
                        content_type = response.headers.get("content-type", "image/jpeg")
                        return Response(content=response.content, media_type=content_type)
                except Exception:
                    pass
            
            raise HTTPException(status_code=500, detail="Failed to fetch image")
