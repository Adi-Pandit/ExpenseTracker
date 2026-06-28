import { createContext, useContext, useState, useEffect } from 'react'
import { getProfile } from '../api/auth'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)

    /* Rehydrate session on hard reload */
    useEffect(() => {
        const token = localStorage.getItem('access')
        if (!token) {
            setLoading(false)
            return
        }
        getProfile()
            .then(u => setUser(u))
            .catch(() => {
                localStorage.removeItem('access')
                localStorage.removeItem('refresh')
            })
            .finally(() => setLoading(false))
    }, [])

    function loginUser({ access, refresh, user: u }) {
        localStorage.setItem('access', access)
        localStorage.setItem('refresh', refresh)
        setUser(u)
    }

    function logoutUser() {
        localStorage.removeItem('access')
        localStorage.removeItem('refresh')
        setUser(null)
    }

    return (
        <AuthContext.Provider value={{ user, setUser, loginUser, logoutUser, loading }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    return useContext(AuthContext)
}
