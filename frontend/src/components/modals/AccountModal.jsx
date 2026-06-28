import { useState } from 'react'
import { createAccount, updateAccount } from '../../api/accounts'
import { useToast } from '../../context/ToastContext'
import { useIsMobile } from '../../hooks/useWindowWidth'
import ModalPortal from './ModalPortal'

const TYPES = [
    { value: 'bank',        label: 'Bank' },
    { value: 'cash',        label: 'Cash' },
    { value: 'credit_card', label: 'Credit Card' },
]

const field = {
    label: {
        display: 'block',
        fontSize: 13,
        fontWeight: 600,
        color: 'var(--text-secondary)',
        marginBottom: 6,
    },
    input: {
        width: '100%',
        height: 44,
        padding: '0 13px',
        border: '1.5px solid var(--border-input)',
        borderRadius: 'var(--radius-md)',
        fontSize: 15,
        outline: 'none',
        fontFamily: 'var(--font)',
        color: 'var(--text-primary)',
        background: 'var(--bg-card)',
        boxSizing: 'border-box',
    },
}

export default function AccountModal({ account, onClose, onSaved }) {
    const isEdit = Boolean(account)
    const toast = useToast()
    const isMobile = useIsMobile()

    const [form, setForm] = useState({
        name: account?.name ?? '',
        account_type: account?.account_type ?? 'bank',
        opening_balance: account?.opening_balance ?? '0',
    })
    const [saving, setSaving] = useState(false)
    const [error, setError] = useState('')

    function set(key, val) {
        setForm(f => ({ ...f, [key]: val }))
        setError('')
    }

    async function handleSubmit(e) {
        e.preventDefault()
        if (!form.name.trim()) { setError('Account name is required.'); return }
        setSaving(true)
        setError('')
        try {
            const payload = {
                name: form.name.trim(),
                account_type: form.account_type,
                opening_balance: form.opening_balance || '0',
            }
            const saved = isEdit
                ? await updateAccount(account.id, payload)
                : await createAccount(payload)
            toast.success(isEdit ? 'Account updated.' : 'Account created.')
            onSaved(saved)
        } catch (err) {
            const msg = err.response?.data
            if (typeof msg === 'object') {
                setError(Object.values(msg).flat().join(' '))
            } else {
                setError('Something went wrong.')
            }
        } finally {
            setSaving(false)
        }
    }

    return (
        <ModalPortal>
        <div
            onClick={onClose}
            style={{
                position: 'fixed', inset: 0, zIndex: 50,
                background: 'rgba(17,24,39,0.45)',
                animation: 'lg-overlay 0.2s ease both',
                display: 'flex',
                alignItems: isMobile ? 'flex-end' : 'center',
                justifyContent: 'center',
                padding: isMobile ? 0 : '16px',
            }}
        >
            <div
                onClick={e => e.stopPropagation()}
                style={{
                    background: 'var(--bg-card)',
                    borderRadius: isMobile ? '20px 20px 0 0' : 'var(--radius-2xl)',
                    padding: isMobile ? '20px 20px 32px' : '24px',
                    width: '100%',
                    maxWidth: isMobile ? '100%' : 420,
                    animation: isMobile ? 'lg-bottom-sheet 0.3s ease both' : 'lg-sheet 0.25s ease both',
                    boxShadow: 'var(--shadow-modal)',
                }}
            >
                {isMobile && (
                    <div style={{ width: 36, height: 4, borderRadius: 2, background: 'var(--border-input)', margin: '0 auto 18px' }} />
                )}
                {/* Header */}
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 20 }}>
                    <div>
                        <h3 style={{ fontSize: 19, fontWeight: 700, margin: 0 }}>
                            {isEdit ? 'Edit Account' : 'Add Account'}
                        </h3>
                        <p style={{ fontSize: 13, color: 'var(--text-subtle)', margin: '3px 0 0' }}>
                            Track balances across accounts.
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        style={{
                            border: 'none', background: 'var(--bg-muted)',
                            width: 34, height: 34, borderRadius: 9,
                            cursor: 'pointer', color: 'var(--text-muted)',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                        }}
                    >
                        <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
                            <path d="M18 6 6 18M6 6l12 12"/>
                        </svg>
                    </button>
                </div>

                {error && (
                    <div style={{
                        background: 'var(--danger-bg)', border: '1px solid var(--danger-border)',
                        color: 'var(--danger-dark)', padding: '10px 12px',
                        borderRadius: 9, fontSize: 13, fontWeight: 500, marginBottom: 16,
                        display: 'flex', alignItems: 'center', gap: 8,
                    }}>
                        <span style={{ width: 7, height: 7, borderRadius: '50%', background: 'var(--danger)', flexShrink: 0 }} />
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    {/* Name */}
                    <div style={{ marginBottom: 14 }}>
                        <label style={field.label}>Account name</label>
                        <input
                            type="text"
                            placeholder="e.g. HDFC Savings"
                            value={form.name}
                            onChange={e => set('name', e.target.value)}
                            style={field.input}
                            required
                            autoFocus
                        />
                    </div>

                    {/* Type + Opening balance */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 13, marginBottom: 22 }}>
                        <div>
                            <label style={field.label}>Type</label>
                            <select
                                value={form.account_type}
                                onChange={e => set('account_type', e.target.value)}
                                style={{ ...field.input, paddingLeft: 10 }}
                            >
                                {TYPES.map(t => (
                                    <option key={t.value} value={t.value}>{t.label}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label style={field.label}>Opening balance</label>
                            <input
                                type="number"
                                min="0"
                                step="0.01"
                                placeholder="0.00"
                                value={form.opening_balance}
                                onChange={e => set('opening_balance', e.target.value)}
                                style={field.input}
                            />
                        </div>
                    </div>

                    {/* Actions */}
                    <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
                        <button
                            type="button"
                            onClick={onClose}
                            style={{
                                height: 42, padding: '0 18px',
                                background: 'var(--bg-card)',
                                color: 'var(--text-secondary)',
                                border: '1.5px solid var(--border-input)',
                                borderRadius: 9, fontSize: 14, fontWeight: 600,
                                cursor: 'pointer',
                            }}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={saving}
                            style={{
                                height: 42, padding: '0 22px',
                                background: 'var(--primary)',
                                color: '#fff', border: 'none',
                                borderRadius: 9, fontSize: 14, fontWeight: 600,
                                cursor: 'pointer',
                                boxShadow: 'var(--shadow-btn)',
                            }}
                        >
                            {saving ? '…' : isEdit ? 'Save changes' : 'Create account'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
        </ModalPortal>
    )
}
