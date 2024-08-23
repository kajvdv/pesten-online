import { createContext, useRef, useState } from "react"


export const AuthContext = createContext()

function AuthProvider({children}) {
  const [accessToken, setAccessToken] = useState()
  return <AuthContext.Provider value={[accessToken, setAccessToken]}>
    {children}
  </AuthContext.Provider>
}

export default AuthProvider