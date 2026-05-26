import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import { warmupBackend } from './api'

// Wake the Render free-tier dyno as early as possible so the first page
// the user navigates to doesn't eat the full cold-start delay.
warmupBackend()

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
