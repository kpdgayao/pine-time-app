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

// CRITICAL FIX: basename must be '/admin' for subdirectory deployment
// This tells React Router to strip '/admin' from the URL before matching routes
// Without this, React Router looks for routes at '/admin' instead of '/'
const basename = '/admin';

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
