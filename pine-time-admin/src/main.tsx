import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.tsx'
import { AuthProvider } from './contexts/AuthContext'
import { LoadingProvider } from './contexts/LoadingContext'

// BrowserRouter with basename is crucial for subdirectory deployments
// This ensures all routes are correctly prefixed with /admin in production

// Log environment information for debugging
console.log('Environment:', import.meta.env.MODE);
console.log('BASE_URL:', import.meta.env.BASE_URL);
console.log('Using BrowserRouter with basename for subdirectory routing');

// For proper subdirectory deployment, we need to correctly set the basename
// When deployed to /admin, we need an empty basename because the URL already includes /admin
// This is critical - with BrowserRouter, the URL is already at /admin, so we don't need to add it again
const basename = '';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter basename={basename}>
      <LoadingProvider>
        <AuthProvider>
          <App />
        </AuthProvider>
      </LoadingProvider>
    </BrowserRouter>
  </StrictMode>
)
