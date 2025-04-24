import base64
import httpx
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
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Referer": "https://www.google.com/"
            }
            
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
            
            # Return the image with the correct content type
            return Response(content=response.content, media_type=content_type)
            
        except httpx.RequestError:
            if fallback:
                try:
                    response = await client.get(fallback, headers=headers)
                    if response.status_code == 200:
                        content_type = response.headers.get("content-type", "image/jpeg")
                        return Response(content=response.content, media_type=content_type)
                except Exception:
                    pass
            
            raise HTTPException(status_code=500, detail="Failed to fetch image")
