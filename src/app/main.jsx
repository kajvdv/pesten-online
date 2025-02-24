import { Children, createContext, StrictMode, useContext, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import LoginPage from './LoginPage'
import RegisterPage from './RegisterPage';
import LobbiesPage from './LobbiesPage';
import GamePage from './GamePage';
import './styles/main.css'
import './styles/cards.css'


const router = createBrowserRouter([
  {
    path: "/",
    element: <LoginPage/>,
  },
  {
    path: "/register",
    element: <RegisterPage/>,
  },
  {
    path: "/lobbies",
    element: <LobbiesPage/>,
  },
  {
    path: "/game",
    element: <GamePage/>
  }
]);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <RouterProvider router={router}/>
  </StrictMode>
)
