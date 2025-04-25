import base64
import httpx
import logging
import os
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
    
    # Decode URL if it's encoded
    try:
        # First, handle base64 encoding
        if url.startswith('b64:'):
            url = base64.b64decode(url[4:]).decode('utf-8')
        
        # Then unquote the URL, potentially multiple times for double-encoding
        prev_url = None
        current_url = url
        while prev_url != current_url:
            prev_url = current_url
            current_url = unquote(prev_url)
        url = current_url
        
        logging.info(f"Decoded URL: {url}")
    except Exception as e:
        logging.error(f"Error decoding URL: {str(e)}")
        pass
    
    # Validate URL
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            logging.error(f"Invalid URL structure: scheme={parsed.scheme}, netloc={parsed.netloc}")
            raise HTTPException(status_code=400, detail=f"Invalid URL: missing {'scheme' if not parsed.scheme else 'domain'}")
    except Exception as e:
        logging.error(f"URL parsing error: {str(e)} for URL: {url}")
        raise HTTPException(status_code=400, detail=f"Invalid URL format: {str(e)}")
    
    # Try to fetch the image
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        try:
            # Determine URL type and set appropriate headers
            url_type = None
            url_lower = url.lower()
            
            # Check for Facebook CDN URLs
            if any(fb_domain in url_lower for fb_domain in [
                'fbcdn.net', 'facebook.com', 'fbsbx.com', 'fbcdn-profile', 'fbcdn-video',
                'fbcdn-sphotos', 'fbexternal', 'fna.fbcdn.net', 'scontent'
            ]):
                url_type = 'facebook'
            
            # Check for Google Drive URLs
            elif any(google_domain in url_lower for google_domain in [
                'drive.google.com', 'docs.google.com'
            ]):
                url_type = 'google'
            
            # Set appropriate headers based on the image source
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Sec-Fetch-Dest": "image",
                "Sec-Fetch-Mode": "no-cors",
                "Sec-Fetch-Site": "cross-site",
                "Cookie": ""
            }
            
            # Add source-specific headers
            if url_type == 'facebook':
                headers.update({
                    "Referer": "https://www.facebook.com/",
                    "Origin": "https://www.facebook.com"
                })
            elif url_type == 'google':
                headers.update({
                    "Referer": "https://drive.google.com/",
                    "Origin": "https://drive.google.com"
                })
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
            # Log the actual exception type and details
            error_type = type(e).__name__
            logging.error(f"Request error when proxying image: {error_type}: {str(e)} for URL: {url}")
            
            # Attempt to use fallback if available
            if fallback:
                try:
                    fallback_response = await client.get(fallback, headers=headers)
                    if fallback_response.status_code == 200:
                        content_type = fallback_response.headers.get("content-type", "image/jpeg")
                        return Response(content=fallback_response.content, media_type=content_type)
                except Exception as fallback_error:
                    logging.error(f"Fallback image also failed: {str(fallback_error)} for URL: {fallback}")
            
            # For 403 errors or other failures, serve a local fallback
            logging.warning(f"Using static fallback for failed image request: {url}")
            
            # If a fallback URL was provided, try using it but ensure it's a static file path
            fallback_file = None
            
            if fallback:
                # Extract just the path portion if it's a full URL
                if fallback.startswith("http"):
                    try:
                        parsed_fallback = urlparse(fallback)
                        fallback_path = parsed_fallback.path
                    except:
                        fallback_path = "/images/placeholders/events/default-event.jpg"
                else:
                    fallback_path = fallback
                
                # Try to find the file in the static directory
                if fallback_path.startswith("/"):
                    fallback_path = fallback_path[1:]
                
                # Look in the static directory for the fallback file
                # First try direct path in the file system
                fallback_file = f"app/static/{fallback_path}"
                
                # If that doesn't exist, try via the static mount
                if not os.path.exists(fallback_file):
                    # Remove any leading 'static/' from the path since we're already in the static directory
                    if fallback_path.startswith('static/'):
                        fallback_path = fallback_path[7:]
                    # Check if the file exists in the static directory
                    app_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                    static_file = os.path.join(app_dir, 'static', fallback_path)
                    if os.path.exists(static_file):
                        fallback_file = static_file
                
                # Check if the fallback file exists, otherwise use a default
                if not os.path.exists(fallback_file):
                    # Check for various default locations
                    default_paths = [
                        "app/static/images/placeholders/events/default-event.jpg",
                        "app/static/default-event.jpg",
                        "app/static/images/default-event.jpg"
                    ]
                    
                    for path in default_paths:
                        if os.path.exists(path):
                            fallback_file = path
                            break
                    
                    # If none exist, create a very simple fallback
                    if not fallback_file or not os.path.exists(fallback_file):
                        # Ensure directories exist
                        os.makedirs("app/static/images/placeholders/events", exist_ok=True)
                        
                        # Create a tiny placeholder image file if it doesn't exist
                        default_file = "app/static/images/placeholders/events/default-event.jpg"
                        if not os.path.exists(default_file):
                            with open(default_file, "w") as f:
                                f.write("Placeholder image")
                        
                        fallback_file = default_file
            
            # If we have a fallback file, return it
            if fallback_file and os.path.exists(fallback_file):
                with open(fallback_file, "rb") as f:
                    content = f.read()
                    
                # Determine content type based on extension
                ext = fallback_file.split(".")[-1].lower()
                content_type = {
                    "jpg": "image/jpeg",
                    "jpeg": "image/jpeg",
                    "png": "image/png",
                    "gif": "image/gif",
                    "webp": "image/webp"
                }.get(ext, "image/jpeg")
                
                return Response(
                    content=content, 
                    media_type=content_type,
                    headers={
                        "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
                        "Content-Type": content_type
                    }
                )
            
            # If all fallbacks fail, raise a 404
            raise HTTPException(status_code=404, detail=f"Image not found: {url}")
