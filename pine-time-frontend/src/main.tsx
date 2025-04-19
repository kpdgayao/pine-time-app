import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './theme/global.css'
import App from './App.tsx'
import { PineTimeThemeProvider } from './theme'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <PineTimeThemeProvider>
      <App />
    </PineTimeThemeProvider>
  </StrictMode>,
)
