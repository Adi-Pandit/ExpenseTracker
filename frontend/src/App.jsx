import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import WakeUpBanner from './components/WakeUpBanner'
import AppShell from './components/AppShell'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Expenses from './pages/Expenses'
import Accounts from './pages/Accounts'
import Recurring from './pages/Recurring'
import Notifications from './pages/Notifications'
import Settings from './pages/Settings'

function PrivateRoute({ children }) {
    const { user, loading } = useAuth()
    if (loading) return null
    return user ? children : <Navigate to="/login" replace />
}

function PublicRoute({ children }) {
    const { user, loading } = useAuth()
    if (loading) return null
    return user ? <Navigate to="/dashboard" replace /> : children
}

export default function App() {
    return (
        <BrowserRouter>
            <WakeUpBanner />
            <Routes>
                <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
                <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
                <Route path="/" element={<PrivateRoute><AppShell /></PrivateRoute>}>
                    <Route index element={<Navigate to="/dashboard" replace />} />
                    <Route path="dashboard" element={<Dashboard />} />
                    <Route path="expenses" element={<Expenses />} />
                    <Route path="accounts" element={<Accounts />} />
                    <Route path="recurring" element={<Recurring />} />
                    <Route path="notifications" element={<Notifications />} />
                    <Route path="settings" element={<Settings />} />
                </Route>
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
        </BrowserRouter>
    )
}
