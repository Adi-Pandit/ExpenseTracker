import { useState, useEffect } from 'react'
import { listRecurring, updateRecurring } from '../api/recurring'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { formatAmount, formatDate } from '../utils/format'
import { getCategoryColor } from '../utils/colors'
import RecurringModal from '../components/modals/RecurringModal'

const FREQ_LABEL = { daily: 'Daily', weekly: 'Weekly', monthly: 'Monthly', yearly: 'Yearly' }

export default function Recurring() {
    const { user } = useAuth()
    const toast = useToast()
    const currency = user?.base_currency ?? 'INR'

    const [items, setItems] = useState([])
    const [loading, setLoading] = useState(true)
    const [activeTab, setActiveTab] = useState('active')
    const [editingItem, setEditingItem] = useState(null)
    const [addOpen, setAddOpen] = useState(false)

    async function load() {
        setLoading(true)
        try {
            const data = await listRecurring()
            setItems(Array.isArray(data) ? data : (data.results ?? []))
        } catch {
            toast.error('Failed to load recurring expenses.')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => { load() }, []) // eslint-disable-line react-hooks/exhaustive-deps

    async function toggleActive(item) {
        try {
            const updated = await updateRecurring(item.id, { is_active: !item.is_active })
            setItems(prev => prev.map(i => i.id === item.id ? updated : i))
            toast.success(updated.is_active ? 'Enabled.' : 'Paused.')
        } catch {
            toast.error('Could not update status.')
        }
    }

    const filtered = items.filter(i => activeTab === 'active' ? i.is_active : !i.is_active)

    return (
        <div className="page">
            {/* ── Header ── */}
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, marginBottom: 20 }}>
                <div>
                    <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0, letterSpacing: '-0.02em' }}>Recurring</h1>
                    <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: '4px 0 0' }}>
                        Subscriptions and bills that repeat on schedule.
                    </p>
                </div>
                <button
                    onClick={() => setAddOpen(true)}
                    style={{ height: 40, padding: '0 18px', display: 'flex', alignItems: 'center', gap: 7, background: 'var(--primary)', color: '#fff', border: 'none', borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: 'pointer', boxShadow: 'var(--shadow-btn)' }}
                >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                        <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                    </svg>
                    Add recurring
                </button>
            </div>

            {/* ── Tabs ── */}
            <div style={{ display: 'flex', gap: 4, marginBottom: 16, background: 'var(--bg-muted)', padding: 4, borderRadius: 10, width: 'fit-content' }}>
                {['active', 'paused'].map(tab => (
                    <button
                        key={tab} onClick={() => setActiveTab(tab)}
                        style={{
                            height: 34, padding: '0 18px', border: 'none', borderRadius: 8,
                            fontSize: 13.5, fontWeight: 600, cursor: 'pointer',
                            background: activeTab === tab ? 'var(--bg-card)' : 'transparent',
                            color: activeTab === tab ? 'var(--text-primary)' : 'var(--text-muted)',
                            boxShadow: activeTab === tab ? 'var(--shadow-card)' : 'none',
                        }}
                    >
                        {tab.charAt(0).toUpperCase() + tab.slice(1)}
                        <span style={{ marginLeft: 6, fontSize: 11.5, fontWeight: 700, color: activeTab === tab ? 'var(--primary)' : 'var(--text-subtle)' }}>
                            {items.filter(i => tab === 'active' ? i.is_active : !i.is_active).length}
                        </span>
                    </button>
                ))}
            </div>

            {loading ? (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 80 }}>
                    <span className="spinner" style={{ width: 26, height: 26 }} />
                </div>
            ) : filtered.length === 0 ? (
                <div style={{ textAlign: 'center', padding: 80 }}>
                    <div style={{ fontSize: 36, marginBottom: 12 }}>🔄</div>
                    <div style={{ fontWeight: 600, fontSize: 16, marginBottom: 8 }}>
                        {activeTab === 'active' ? 'No active recurring expenses' : 'No paused recurring expenses'}
                    </div>
                    <div style={{ color: 'var(--text-muted)', fontSize: 14 }}>
                        {activeTab === 'active' ? 'Set up subscriptions and bills to track them automatically.' : ''}
                    </div>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                    {filtered.map(item => {
                        const cat = item.category_name ?? 'Other'
                        const colors = getCategoryColor(cat)
                        return (
                            <div
                                key={item.id}
                                style={{
                                    background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)',
                                    border: '1px solid var(--border-card)', padding: '16px 18px',
                                    boxShadow: 'var(--shadow-card)', display: 'flex', alignItems: 'center', gap: 14,
                                    opacity: item.is_active ? 1 : 0.65,
                                }}
                            >
                                {/* Icon */}
                                <div style={{ width: 42, height: 42, borderRadius: 10, background: colors.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={colors.text} strokeWidth="2" strokeLinecap="round">
                                        <polyline points="23 4 23 10 17 10"/>
                                        <path d="M20.49 15a9 9 0 11-2.12-9.36L23 10"/>
                                    </svg>
                                </div>

                                {/* Info */}
                                <div style={{ flex: 1, minWidth: 0 }}>
                                    <div style={{ fontSize: 14.5, fontWeight: 600, marginBottom: 3, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                        {item.notes || cat}
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                                        <span style={{ fontSize: 12, padding: '2px 8px', borderRadius: 20, background: colors.bg, color: colors.text, fontWeight: 600 }}>{cat}</span>
                                        <span style={{ fontSize: 12, color: 'var(--text-subtle)' }}>{item.account_name ?? ''}</span>
                                    </div>
                                </div>

                                {/* Frequency + next run */}
                                <div style={{ textAlign: 'center', flexShrink: 0, display: 'none' }} className="md-show">
                                    <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--primary)', marginBottom: 2 }}>{FREQ_LABEL[item.frequency] ?? item.frequency}</div>
                                    <div style={{ fontSize: 11.5, color: 'var(--text-subtle)' }}>next {item.next_run_date ? formatDate(item.next_run_date) : '—'}</div>
                                </div>

                                {/* Frequency + next run (always visible) */}
                                <div style={{ textAlign: 'center', flexShrink: 0 }}>
                                    <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--primary)', marginBottom: 2 }}>{FREQ_LABEL[item.frequency] ?? item.frequency}</div>
                                    <div style={{ fontSize: 11.5, color: 'var(--text-subtle)' }}>next {item.next_run_date ? formatDate(item.next_run_date) : '—'}</div>
                                </div>

                                {/* Amount */}
                                <div style={{ textAlign: 'right', flexShrink: 0 }}>
                                    <div style={{ fontSize: 16, fontWeight: 700 }}>{formatAmount(Number(item.amount), item.currency)}</div>
                                    {item.currency !== currency && (
                                        <div style={{ fontSize: 11.5, color: 'var(--text-subtle)' }}>{item.currency}</div>
                                    )}
                                </div>

                                {/* Actions */}
                                <div style={{ display: 'flex', gap: 6, flexShrink: 0 }}>
                                    {/* Toggle */}
                                    <button
                                        onClick={() => toggleActive(item)}
                                        title={item.is_active ? 'Pause' : 'Resume'}
                                        style={{
                                            width: 32, height: 32, border: 'none',
                                            background: item.is_active ? 'var(--success-bg)' : 'var(--bg-muted)',
                                            color: item.is_active ? 'var(--success)' : 'var(--text-muted)',
                                            borderRadius: 8, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
                                        }}
                                    >
                                        {item.is_active ? (
                                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                                                <rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/>
                                            </svg>
                                        ) : (
                                            <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor">
                                                <polygon points="5 3 19 12 5 21 5 3"/>
                                            </svg>
                                        )}
                                    </button>
                                    {/* Edit */}
                                    <button
                                        onClick={() => setEditingItem(item)}
                                        style={{ width: 32, height: 32, border: 'none', background: 'var(--bg-muted)', color: 'var(--text-muted)', borderRadius: 8, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                                    >
                                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
                                            <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                                            <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        )
                    })}
                </div>
            )}

            {addOpen && <RecurringModal onClose={() => setAddOpen(false)} onSaved={() => { setAddOpen(false); load() }} />}
            {editingItem && <RecurringModal recurring={editingItem} onClose={() => setEditingItem(null)} onSaved={() => { setEditingItem(null); load() }} />}
        </div>
    )
}
