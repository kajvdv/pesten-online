import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import LobbiesPage from './LobbiesPage'


createRoot(document.getElementById('root')).render(
  <StrictMode>
    <LobbiesPage/>
  </StrictMode>
)