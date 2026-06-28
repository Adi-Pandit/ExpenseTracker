import { useState, useEffect, useCallback } from 'react'
import { listExpenses, exportExpenses } from '../api/expenses'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { useIsMobile } from '../hooks/useWindowWidth'
import { formatAmount, formatDate } from '../utils/format'
import { getCategoryColor } from '../utils/colors'
import ExpenseModal from '../components/modals/ExpenseModal'
import FilterSheet from '../components/modals/FilterSheet'

export default function Expenses() {
    const { user } = useAuth()
    const toast = useToast()
    const isMobile = useIsMobile()
    const currency = user?.base_currency ?? 'INR'

    const [expenses, setExpenses] = useState([])
    const [count, setCount] = useState(0)
    const [page, setPage] = useState(1)
    const [hasNext, setHasNext] = useState(false)
    const [hasPrev, setHasPrev] = useState(false)
    const [loading, setLoading] = useState(true)

    const [search, setSearch] = useState('')
    const [filters, setFilters] = useState({})
    const [filterOpen, setFilterOpen] = useState(false)
    const [exportOpen, setExportOpen] = useState(false)

    const [editingExpense, setEditingExpense] = useState(null)
    const [addOpen, setAddOpen] = useState(false)

    const activeFilterCount = Object.keys(filters).length

    const load = useCallback(async (pg = 1, q = search, f = filters) => {
        setLoading(true)
        try {
            const params = { page: pg, ...f }
            if (q) params.search = q
            const data = await listExpenses(params)
            setExpenses(data.results ?? [])
            setCount(data.count ?? 0)
            setHasNext(Boolean(data.next))
            setHasPrev(Boolean(data.previous))
        } catch {
            toast.error('Failed to load expenses.')
        } finally {
            setLoading(false)
        }
    }, []) // eslint-disable-line react-hooks/exhaustive-deps

    useEffect(() => { load(1, search, filters) }, []) // eslint-disable-line react-hooks/exhaustive-deps

    function handleSearch(e) {
        const q = e.target.value
        setSearch(q)
        setPage(1)
        load(1, q, filters)
    }

    function handleApplyFilters(f) {
        setFilters(f)
        setPage(1)
        load(1, search, f)
    }

    function goPage(p) {
        setPage(p)
        load(p, search, filters)
    }

    async function handleExport(format) {
        setExportOpen(false)
        try {
            const res = await exportExpenses({ ...filters, format })
            const url = URL.createObjectURL(res.data)
            const a = document.createElement('a')
            a.href = url
            a.download = `expenses.${format}`
            document.body.appendChild(a)
            a.click()
            document.body.removeChild(a)
            URL.revokeObjectURL(url)
            toast.success(`Exported as ${format.toUpperCase()}.`)
        } catch {
            toast.error('Export failed.')
        }
    }

    function handleSaved(saved) {
        setAddOpen(false)
        setEditingExpense(null)
        load(page, search, filters)
    }

    return (
        <div className="page">
            {/* ── Header ── */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, marginBottom: 20 }}>
                <div>
                    <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0, letterSpacing: '-0.02em' }}>Expenses</h1>
                    <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: '3px 0 0' }}>
                        {count.toLocaleString()} transaction{count !== 1 ? 's' : ''}
                    </p>
                </div>
                <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    {/* Search */}
                    <div style={{ position: 'relative' }}>
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="2.2" strokeLinecap="round" style={{ position: 'absolute', left: 11, top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none' }}>
                            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
                        </svg>
                        <input
                            value={search} onChange={handleSearch} placeholder="Search expenses…"
                            style={{ height: 38, paddingLeft: 34, paddingRight: 12, width: 200, border: '1.5px solid var(--border-input)', borderRadius: 9, fontSize: 14, outline: 'none', fontFamily: 'var(--font)', background: 'var(--bg-card)' }}
                        />
                    </div>

                    {/* Filter */}
                    <button
                        onClick={() => setFilterOpen(true)}
                        style={{
                            height: 38, padding: '0 14px', display: 'flex', alignItems: 'center', gap: 7,
                            background: activeFilterCount ? 'var(--primary-light)' : 'var(--bg-card)',
                            color: activeFilterCount ? 'var(--primary)' : 'var(--text-secondary)',
                            border: `1.5px solid ${activeFilterCount ? 'var(--primary-muted)' : 'var(--border-input)'}`,
                            borderRadius: 9, fontSize: 13.5, fontWeight: 600, cursor: 'pointer',
                        }}
                    >
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
                            <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
                        </svg>
                        Filters {activeFilterCount > 0 && `(${activeFilterCount})`}
                    </button>

                    {/* Export */}
                    <div style={{ position: 'relative' }}>
                        <button
                            onClick={() => setExportOpen(o => !o)}
                            style={{
                                height: 38, padding: '0 14px', display: 'flex', alignItems: 'center', gap: 7,
                                background: 'var(--bg-card)', color: 'var(--text-secondary)',
                                border: '1.5px solid var(--border-input)', borderRadius: 9,
                                fontSize: 13.5, fontWeight: 600, cursor: 'pointer',
                            }}
                        >
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
                                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/>
                            </svg>
                            Export
                        </button>
                        {exportOpen && (
                            <>
                                <div onClick={() => setExportOpen(false)} style={{ position: 'fixed', inset: 0, zIndex: 10 }} />
                                <div style={{
                                    position: 'absolute', right: 0, top: 44, zIndex: 20,
                                    background: 'var(--bg-card)', border: '1px solid var(--border-card)',
                                    borderRadius: 10, boxShadow: 'var(--shadow-float)', padding: 6, minWidth: 130,
                                }}>
                                    {['csv', 'xlsx', 'pdf'].map(fmt => (
                                        <button
                                            key={fmt} onClick={() => handleExport(fmt)}
                                            style={{ display: 'block', width: '100%', padding: '9px 13px', border: 'none', background: 'none', textAlign: 'left', fontSize: 13.5, fontWeight: 500, cursor: 'pointer', borderRadius: 7, color: 'var(--text-primary)' }}
                                        >
                                            {fmt.toUpperCase()}
                                        </button>
                                    ))}
                                </div>
                            </>
                        )}
                    </div>

                    {/* Add */}
                    <button
                        onClick={() => setAddOpen(true)}
                        style={{
                            height: 38, padding: '0 16px', display: 'flex', alignItems: 'center', gap: 7,
                            background: 'var(--primary)', color: '#fff', border: 'none',
                            borderRadius: 9, fontSize: 13.5, fontWeight: 600, cursor: 'pointer',
                            boxShadow: 'var(--shadow-btn)',
                        }}
                    >
                        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                        </svg>
                        Add
                    </button>
                </div>
            </div>

            {/* ── Table / Cards ── */}
            <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-card)', boxShadow: 'var(--shadow-card)', overflow: 'hidden' }}>
                {loading ? (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 60 }}>
                        <span className="spinner" style={{ width: 24, height: 24 }} />
                    </div>
                ) : expenses.length === 0 ? (
                    <div style={{ padding: 60, textAlign: 'center' }}>
                        <div style={{ fontSize: 32, marginBottom: 10 }}>🧾</div>
                        <div style={{ fontWeight: 600, fontSize: 16, marginBottom: 6 }}>No expenses found</div>
                        <div style={{ color: 'var(--text-muted)', fontSize: 14 }}>
                            {activeFilterCount || search ? 'Try adjusting your search or filters.' : 'Add your first expense to get started.'}
                        </div>
                    </div>
                ) : isMobile ? (
                    /* Mobile card list */
                    <div>
                        {expenses.map((exp, i) => {
                            const cat = exp.category_name ?? 'Other'
                            const colors = getCategoryColor(cat)
                            return (
                                <div
                                    key={exp.id}
                                    onClick={() => setEditingExpense(exp)}
                                    style={{
                                        display: 'flex', alignItems: 'center', gap: 12, padding: '14px 16px',
                                        borderBottom: i < expenses.length - 1 ? '1px solid var(--border-subtle)' : 'none',
                                        cursor: 'pointer',
                                    }}
                                >
                                    <div style={{ width: 38, height: 38, borderRadius: 10, background: colors.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                                        <span style={{ fontSize: 14, fontWeight: 700, color: colors.text }}>{cat.charAt(0)}</span>
                                    </div>
                                    <div style={{ flex: 1, minWidth: 0 }}>
                                        <div style={{ fontSize: 14, fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{exp.notes || cat}</div>
                                        <div style={{ fontSize: 12, color: 'var(--text-subtle)', marginTop: 2 }}>{formatDate(exp.date)} · {exp.account_name}</div>
                                    </div>
                                    <div style={{ fontSize: 14.5, fontWeight: 700, color: 'var(--danger)', flexShrink: 0 }}>
                                        −{formatAmount(exp.converted_amount ?? exp.amount, currency)}
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                ) : (
                    /* Desktop table */
                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                                {['Transaction', 'Date', 'Category', 'Account', 'Amount'].map(h => (
                                    <th key={h} style={{ padding: '12px 18px', fontSize: 12, fontWeight: 600, color: 'var(--text-muted)', textAlign: h === 'Amount' ? 'right' : 'left', textTransform: 'uppercase', letterSpacing: '0.04em' }}>{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {expenses.map((exp, i) => {
                                const cat = exp.category_name ?? 'Other'
                                const colors = getCategoryColor(cat)
                                return (
                                    <tr
                                        key={exp.id}
                                        onClick={() => setEditingExpense(exp)}
                                        style={{
                                            borderBottom: i < expenses.length - 1 ? '1px solid var(--border-subtle)' : 'none',
                                            cursor: 'pointer', transition: 'background .12s',
                                        }}
                                        onMouseEnter={e => e.currentTarget.style.background = 'var(--bg-hover)'}
                                        onMouseLeave={e => e.currentTarget.style.background = ''}
                                    >
                                        <td style={{ padding: '13px 18px' }}>
                                            <span style={{ fontSize: 14, fontWeight: 500, maxWidth: 220, display: 'block', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                                {exp.notes || '—'}
                                            </span>
                                        </td>
                                        <td style={{ padding: '13px 18px', fontSize: 13.5, color: 'var(--text-muted)' }}>{formatDate(exp.date)}</td>
                                        <td style={{ padding: '13px 18px' }}>
                                            <span style={{ display: 'inline-flex', alignItems: 'center', gap: 5, padding: '3px 10px', borderRadius: 20, background: colors.bg, fontSize: 12.5, fontWeight: 600, color: colors.text }}>
                                                {cat}
                                            </span>
                                        </td>
                                        <td style={{ padding: '13px 18px', fontSize: 13.5, color: 'var(--text-secondary)' }}>{exp.account_name ?? '—'}</td>
                                        <td style={{ padding: '13px 18px', textAlign: 'right', fontSize: 14.5, fontWeight: 700, color: 'var(--danger)' }}>
                                            −{formatAmount(exp.converted_amount ?? exp.amount, currency)}
                                        </td>
                                    </tr>
                                )
                            })}
                        </tbody>
                    </table>
                )}

                {/* Pagination */}
                {(hasNext || hasPrev) && (
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px 18px', borderTop: '1px solid var(--border-subtle)' }}>
                        <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                            Page {page} · {count.toLocaleString()} results
                        </span>
                        <div style={{ display: 'flex', gap: 6 }}>
                            <button
                                onClick={() => goPage(page - 1)} disabled={!hasPrev}
                                style={{ height: 34, padding: '0 14px', border: '1.5px solid var(--border-input)', borderRadius: 8, fontSize: 13.5, fontWeight: 600, cursor: hasPrev ? 'pointer' : 'not-allowed', background: 'var(--bg-card)', color: hasPrev ? 'var(--text-primary)' : 'var(--text-subtle)', opacity: hasPrev ? 1 : 0.5 }}
                            >
                                ← Prev
                            </button>
                            <button
                                onClick={() => goPage(page + 1)} disabled={!hasNext}
                                style={{ height: 34, padding: '0 14px', border: '1.5px solid var(--border-input)', borderRadius: 8, fontSize: 13.5, fontWeight: 600, cursor: hasNext ? 'pointer' : 'not-allowed', background: 'var(--bg-card)', color: hasNext ? 'var(--text-primary)' : 'var(--text-subtle)', opacity: hasNext ? 1 : 0.5 }}
                            >
                                Next →
                            </button>
                        </div>
                    </div>
                )}
            </div>

            {filterOpen && (
                <FilterSheet filters={filters} onClose={() => setFilterOpen(false)} onApply={handleApplyFilters} />
            )}
            {addOpen && (
                <ExpenseModal onClose={() => setAddOpen(false)} onSaved={handleSaved} />
            )}
            {editingExpense && (
                <ExpenseModal expense={editingExpense} onClose={() => setEditingExpense(null)} onSaved={handleSaved} />
            )}
        </div>
    )
}
