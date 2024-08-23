import { Children, createContext, StrictMode, useContext, useRef, useState } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.jsx'
import {
  createBrowserRouter,
  RouterProvider,
} from "react-router-dom";
import LoginPage from './LoginPage'
import RegisterPage from './RegisterPage';
import LobbiesPage from './LobbiesPage';
import AuthProvider from './AuthProvider';
// import './index.css'


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
]);

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <AuthProvider>
      <RouterProvider router={router}/>
    </AuthProvider>
  </StrictMode>,
)
