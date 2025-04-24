from typing import Any
import logging
import httpx
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, HttpUrl

from app.api.dependencies import safe_api_call

router = APIRouter()


class ProxyRequest(BaseModel):
    url: HttpUrl


@router.get("/image")
@safe_api_call
async def proxy_image(url: str) -> Any:
    """
    Proxy an external image to bypass CORS and referrer restrictions.
    
    This endpoint fetches an image from an external URL and returns it,
    bypassing CORS restrictions and referrer checks that might cause 403 errors
    in the frontend (especially for Facebook CDN images).
    
    Args:
        url: The URL of the image to proxy
        
    Returns:
        The image content with appropriate content type
    """
    try:
        logging.info(f"Proxying image from: {url}")
        
        # Set up headers to mimic a browser request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.facebook.com/",  # This helps with Facebook CDN images
            "Sec-Fetch-Dest": "image",
            "Sec-Fetch-Mode": "no-cors",
            "Sec-Fetch-Site": "cross-site",
        }
        
        # Create a timeout to prevent hanging requests
        timeout = httpx.Timeout(10.0, connect=5.0)
        
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            
            # Check if the request was successful
            if response.status_code != 200:
                logging.error(f"Failed to proxy image. Status code: {response.status_code}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Failed to fetch image from source: {response.status_code}"
                )
            
            # Get the content type from the response headers or default to image/jpeg
            content_type = response.headers.get("Content-Type", "image/jpeg")
            
            # Return the image as a streaming response
            return StreamingResponse(
                content=response.iter_bytes(),
                media_type=content_type,
                headers={
                    "Cache-Control": "public, max-age=86400",  # Cache for 24 hours
                    "Content-Type": content_type
                }
            )
            
    except httpx.RequestError as e:
        logging.error(f"Request error when proxying image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error fetching image: {str(e)}"
        )
        
    except Exception as e:
        logging.error(f"Unexpected error in proxy_image: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred when proxying the image"
        )
