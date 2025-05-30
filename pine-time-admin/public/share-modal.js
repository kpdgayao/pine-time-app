// Pine Time Admin - Share Modal Handling
// This script handles the share functionality safely with proper error handling

document.addEventListener('DOMContentLoaded', function() {
  try {
    // Safely try to find the share button
    const shareButton = document.getElementById('share-button');
    
    // Only add event listener if element exists
    if (shareButton) {
      shareButton.addEventListener('click', function() {
        // Share functionality
        console.log('Share button clicked');
        
        // Create and show modal if supported
        if (navigator.share) {
          navigator.share({
            title: 'Pine Time Admin Dashboard',
            url: window.location.href
          })
          .catch(error => {
            console.warn('Share failed:', error);
          });
        } else {
          console.log('Web Share API not supported');
          // Fallback share implementation
        }
      });
    } else {
      console.log('Share button not found, skipping share functionality');
    }
  } catch (error) {
    // Log error but don't crash
    console.warn('Error initializing share functionality:', error);
  }
});
