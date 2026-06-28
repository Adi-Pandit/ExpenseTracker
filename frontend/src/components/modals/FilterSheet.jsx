import { useState, useEffect } from 'react'
import { listCategories } from '../../api/categories'
import { listAccounts } from '../../api/accounts'
import ModalPortal from './ModalPortal'

const field = {
    label: {
        display: 'block',
        fontSize: 12,
        fontWeight: 600,
        color: 'var(--text-muted)',
        textTransform: 'uppercase',
        letterSpacing: '0.04em',
        marginBottom: 8,
    },
    input: {
        width: '100%',
        height: 42,
        padding: '0 12px',
        border: '1.5px solid var(--border-input)',
        borderRadius: 'var(--radius-md)',
        fontSize: 14,
        outline: 'none',
        fontFamily: 'var(--font)',
        color: 'var(--text-primary)',
        background: 'var(--bg-card)',
        boxSizing: 'border-box',
    },
}

const EMPTY = {
    category: '',
    account: '',
    start_date: '',
    end_date: '',
    min_amount: '',
    max_amount: '',
}

export default function FilterSheet({ filters, onClose, onApply }) {
    const [form, setForm] = useState({ ...EMPTY, ...filters })
    const [accounts, setAccounts] = useState([])
    const [categories, setCategories] = useState([])

    useEffect(() => {
        Promise.all([listAccounts(), listCategories()])
            .then(([accs, cats]) => {
                setAccounts(Array.isArray(accs) ? accs : (accs.results ?? []))
                setCategories(Array.isArray(cats) ? cats : (cats.results ?? []))
            })
            .catch(() => {})
    }, [])

    function set(key, val) {
        setForm(f => ({ ...f, [key]: val }))
    }

    function handleApply() {
        /* strip empty values before passing up */
        const clean = Object.fromEntries(
            Object.entries(form).filter(([, v]) => v !== '' && v !== null)
        )
        onApply(clean)
        onClose()
    }

    function handleClear() {
        setForm({ ...EMPTY })
        onApply({})
        onClose()
    }

    const activeCount = Object.values(form).filter(v => v !== '').length

    return (
        <ModalPortal>
        <div
            onClick={onClose}
            style={{
                position: 'fixed', inset: 0, zIndex: 50,
                background: 'rgba(17,24,39,0.45)',
                animation: 'lg-overlay 0.2s ease both',
                display: 'flex', justifyContent: 'flex-end',
            }}
        >
            <div
                onClick={e => e.stopPropagation()}
                style={{
                    width: '100%',
                    maxWidth: 360,
                    height: '100%',
                    background: 'var(--bg-card)',
                    padding: '24px 20px',
                    animation: 'lg-drawer 0.25s ease both',
                    boxShadow: '-8px 0 32px rgba(16,24,40,0.12)',
                    display: 'flex',
                    flexDirection: 'column',
                    overflowY: 'auto',
                }}
            >
                {/* Header */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
                    <div>
                        <h3 style={{ fontSize: 18, fontWeight: 700, margin: 0 }}>Filter expenses</h3>
                        {activeCount > 0 && (
                            <span style={{ fontSize: 12, color: 'var(--primary)', fontWeight: 600 }}>
                                {activeCount} filter{activeCount > 1 ? 's' : ''} active
                            </span>
                        )}
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

                {/* Filters */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 20, flex: 1 }}>
                    {/* Category */}
                    <div>
                        <label style={field.label}>Category</label>
                        <select value={form.category} onChange={e => set('category', e.target.value)} style={{ ...field.input, paddingLeft: 10 }}>
                            <option value="">All categories</option>
                            {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                        </select>
                    </div>

                    {/* Account */}
                    <div>
                        <label style={field.label}>Account</label>
                        <select value={form.account} onChange={e => set('account', e.target.value)} style={{ ...field.input, paddingLeft: 10 }}>
                            <option value="">All accounts</option>
                            {accounts.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
                        </select>
                    </div>

                    {/* Date range */}
                    <div>
                        <label style={field.label}>Date range</label>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                            <div>
                                <div style={{ fontSize: 11, color: 'var(--text-subtle)', marginBottom: 4 }}>From</div>
                                <input type="date" value={form.start_date} onChange={e => set('start_date', e.target.value)} style={field.input} />
                            </div>
                            <div>
                                <div style={{ fontSize: 11, color: 'var(--text-subtle)', marginBottom: 4 }}>To</div>
                                <input type="date" value={form.end_date} onChange={e => set('end_date', e.target.value)} style={field.input} />
                            </div>
                        </div>
                    </div>

                    {/* Amount range */}
                    <div>
                        <label style={field.label}>Amount range</label>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                            <div>
                                <div style={{ fontSize: 11, color: 'var(--text-subtle)', marginBottom: 4 }}>Min</div>
                                <input
                                    type="number" min="0" step="0.01" placeholder="0.00"
                                    value={form.min_amount} onChange={e => set('min_amount', e.target.value)}
                                    style={field.input}
                                />
                            </div>
                            <div>
                                <div style={{ fontSize: 11, color: 'var(--text-subtle)', marginBottom: 4 }}>Max</div>
                                <input
                                    type="number" min="0" step="0.01" placeholder="Any"
                                    value={form.max_amount} onChange={e => set('max_amount', e.target.value)}
                                    style={field.input}
                                />
                            </div>
                        </div>
                    </div>
                </div>

                {/* Actions */}
                <div style={{ display: 'flex', gap: 10, paddingTop: 24, borderTop: '1px solid var(--border-subtle)', marginTop: 24 }}>
                    <button
                        onClick={handleClear}
                        style={{
                            flex: 1, height: 42,
                            background: 'var(--bg-card)', color: 'var(--text-secondary)',
                            border: '1.5px solid var(--border-input)',
                            borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: 'pointer',
                        }}
                    >
                        Clear all
                    </button>
                    <button
                        onClick={handleApply}
                        style={{
                            flex: 1, height: 42,
                            background: 'var(--primary)', color: '#fff', border: 'none',
                            borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: 'pointer',
                            boxShadow: 'var(--shadow-btn)',
                        }}
                    >
                        Apply filters
                    </button>
                </div>
            </div>
        </div>
        </ModalPortal>
    )
}
