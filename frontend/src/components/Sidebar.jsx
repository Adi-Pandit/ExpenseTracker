import { useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getInitials } from '../utils/colors'
import Logo from './Logo'

const NAV = [
    {
        key: 'dashboard',
        label: 'Dashboard',
        icon: (
            <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/>
            </svg>
        ),
    },
    {
        key: 'expenses',
        label: 'Expenses',
        icon: (
            <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 3v18l2-1.4 2 1.4 2-1.4 2 1.4 2-1.4 2 1.4V3l-2 1.4L13 3l-2 1.4L9 3 7 4.4Z"/><path d="M9 8h6M9 12h6"/>
            </svg>
        ),
    },
    {
        key: 'accounts',
        label: 'Accounts',
        icon: (
            <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="6" width="18" height="13" rx="2.5"/><path d="M3 10h18"/><path d="M16 14.5h2"/>
            </svg>
        ),
    },
    {
        key: 'recurring',
        label: 'Recurring',
        icon: (
            <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M3 12a9 9 0 0 1 15.5-6.2L21 8"/><path d="M21 4v4h-4"/><path d="M21 12a9 9 0 0 1-15.5 6.2L3 16"/><path d="M3 20v-4h4"/>
            </svg>
        ),
    },
    {
        key: 'notifications',
        label: 'Notifications',
        icon: (
            <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M18 8a6 6 0 1 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/>
            </svg>
        ),
    },
    {
        key: 'settings',
        label: 'Settings',
        icon: (
            <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-2.92.99V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.6 14H4.5a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 11 4.6V4.5a2 2 0 1 1 4 0v.09a1.65 1.65 0 0 0 2.4 1.5l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 11H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1Z"/>
            </svg>
        ),
    },
]

export default function Sidebar({ unreadCount = 0 }) {
    const navigate = useNavigate()
    const { pathname } = useLocation()
    const { user, logoutUser } = useAuth()

    const active = pathname.split('/')[1] || 'dashboard'

    function navItemStyle(key) {
        const isActive = active === key
        return {
            display: 'flex',
            alignItems: 'center',
            gap: 10,
            padding: '9px 12px',
            borderRadius: 10,
            cursor: 'pointer',
            fontSize: 14.5,
            fontWeight: isActive ? 600 : 500,
            color: isActive ? 'var(--primary-fg)' : 'var(--text-muted)',
            background: isActive ? 'var(--primary)' : 'transparent',
            transition: 'var(--t)',
            userSelect: 'none',
        }
    }

    const initials = getInitials(`${user?.first_name ?? ''} ${user?.last_name ?? ''}`.trim() || user?.username)
    const displayName = [user?.first_name, user?.last_name].filter(Boolean).join(' ') || user?.username

    return (
        <aside style={{
            width: 'var(--sidebar-width)',
            flexShrink: 0,
            background: 'var(--bg-card)',
            borderRight: '1px solid var(--border-card)',
            padding: '22px 16px',
            display: 'flex',
            flexDirection: 'column',
            position: 'sticky',
            top: 0,
            height: '100vh',
            overflowY: 'auto',
        }}>
            {/* Brand */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 11, padding: '4px 8px 22px' }}>
                <Logo size={34} />
                <span style={{ fontSize: 19, fontWeight: 700, letterSpacing: '-0.02em' }}>Ledgerly</span>
            </div>

            {/* Nav */}
            <nav style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                {NAV.map(({ key, label, icon }) => (
                    <div key={key} onClick={() => navigate(`/${key}`)} style={navItemStyle(key)}>
                        {icon}
                        <span style={{ flex: 1 }}>{label}</span>
                        {key === 'notifications' && unreadCount > 0 && (
                            <span style={{
                                background: 'var(--danger)',
                                color: '#fff',
                                fontSize: 11,
                                fontWeight: 700,
                                minWidth: 19,
                                height: 19,
                                borderRadius: 10,
                                display: 'inline-flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                padding: '0 5px',
                            }}>
                                {unreadCount > 99 ? '99+' : unreadCount}
                            </span>
                        )}
                    </div>
                ))}
            </nav>

            {/* User footer */}
            <div style={{
                marginTop: 'auto',
                borderTop: '1px solid var(--border-subtle)',
                paddingTop: 14,
                display: 'flex',
                alignItems: 'center',
                gap: 11,
            }}>
                <div style={{
                    width: 38,
                    height: 38,
                    borderRadius: '50%',
                    background: 'var(--primary-light)',
                    color: 'var(--primary)',
                    fontWeight: 700,
                    fontSize: 15,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                }}>
                    {initials}
                </div>
                <div style={{ minWidth: 0, flex: 1 }}>
                    <div style={{ fontSize: 14, fontWeight: 600, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {displayName}
                    </div>
                    <div style={{ fontSize: 12, color: 'var(--text-subtle)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {user?.email}
                    </div>
                </div>
                <button
                    onClick={logoutUser}
                    title="Log out"
                    style={{
                        border: 'none',
                        background: 'transparent',
                        color: 'var(--text-subtle)',
                        cursor: 'pointer',
                        padding: 6,
                        borderRadius: 8,
                        display: 'flex',
                        alignItems: 'center',
                        transition: 'var(--t)',
                    }}
                    onMouseEnter={e => {
                        e.currentTarget.style.color = 'var(--danger)'
                        e.currentTarget.style.background = 'var(--danger-bg)'
                    }}
                    onMouseLeave={e => {
                        e.currentTarget.style.color = 'var(--text-subtle)'
                        e.currentTarget.style.background = 'transparent'
                    }}
                >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                        <path d="m16 17 5-5-5-5"/><path d="M21 12H9"/>
                    </svg>
                </button>
            </div>
        </aside>
    )
}
