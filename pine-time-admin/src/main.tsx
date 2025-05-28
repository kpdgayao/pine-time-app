import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { HashRouter } from 'react-router-dom'
import './index.css'
import App from './App.tsx'
import { AuthProvider } from './contexts/AuthContext'
import { LoadingProvider } from './contexts/LoadingContext'

// HashRouter doesn't need basename for subdirectory deployments
// It automatically handles paths based on the hash fragment

// Log environment information for debugging
console.log('Environment:', import.meta.env.MODE);
console.log('Using HashRouter for more reliable routing');

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <HashRouter>
      <LoadingProvider>
        <AuthProvider>
          <App />
        </AuthProvider>
      </LoadingProvider>
    </HashRouter>
  </StrictMode>,
)
