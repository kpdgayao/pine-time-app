import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import './index.css'
import App from './App.tsx'
import { AuthProvider } from './contexts/AuthContext'
import { LoadingProvider } from './contexts/LoadingContext'

// Use the correct basename based on environment
// In production, the app is served from /admin
// In development, it's served from the root
const basename = import.meta.env.PROD ? '/admin' : '/';

// Log environment information for debugging
console.log('Environment:', import.meta.env.MODE);
console.log('Using basename:', basename);

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter basename={basename}>
      <LoadingProvider>
        <AuthProvider>
          <App />
        </AuthProvider>
      </LoadingProvider>
    </BrowserRouter>
  </StrictMode>,
)
