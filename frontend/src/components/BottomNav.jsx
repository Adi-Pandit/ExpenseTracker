import { useNavigate, useLocation } from 'react-router-dom'

const NAV = [
    {
        key: 'dashboard',
        icon: (
            <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/>
            </svg>
        ),
    },
    {
        key: 'expenses',
        icon: (
            <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 3v18l2-1.4 2 1.4 2-1.4 2 1.4 2-1.4 2 1.4V3l-2 1.4L13 3l-2 1.4L9 3 7 4.4Z"/><path d="M9 8h6M9 12h6"/>
            </svg>
        ),
    },
    {
        key: 'accounts',
        icon: (
            <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="6" width="18" height="13" rx="2.5"/><path d="M3 10h18"/>
            </svg>
        ),
    },
    {
        key: 'recurring',
        icon: (
            <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 12a9 9 0 0 1 15.5-6.2L21 8"/><path d="M21 4v4h-4"/><path d="M21 12a9 9 0 0 1-15.5 6.2L3 16"/><path d="M3 20v-4h4"/>
            </svg>
        ),
    },
    {
        key: 'notifications',
        icon: (
            <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/>
            </svg>
        ),
    },
    {
        key: 'settings',
        icon: (
            <svg width="21" height="21" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-2.92.99V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.6 14H4.5a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 11 4.6V4.5a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 2.4 1.5l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 11H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1Z"/>
            </svg>
        ),
    },
]

export default function BottomNav({ unreadCount = 0 }) {
    const navigate = useNavigate()
    const { pathname } = useLocation()
    const active = pathname.split('/')[1] || 'dashboard'

    return (
        <div style={{
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            height: 'var(--bottom-nav-h)',
            background: 'var(--bg-card)',
            borderTop: '1px solid var(--border-card)',
            display: 'flex',
            alignItems: 'stretch',
            zIndex: 40,
            boxShadow: '0 -2px 16px rgba(16,24,40,0.05)',
        }}>
            {NAV.map(({ key, icon }) => {
                const isActive = active === key
                return (
                    <button
                        key={key}
                        onClick={() => navigate(`/${key}`)}
                        style={{
                            flex: 1,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            border: 'none',
                            background: 'transparent',
                            color: isActive ? 'var(--primary)' : 'var(--text-subtle)',
                            cursor: 'pointer',
                            position: 'relative',
                            transition: 'var(--t)',
                        }}
                    >
                        {icon}
                        {key === 'notifications' && unreadCount > 0 && (
                            <span style={{
                                position: 'absolute',
                                top: 8,
                                right: '50%',
                                transform: 'translateX(8px)',
                                background: 'var(--danger)',
                                color: '#fff',
                                fontSize: 9,
                                fontWeight: 700,
                                minWidth: 15,
                                height: 15,
                                borderRadius: 8,
                                display: 'inline-flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                padding: '0 3px',
                            }}>
                                {unreadCount > 99 ? '99+' : unreadCount}
                            </span>
                        )}
                    </button>
                )
            })}
        </div>
    )
}
