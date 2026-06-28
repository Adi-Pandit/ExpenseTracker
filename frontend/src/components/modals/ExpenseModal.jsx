import { useState, useEffect } from 'react'
import { createExpense, updateExpense, deleteExpense } from '../../api/expenses'
import { listCategories } from '../../api/categories'
import { listAccounts } from '../../api/accounts'
import { useToast } from '../../context/ToastContext'
import { useIsMobile } from '../../hooks/useWindowWidth'
import ModalPortal from './ModalPortal'

const CURRENCIES = ['INR', 'USD', 'EUR', 'GBP', 'AED', 'SGD']

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

export default function ExpenseModal({ expense, onClose, onSaved }) {
    const isEdit = Boolean(expense)
    const toast = useToast()
    const isMobile = useIsMobile()

    const [form, setForm] = useState({
        amount: expense?.amount ?? '',
        currency: expense?.currency ?? 'INR',
        date: expense?.date ?? today(),
        account: expense?.account ?? '',
        category: expense?.category ?? '',
        notes: expense?.notes ?? '',
    })
    const [accounts, setAccounts] = useState([])
    const [categories, setCategories] = useState([])
    const [saving, setSaving] = useState(false)
    const [deleting, setDeleting] = useState(false)
    const [confirmDelete, setConfirmDelete] = useState(false)
    const [error, setError] = useState('')

    useEffect(() => {
        Promise.all([listAccounts(), listCategories()])
            .then(([accs, cats]) => {
                const accList = Array.isArray(accs) ? accs : (accs.results ?? [])
                const catList = Array.isArray(cats) ? cats : (cats.results ?? [])
                setAccounts(accList)
                setCategories(catList)
                /* pre-select first account if adding new */
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
        if (!form.amount || !form.account || !form.date) {
            setError('Amount, account and date are required.')
            return
        }
        setSaving(true)
        setError('')
        try {
            const payload = {
                amount: form.amount,
                currency: form.currency,
                date: form.date,
                account: form.account,
                category: form.category || null,
                notes: form.notes,
            }
            const saved = isEdit
                ? await updateExpense(expense.id, payload)
                : await createExpense(payload)
            toast.success(isEdit ? 'Expense updated.' : 'Expense added.')
            onSaved(saved)
        } catch (err) {
            const msg = err.response?.data
            if (typeof msg === 'object') {
                setError(Object.values(msg).flat().join(' '))
            } else {
                setError('Something went wrong. Please try again.')
            }
        } finally {
            setSaving(false)
        }
    }

    async function handleDelete() {
        if (!confirmDelete) { setConfirmDelete(true); return }
        setDeleting(true)
        try {
            await deleteExpense(expense.id)
            toast.success('Expense deleted.')
            onSaved(null)
        } catch {
            toast.error('Could not delete expense.')
            setDeleting(false)
            setConfirmDelete(false)
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
                    padding: '20px 20px 32px',
                    width: '100%',
                    maxWidth: isMobile ? '100%' : 480,
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
                            {isEdit ? 'Edit Expense' : 'Add Expense'}
                        </h3>
                        <p style={{ fontSize: 13, color: 'var(--text-subtle)', margin: '3px 0 0' }}>
                            Record where your money went.
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        style={{
                            border: 'none', background: 'var(--bg-muted)',
                            width: 34, height: 34, borderRadius: 9,
                            cursor: 'pointer', color: 'var(--text-muted)',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            flexShrink: 0,
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
                                type="number"
                                min="0.01"
                                step="0.01"
                                placeholder="0.00"
                                value={form.amount}
                                onChange={e => set('amount', e.target.value)}
                                style={{ ...field.input, fontSize: 16, fontWeight: 600 }}
                                required
                            />
                        </div>
                        <div>
                            <label style={field.label}>Currency</label>
                            <select
                                value={form.currency}
                                onChange={e => set('currency', e.target.value)}
                                style={{ ...field.input, paddingLeft: 10 }}
                            >
                                {CURRENCIES.map(c => <option key={c} value={c}>{c}</option>)}
                            </select>
                        </div>
                    </div>

                    {/* Date */}
                    <div style={{ marginBottom: 14 }}>
                        <label style={field.label}>Date</label>
                        <input
                            type="date"
                            value={form.date}
                            max={today()}
                            onChange={e => set('date', e.target.value)}
                            style={field.input}
                            required
                        />
                    </div>

                    {/* Account + Category */}
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 13, marginBottom: 14 }}>
                        <div>
                            <label style={field.label}>Account</label>
                            <select
                                value={form.account}
                                onChange={e => set('account', e.target.value)}
                                style={{ ...field.input, paddingLeft: 10 }}
                                required
                            >
                                <option value="">Select…</option>
                                {accounts.map(a => (
                                    <option key={a.id} value={a.id}>{a.name}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label style={field.label}>Category</label>
                            <select
                                value={form.category}
                                onChange={e => set('category', e.target.value)}
                                style={{ ...field.input, paddingLeft: 10 }}
                            >
                                <option value="">Uncategorized</option>
                                {categories.map(c => (
                                    <option key={c.id} value={c.id}>{c.name}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {/* Notes */}
                    <div style={{ marginBottom: 22 }}>
                        <label style={field.label}>Notes</label>
                        <input
                            type="text"
                            placeholder="What was this for?"
                            value={form.notes}
                            onChange={e => set('notes', e.target.value)}
                            style={field.input}
                        />
                    </div>

                    {/* Actions */}
                    <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                        {isEdit && (
                            <button
                                type="button"
                                onClick={handleDelete}
                                disabled={deleting}
                                style={{
                                    height: 42, padding: '0 16px',
                                    background: confirmDelete ? 'var(--danger)' : 'var(--bg-card)',
                                    color: confirmDelete ? '#fff' : 'var(--danger)',
                                    border: '1.5px solid var(--danger-border)',
                                    borderRadius: 9, fontSize: 14, fontWeight: 600,
                                    cursor: 'pointer', transition: 'var(--t)',
                                }}
                            >
                                {deleting ? '…' : confirmDelete ? 'Confirm delete' : 'Delete'}
                            </button>
                        )}
                        <div style={{ flex: 1 }} />
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
                            {saving ? '…' : isEdit ? 'Save changes' : 'Add expense'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
        </ModalPortal>
    )
}
