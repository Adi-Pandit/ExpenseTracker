import { useState, useEffect } from 'react'
import { useOutletContext } from 'react-router-dom'
import { listNotifications, markRead } from '../api/notifications'
import { useToast } from '../context/ToastContext'
import { formatDate } from '../utils/format'

const TYPE_ICON = {
    budget_exceeded: { icon: '⚠️', color: '#D97706', bg: '#FEF3C7' },
    recurring_generated: { icon: '🔄', color: '#059669', bg: '#D1FAE5' },
    expense_created: { icon: '💰', color: 'var(--primary)', bg: 'var(--primary-light)' },
    default: { icon: '🔔', color: 'var(--primary)', bg: 'var(--primary-light)' },
}

function getTypeStyle(type) {
    return TYPE_ICON[type] ?? TYPE_ICON.default
}

export default function Notifications() {
    const toast = useToast()
    const { refreshUnread } = useOutletContext() ?? {}

    const [notifications, setNotifications] = useState([])
    const [count, setCount] = useState(0)
    const [hasNext, setHasNext] = useState(false)
    const [hasPrev, setHasPrev] = useState(false)
    const [page, setPage] = useState(1)
    const [loading, setLoading] = useState(true)
    const [tab, setTab] = useState('all')
    const [markingAll, setMarkingAll] = useState(false)

    async function load(pg = 1, currentTab = tab) {
        setLoading(true)
        try {
            const params = { page: pg }
            if (currentTab === 'unread') params.is_read = false
            const data = await listNotifications(params)
            setNotifications(data.results ?? [])
            setCount(data.count ?? 0)
            setHasNext(Boolean(data.next))
            setHasPrev(Boolean(data.previous))
        } catch {
            toast.error('Failed to load notifications.')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => { load(1, tab) }, [tab]) // eslint-disable-line react-hooks/exhaustive-deps

    async function handleMarkRead(id) {
        try {
            await markRead(id)
            setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n))
            refreshUnread?.()
        } catch {
            toast.error('Could not mark as read.')
        }
    }

    async function handleMarkAllRead() {
        const unread = notifications.filter(n => !n.is_read)
        if (!unread.length) return
        setMarkingAll(true)
        try {
            await Promise.all(unread.map(n => markRead(n.id)))
            setNotifications(prev => prev.map(n => ({ ...n, is_read: true })))
            refreshUnread?.()
            toast.success('All notifications marked as read.')
        } catch {
            toast.error('Failed to mark all as read.')
        } finally {
            setMarkingAll(false)
        }
    }

    function goPage(p) {
        setPage(p)
        load(p, tab)
    }

    const unreadCount = notifications.filter(n => !n.is_read).length

    return (
        <div className="page">
            {/* ── Header ── */}
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, marginBottom: 20 }}>
                <div>
                    <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0, letterSpacing: '-0.02em' }}>Notifications</h1>
                    <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: '4px 0 0' }}>
                        {count} notification{count !== 1 ? 's' : ''}{unreadCount > 0 ? ` · ${unreadCount} unread` : ''}
                    </p>
                </div>
                {unreadCount > 0 && (
                    <button
                        onClick={handleMarkAllRead}
                        disabled={markingAll}
                        style={{
                            height: 38, padding: '0 16px', display: 'flex', alignItems: 'center', gap: 7,
                            background: 'var(--bg-card)', color: 'var(--primary)',
                            border: '1.5px solid var(--primary-muted)', borderRadius: 9,
                            fontSize: 13.5, fontWeight: 600, cursor: markingAll ? 'not-allowed' : 'pointer',
                        }}
                    >
                        {markingAll ? <span className="spinner" style={{ width: 14, height: 14 }} /> : null}
                        Mark all read
                    </button>
                )}
            </div>

            {/* ── Tabs ── */}
            <div style={{ display: 'flex', gap: 4, marginBottom: 16, background: 'var(--bg-muted)', padding: 4, borderRadius: 10, width: 'fit-content' }}>
                {['all', 'unread'].map(t => (
                    <button
                        key={t} onClick={() => { setTab(t); setPage(1) }}
                        style={{
                            height: 34, padding: '0 18px', border: 'none', borderRadius: 8,
                            fontSize: 13.5, fontWeight: 600, cursor: 'pointer',
                            background: tab === t ? 'var(--bg-card)' : 'transparent',
                            color: tab === t ? 'var(--text-primary)' : 'var(--text-muted)',
                            boxShadow: tab === t ? 'var(--shadow-card)' : 'none',
                        }}
                    >
                        {t.charAt(0).toUpperCase() + t.slice(1)}
                    </button>
                ))}
            </div>

            {/* ── List ── */}
            <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-card)', boxShadow: 'var(--shadow-card)', overflow: 'hidden' }}>
                {loading ? (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 60 }}>
                        <span className="spinner" style={{ width: 24, height: 24 }} />
                    </div>
                ) : notifications.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: 60 }}>
                        <div style={{ fontSize: 36, marginBottom: 12 }}>🔔</div>
                        <div style={{ fontWeight: 600, fontSize: 16, marginBottom: 6 }}>
                            {tab === 'unread' ? 'All caught up!' : 'No notifications yet'}
                        </div>
                        <div style={{ color: 'var(--text-muted)', fontSize: 14 }}>
                            {tab === 'unread' ? "You've read everything." : "Notifications will appear here when your spending changes."}
                        </div>
                    </div>
                ) : (
                    <div>
                        {notifications.map((n, i) => {
                            const style = getTypeStyle(n.notification_type ?? n.type)
                            return (
                                <div
                                    key={n.id}
                                    style={{
                                        display: 'flex', alignItems: 'flex-start', gap: 14, padding: '16px 18px',
                                        borderBottom: i < notifications.length - 1 ? '1px solid var(--border-subtle)' : 'none',
                                        background: n.is_read ? 'transparent' : 'var(--primary-light)',
                                        cursor: n.is_read ? 'default' : 'pointer',
                                    }}
                                    onClick={() => !n.is_read && handleMarkRead(n.id)}
                                >
                                    {/* Icon */}
                                    <div style={{ width: 40, height: 40, borderRadius: 10, background: style.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, fontSize: 18 }}>
                                        {style.icon}
                                    </div>

                                    {/* Content */}
                                    <div style={{ flex: 1, minWidth: 0 }}>
                                        <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 8, marginBottom: 4 }}>
                                            <div style={{ fontSize: 14, fontWeight: n.is_read ? 500 : 700, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                                {n.title ?? n.message ?? 'Notification'}
                                            </div>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexShrink: 0 }}>
                                                <span style={{ fontSize: 12, color: 'var(--text-subtle)' }}>
                                                    {formatDate(n.created_at ?? n.date)}
                                                </span>
                                                {!n.is_read && (
                                                    <span style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--primary)', flexShrink: 0 }} />
                                                )}
                                            </div>
                                        </div>
                                        {(n.message || n.body) && (
                                            <div style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.45 }}>
                                                {n.body ?? n.message}
                                            </div>
                                        )}
                                        {!n.is_read && (
                                            <button
                                                onClick={e => { e.stopPropagation(); handleMarkRead(n.id) }}
                                                style={{ marginTop: 8, fontSize: 12, fontWeight: 600, color: 'var(--primary)', background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
                                            >
                                                Mark as read
                                            </button>
                                        )}
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                )}

                {/* Pagination */}
                {(hasNext || hasPrev) && (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 18px', borderTop: '1px solid var(--border-subtle)' }}>
                        <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>Page {page}</span>
                        <div style={{ display: 'flex', gap: 6 }}>
                            <button onClick={() => goPage(page - 1)} disabled={!hasPrev} style={pageBtnStyle(!hasPrev)}>← Prev</button>
                            <button onClick={() => goPage(page + 1)} disabled={!hasNext} style={pageBtnStyle(!hasNext)}>Next →</button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}

const pageBtnStyle = disabled => ({
    height: 34, padding: '0 14px', border: '1.5px solid var(--border-input)', borderRadius: 8,
    fontSize: 13.5, fontWeight: 600, cursor: disabled ? 'not-allowed' : 'pointer',
    background: 'var(--bg-card)', color: disabled ? 'var(--text-subtle)' : 'var(--text-primary)',
    opacity: disabled ? 0.5 : 1,
})
