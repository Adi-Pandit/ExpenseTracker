import { useState, useEffect } from 'react'
import { createRecurring, updateRecurring } from '../../api/recurring'
import { listCategories } from '../../api/categories'
import { listAccounts } from '../../api/accounts'
import { useToast } from '../../context/ToastContext'
import { useIsMobile } from '../../hooks/useWindowWidth'
import ModalPortal from './ModalPortal'

const CURRENCIES = ['INR', 'USD', 'EUR', 'GBP', 'AED', 'SGD']

const FREQUENCIES = [
    { value: 'daily',   label: 'Daily' },
    { value: 'weekly',  label: 'Weekly' },
    { value: 'monthly', label: 'Monthly' },
    { value: 'yearly',  label: 'Yearly' },
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

function today() {
    return new Date().toISOString().split('T')[0]
}

export default function RecurringModal({ recurring, onClose, onSaved }) {
    const isEdit = Boolean(recurring)
    const toast = useToast()
    const isMobile = useIsMobile()

    const [form, setForm] = useState({
        amount: recurring?.amount ?? '',
        currency: recurring?.currency ?? 'INR',
        account: recurring?.account ?? '',
        category: recurring?.category ?? '',
        notes: recurring?.notes ?? '',
        frequency: recurring?.frequency ?? 'monthly',
        start_date: recurring?.start_date ?? today(),
        next_run_date: recurring?.next_run_date ?? today(),
        is_active: recurring?.is_active ?? true,
    })
    const [accounts, setAccounts] = useState([])
    const [categories, setCategories] = useState([])
    const [saving, setSaving] = useState(false)
    const [error, setError] = useState('')

    useEffect(() => {
        Promise.all([listAccounts(), listCategories()])
            .then(([accs, cats]) => {
                const accList = Array.isArray(accs) ? accs : (accs.results ?? [])
                const catList = Array.isArray(cats) ? cats : (cats.results ?? [])
                setAccounts(accList)
                setCategories(catList)
                if (!isEdit && accList.length && !form.account) {
                    setForm(f => ({ ...f, account: accList[0].id }))
                }
            })
            .catch(() => {})
    }, []) // eslint-disable-line react-hooks/exhaustive-deps

    function set(key, val) {
        setForm(f => ({ ...f, [key]: val }))
        setError('')
    }

    async function handleSubmit(e) {
        e.preventDefault()
        if (!form.amount || !form.account) {
            setError('Amount and account are required.')
            return
        }
        setSaving(true)
        setError('')
        try {
            const payload = {
                amount: form.amount,
                currency: form.currency,
                account: form.account,
                category: form.category || null,
                notes: form.notes,
                frequency: form.frequency,
                start_date: form.start_date,
                next_run_date: form.next_run_date,
                is_active: form.is_active,
            }
            const saved = isEdit
                ? await updateRecurring(recurring.id, payload)
                : await createRecurring(payload)
            toast.success(isEdit ? 'Recurring expense updated.' : 'Recurring expense created.')
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
                    maxWidth: isMobile ? '100%' : 500,
                    animation: isMobile ? 'lg-bottom-sheet 0.3s ease both' : 'lg-sheet 0.25s ease both',
                    boxShadow: 'var(--shadow-modal)',
                    maxHeight: '92vh',
                    overflowY: 'auto',
                }}
            >
                {isMobile && (
                    <div style={{ width: 36, height: 4, borderRadius: 2, background: 'var(--border-input)', margin: '0 auto 18px' }} />
                )}
                {/* Header */}
                <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 20 }}>
                    <div>
                        <h3 style={{ fontSize: 19, fontWeight: 700, margin: 0 }}>
                            {isEdit ? 'Edit Recurring' : 'Add Recurring'}
                        </h3>
                        <p style={{ fontSize: 13, color: 'var(--text-subtle)', margin: '3px 0 0' }}>
                            Set up an expense that repeats on schedule.
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
                    {/* Amount + Currency */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: 13, marginBottom: 14 }}>
                        <div>
                            <label style={field.label}>Amount</label>
                            <input
                                type="number" min="0.01" step="0.01" placeholder="0.00"
                                value={form.amount}
                                onChange={e => set('amount', e.target.value)}
                                style={{ ...field.input, fontSize: 16, fontWeight: 600 }}
                                required
                            />
                        </div>
                        <div>
                            <label style={field.label}>Currency</label>
                            <select value={form.currency} onChange={e => set('currency', e.target.value)} style={{ ...field.input, paddingLeft: 10 }}>
                                {CURRENCIES.map(c => <option key={c} value={c}>{c}</option>)}
                            </select>
                        </div>
                    </div>

                    {/* Account + Category */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 13, marginBottom: 14 }}>
                        <div>
                            <label style={field.label}>Account</label>
                            <select value={form.account} onChange={e => set('account', e.target.value)} style={{ ...field.input, paddingLeft: 10 }} required>
                                <option value="">Select…</option>
                                {accounts.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
                            </select>
                        </div>
                        <div>
                            <label style={field.label}>Category</label>
                            <select value={form.category} onChange={e => set('category', e.target.value)} style={{ ...field.input, paddingLeft: 10 }}>
                                <option value="">Uncategorized</option>
                                {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                            </select>
                        </div>
                    </div>

                    {/* Notes */}
                    <div style={{ marginBottom: 14 }}>
                        <label style={field.label}>Notes</label>
                        <input
                            type="text" placeholder="e.g. Netflix subscription"
                            value={form.notes}
                            onChange={e => set('notes', e.target.value)}
                            style={field.input}
                        />
                    </div>

                    {/* Frequency + Start date */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 13, marginBottom: 14 }}>
                        <div>
                            <label style={field.label}>Frequency</label>
                            <select value={form.frequency} onChange={e => set('frequency', e.target.value)} style={{ ...field.input, paddingLeft: 10 }}>
                                {FREQUENCIES.map(f => <option key={f.value} value={f.value}>{f.label}</option>)}
                            </select>
                        </div>
                        <div>
                            <label style={field.label}>Start date</label>
                            <input type="date" value={form.start_date} onChange={e => set('start_date', e.target.value)} style={field.input} />
                        </div>
                    </div>

                    {/* Next run date + Active toggle */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 13, marginBottom: 22 }}>
                        <div>
                            <label style={field.label}>Next run date</label>
                            <input type="date" value={form.next_run_date} onChange={e => set('next_run_date', e.target.value)} style={field.input} />
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column' }}>
                            <label style={field.label}>Status</label>
                            <label style={{
                                display: 'flex', alignItems: 'center', gap: 10,
                                height: 44, cursor: 'pointer', fontSize: 14, fontWeight: 500,
                                color: 'var(--text-secondary)',
                            }}>
                                <input
                                    type="checkbox"
                                    checked={form.is_active}
                                    onChange={e => set('is_active', e.target.checked)}
                                    style={{ width: 17, height: 17, accentColor: 'var(--primary)', cursor: 'pointer' }}
                                />
                                Active
                            </label>
                        </div>
                    </div>

                    {/* Actions */}
                    <div style={{ display: 'flex', gap: 10, justifyContent: 'flex-end' }}>
                        <button
                            type="button" onClick={onClose}
                            style={{
                                height: 42, padding: '0 18px',
                                background: 'var(--bg-card)', color: 'var(--text-secondary)',
                                border: '1.5px solid var(--border-input)',
                                borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: 'pointer',
                            }}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit" disabled={saving}
                            style={{
                                height: 42, padding: '0 22px',
                                background: 'var(--primary)', color: '#fff', border: 'none',
                                borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: 'pointer',
                                boxShadow: 'var(--shadow-btn)',
                            }}
                        >
                            {saving ? '…' : isEdit ? 'Save changes' : 'Create recurring'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
        </ModalPortal>
    )
}
