import { useState, useEffect } from 'react'
import { listAccounts } from '../api/accounts'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { formatAmount } from '../utils/format'
import { getAccountBadge, getAccountLabel } from '../utils/colors'
import AccountModal from '../components/modals/AccountModal'

export default function Accounts() {
    const { user } = useAuth()
    const toast = useToast()
    const currency = user?.base_currency ?? 'INR'

    const [accounts, setAccounts] = useState([])
    const [loading, setLoading] = useState(true)
    const [editingAccount, setEditingAccount] = useState(null)
    const [addOpen, setAddOpen] = useState(false)

    async function load() {
        try {
            const data = await listAccounts()
            setAccounts(Array.isArray(data) ? data : (data.results ?? []))
        } catch {
            toast.error('Failed to load accounts.')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => { load() }, []) // eslint-disable-line react-hooks/exhaustive-deps

    function handleSaved() {
        setAddOpen(false)
        setEditingAccount(null)
        load()
    }

    const totalBalance = accounts.reduce((sum, a) => sum + Number(a.current_balance ?? a.opening_balance ?? 0), 0)

    return (
        <div className="page">
            {/* ── Header ── */}
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, marginBottom: 24 }}>
                <div>
                    <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0, letterSpacing: '-0.02em' }}>Accounts</h1>
                    <div style={{ display: 'flex', align: 'center', gap: 12, marginTop: 6 }}>
                        <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>{accounts.length} account{accounts.length !== 1 ? 's' : ''}</span>
                        {accounts.length > 0 && (
                            <>
                                <span style={{ color: 'var(--border-subtle)' }}>·</span>
                                <span style={{ fontSize: 13, color: 'var(--text-secondary)', fontWeight: 600 }}>
                                    Total balance: {formatAmount(totalBalance, currency)}
                                </span>
                            </>
                        )}
                    </div>
                </div>
                <button
                    onClick={() => setAddOpen(true)}
                    style={{
                        height: 40, padding: '0 18px', display: 'flex', alignItems: 'center', gap: 7,
                        background: 'var(--primary)', color: '#fff', border: 'none',
                        borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: 'pointer',
                        boxShadow: 'var(--shadow-btn)',
                    }}
                >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                        <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                    </svg>
                    Add account
                </button>
            </div>

            {loading ? (
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 80 }}>
                    <span className="spinner" style={{ width: 26, height: 26 }} />
                </div>
            ) : accounts.length === 0 ? (
                <div style={{ textAlign: 'center', padding: 80 }}>
                    <div style={{ fontSize: 36, marginBottom: 12 }}>🏦</div>
                    <div style={{ fontWeight: 600, fontSize: 17, marginBottom: 8 }}>No accounts yet</div>
                    <div style={{ color: 'var(--text-muted)', fontSize: 14, marginBottom: 20 }}>Add a bank, cash, or credit card account to start tracking.</div>
                    <button
                        onClick={() => setAddOpen(true)}
                        style={{ height: 40, padding: '0 22px', background: 'var(--primary)', color: '#fff', border: 'none', borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: 'pointer', boxShadow: 'var(--shadow-btn)' }}
                    >
                        Add your first account
                    </button>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 14 }}>
                    {accounts.map(account => {
                        const badge = getAccountBadge(account.account_type)
                        const label = getAccountLabel(account.account_type)
                        const balance = Number(account.current_balance ?? account.opening_balance ?? 0)
                        return (
                            <div
                                key={account.id}
                                style={{
                                    background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)',
                                    border: '1px solid var(--border-card)', padding: '20px',
                                    boxShadow: 'var(--shadow-card)',
                                }}
                            >
                                {/* Card header */}
                                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 16 }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                                        <div style={{ width: 42, height: 42, borderRadius: 11, background: badge.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={badge.text} strokeWidth="2" strokeLinecap="round">
                                                <rect x="2" y="5" width="20" height="14" rx="2"/>
                                                <line x1="2" y1="10" x2="22" y2="10"/>
                                            </svg>
                                        </div>
                                        <div>
                                            <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 2 }}>{account.name}</div>
                                            <span style={{ display: 'inline-block', padding: '2px 8px', borderRadius: 20, background: badge.bg, color: badge.text, fontSize: 11.5, fontWeight: 600 }}>{label}</span>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => setEditingAccount(account)}
                                        style={{ width: 32, height: 32, border: 'none', background: 'var(--bg-muted)', borderRadius: 8, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', flexShrink: 0 }}
                                    >
                                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
                                            <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7"/>
                                            <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z"/>
                                        </svg>
                                    </button>
                                </div>

                                {/* Balance */}
                                <div style={{ padding: '14px', background: 'var(--bg-muted)', borderRadius: 10, marginBottom: 14 }}>
                                    <div style={{ fontSize: 12, color: 'var(--text-subtle)', marginBottom: 4 }}>Current balance</div>
                                    <div style={{ fontSize: 24, fontWeight: 700, letterSpacing: '-0.02em' }}>{formatAmount(balance, currency)}</div>
                                </div>

                                {/* Opening balance */}
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
                                    <span style={{ color: 'var(--text-muted)' }}>Opening balance</span>
                                    <span style={{ fontWeight: 600 }}>{formatAmount(Number(account.opening_balance ?? 0), currency)}</span>
                                </div>
                            </div>
                        )
                    })}
                </div>
            )}

            {addOpen && <AccountModal onClose={() => setAddOpen(false)} onSaved={handleSaved} />}
            {editingAccount && <AccountModal account={editingAccount} onClose={() => setEditingAccount(null)} onSaved={handleSaved} />}
        </div>
    )
}
