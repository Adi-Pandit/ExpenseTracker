import { useState, useEffect, useCallback } from 'react'
import { Outlet } from 'react-router-dom'
import { useIsMobile } from '../hooks/useWindowWidth'
import { listNotifications } from '../api/notifications'
import Sidebar from './Sidebar'
import BottomNav from './BottomNav'

export default function AppShell() {
    const isMobile = useIsMobile()
    const [unreadCount, setUnreadCount] = useState(0)

    const refreshUnread = useCallback(async () => {
        try {
            const data = await listNotifications({ is_read: false })
            /* data is either a paginated object { count, results } or a plain array */
            const count = Array.isArray(data) ? data.length : (data.count ?? 0)
            setUnreadCount(count)
        } catch {
            /* silently ignore — badge is non-critical */
        }
    }, [])

    useEffect(() => {
        refreshUnread()
    }, [refreshUnread])

    return (
        <div style={{ display: 'flex', minHeight: '100vh' }}>
            {!isMobile && <Sidebar unreadCount={unreadCount} />}

            <main style={{
                flex: 1,
                minWidth: 0,
                paddingBottom: isMobile ? 'var(--bottom-nav-h)' : 0,
                overflowX: 'hidden',
                minHeight: '100vh',
            }}>
                {/* refreshUnread lets pages update the badge after marking notifications read */}
                <Outlet context={{ refreshUnread }} />
            </main>

            {isMobile && <BottomNav unreadCount={unreadCount} />}
        </div>
    )
}
