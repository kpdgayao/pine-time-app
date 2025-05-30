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

// SUBDOMAIN DEPLOYMENT: For admin.pinetimeapp.com we don't need a basename
// Since we're at the root of the subdomain, we use an empty string or '/'
// This simplifies routing and eliminates path conflicts
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
