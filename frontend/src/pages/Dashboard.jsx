import { useState, useEffect, useCallback } from 'react'
import { useOutletContext, useNavigate } from 'react-router-dom'
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell,
} from 'recharts'
import { getSummary, getTrends, getCategories, getRecent, getInsights } from '../api/dashboard'
import { useAuth } from '../context/AuthContext'
import { formatAmount, formatDate, greeting, formatLongDate } from '../utils/format'
import { getDonutColor, getCategoryColor, getInitials } from '../utils/colors'
import ExpenseModal from '../components/modals/ExpenseModal'
import { useToast } from '../context/ToastContext'

const ACCOUNT_COLORS = [
    { bg: 'var(--primary-light)', color: 'var(--primary)' },
    { bg: '#FEF3C7', color: '#D97706' },
    { bg: '#D1FAE5', color: '#059669' },
    { bg: '#FEE2E2', color: '#DC2626' },
    { bg: '#E0E7FF', color: '#4338CA' },
]

export default function Dashboard() {
    const { user } = useAuth()
    const toast = useToast()
    const navigate = useNavigate()
    const { refreshUnread } = useOutletContext() ?? {}

    const [summary, setSummary] = useState(null)
    const [trendData, setTrendData] = useState([])
    const [catData, setCatData] = useState([])
    const [recent, setRecent] = useState([])
    const [insights, setInsights] = useState([])
    const [loading, setLoading] = useState(true)
    const [addOpen, setAddOpen] = useState(false)

    const loadDashboard = useCallback(async () => {
        try {
            const [s, t, c, r, i] = await Promise.all([
                getSummary(),
                getTrends().catch(() => null),
                getCategories().catch(() => null),
                getRecent().catch(() => null),
                getInsights().catch(() => null),
            ])
            setSummary(s)
            const daily = t?.daily_expenses ?? t?.data ?? []
            setTrendData(Array.isArray(daily) ? daily.map(d => ({
                label: formatDate(d.date),
                amount: Number(d.amount ?? 0),
            })) : [])
            const breakdown = c?.breakdown ?? c?.results ?? (Array.isArray(c) ? c : [])
            setCatData(Array.isArray(breakdown) ? breakdown : [])
            const recentList = r?.results ?? (Array.isArray(r) ? r : [])
            setRecent(recentList.slice(0, 5))
            const rawInsights = i?.insights ?? i?.data ?? (Array.isArray(i) ? i : [])
            setInsights(Array.isArray(rawInsights) ? rawInsights.slice(0, 4) : [])
        } catch {
            toast.error('Failed to load dashboard.')
        } finally {
            setLoading(false)
        }
    }, [toast])

    useEffect(() => {
        async function run() { await loadDashboard() }
        run()
    }, [loadDashboard])

    const currency = user?.base_currency ?? 'INR'
    const pctChange = summary?.percent_change ?? 0
    const monthTotal = summary?.current_month?.total_spend ?? 0
    const monthLabel = summary?.current_month?.label ?? new Date().toLocaleString('default', { month: 'long', year: 'numeric' })
    const daysElapsed = new Date().getDate()
    const dailyAvg = daysElapsed > 0 ? monthTotal / daysElapsed : 0

    if (loading) {
        return (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 300 }}>
                <span className="spinner" style={{ width: 28, height: 28 }} />
            </div>
        )
    }

    const summaryCards = [
        {
            label: 'This month',
            sub: monthLabel,
            value: formatAmount(monthTotal, currency),
            trend: pctChange,
            color: 'var(--primary)',
            bg: 'var(--primary-light)',
            icon: (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
                    <path d="M12 2v20M17 5H9.5a3.5 3.5 0 000 7h5a3.5 3.5 0 010 7H6"/>
                </svg>
            ),
        },
        {
            label: 'Last month',
            sub: summary?.last_month?.label ?? '',
            value: formatAmount(summary?.last_month?.total_spend ?? 0, currency),
            trend: null,
            color: '#6B7280',
            bg: '#F3F4F6',
            icon: (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                    <line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>
                    <line x1="3" y1="10" x2="21" y2="10"/>
                </svg>
            ),
        },
        {
            label: 'Top category',
            sub: summary?.top_category?.name ? formatAmount(summary.top_category.amount ?? 0, currency) : 'No data',
            value: summary?.top_category?.name ?? '—',
            trend: null,
            color: '#059669',
            bg: '#D1FAE5',
            icon: (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
                    <path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/>
                    <line x1="7" y1="7" x2="7.01" y2="7"/>
                </svg>
            ),
        },
        {
            label: 'Total balance',
            sub: `${(summary?.account_balances ?? []).length} account${(summary?.account_balances ?? []).length !== 1 ? 's' : ''}`,
            value: formatAmount(
                (summary?.account_balances ?? []).reduce((sum, a) => sum + Number(a.current_balance ?? 0), 0),
                currency,
            ),
            trend: null,
            color: '#D97706',
            bg: '#FEF3C7',
            icon: (
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
                    <rect x="2" y="5" width="20" height="14" rx="2"/>
                    <line x1="2" y1="10" x2="22" y2="10"/>
                </svg>
            ),
        },
    ]

    const accounts = summary?.account_balances ?? []

    return (
        <div className="page">
            {/* ── Header ── */}
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, marginBottom: 24 }}>
                <div>
                    <h1 style={{ fontSize: 24, fontWeight: 700, margin: 0, letterSpacing: '-0.02em' }}>
                        {greeting()}, {user?.first_name || user?.username || 'there'} 👋
                    </h1>
                    <p style={{ fontSize: 14, color: 'var(--text-muted)', margin: '4px 0 0' }}>{formatLongDate(new Date())}</p>
                </div>
                <button
                    onClick={() => setAddOpen(true)}
                    style={{
                        height: 42, padding: '0 18px', display: 'flex', alignItems: 'center', gap: 8,
                        background: 'var(--primary)', color: '#fff', border: 'none',
                        borderRadius: 10, fontSize: 14, fontWeight: 600, cursor: 'pointer',
                        boxShadow: '0 1px 3px rgba(55,48,163,.3)',
                    }}
                >
                    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                        <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                    </svg>
                    Add expense
                </button>
            </div>

            {/* ── Summary cards ── */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(210px, 1fr))', gap: 14, marginBottom: 24 }}>
                {summaryCards.map(card => (
                    <div key={card.label} style={{
                        background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)',
                        border: '1px solid var(--border-card)', padding: '18px 18px 16px',
                        boxShadow: 'var(--shadow-card)',
                    }}>
                        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 12 }}>
                            <span style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--text-muted)', letterSpacing: '0.01em' }}>{card.label}</span>
                            <span style={{
                                width: 30, height: 30, borderRadius: 9, background: card.bg,
                                color: card.color, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                            }}>{card.icon}</span>
                        </div>
                        <div style={{ fontSize: 22, fontWeight: 700, letterSpacing: '-0.02em', marginBottom: 6, lineHeight: 1.2 }}>{card.value}</div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                            <span style={{ fontSize: 12, color: 'var(--text-subtle)' }}>{card.sub}</span>
                            {card.trend !== null && (
                                <span style={{
                                    fontSize: 11, fontWeight: 700, padding: '2px 7px', borderRadius: 20,
                                    background: pctChange > 0 ? 'var(--danger-bg)' : 'var(--success-bg)',
                                    color: pctChange > 0 ? 'var(--danger)' : 'var(--success)',
                                }}>
                                    {pctChange > 0 ? '↑' : '↓'} {Math.abs(pctChange).toFixed(1)}%
                                </span>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {/* ── Charts row ── */}
            <div style={{ display: 'grid', gridTemplateColumns: trendData.length ? '1fr 320px' : '1fr', gap: 14, marginBottom: 24 }}>
                {/* Bar chart */}
                <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-card)', padding: '20px 20px 14px', boxShadow: 'var(--shadow-card)' }}>
                    <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 16 }}>
                        <div>
                            <div style={{ fontSize: 15, fontWeight: 700 }}>Spending this month</div>
                            <div style={{ fontSize: 12, color: 'var(--text-subtle)', marginTop: 2 }}>Daily expenses · {monthLabel}</div>
                        </div>
                        {monthTotal > 0 && (
                            <div style={{ textAlign: 'right', flexShrink: 0 }}>
                                <div style={{ fontSize: 18, fontWeight: 700, letterSpacing: '-0.02em' }}>{formatAmount(monthTotal, currency)}</div>
                                <div style={{ fontSize: 11.5, color: 'var(--text-subtle)', marginTop: 1 }}>avg {formatAmount(dailyAvg, currency)}/day</div>
                            </div>
                        )}
                    </div>
                    {trendData.length ? (
                        <ResponsiveContainer width="100%" height={190}>
                            <BarChart data={trendData} barSize={8} barCategoryGap="35%" margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                                <XAxis
                                    dataKey="label"
                                    tickLine={false}
                                    axisLine={false}
                                    tick={{ fontSize: 11, fill: '#9CA3AF' }}
                                    interval={trendData.length > 8 ? Math.floor(trendData.length / 7) : 0}
                                />
                                <YAxis hide />
                                <Tooltip
                                    cursor={{ fill: 'var(--primary-light)', radius: 6 }}
                                    contentStyle={{ borderRadius: 10, border: '1px solid var(--border-card)', fontSize: 13, fontFamily: 'var(--font)', boxShadow: 'var(--shadow-float)' }}
                                    labelStyle={{ fontWeight: 600, color: 'var(--text-primary)' }}
                                    formatter={v => [formatAmount(v, currency), 'Spent']}
                                />
                                <Bar dataKey="amount" fill="var(--primary)" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    ) : (
                        <div style={{ height: 190, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-subtle)', fontSize: 14 }}>
                            No spending data yet
                        </div>
                    )}
                </div>

                {/* Donut chart */}
                {catData.length > 0 && (
                    <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-card)', padding: '20px', boxShadow: 'var(--shadow-card)' }}>
                        <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 2 }}>By category</div>
                        <div style={{ fontSize: 12, color: 'var(--text-subtle)', marginBottom: 10 }}>This month</div>
                        <ResponsiveContainer width="100%" height={150}>
                            <PieChart>
                                <Pie data={catData} cx="50%" cy="50%" innerRadius={44} outerRadius={66} dataKey="amount" strokeWidth={2} stroke="var(--bg-card)">
                                    {catData.map((_, i) => <Cell key={i} fill={getDonutColor(i)} />)}
                                </Pie>
                                <Tooltip
                                    contentStyle={{ borderRadius: 10, border: '1px solid var(--border-card)', fontSize: 13, fontFamily: 'var(--font)' }}
                                    formatter={(v, _n, p) => [formatAmount(v, currency), p.payload?.category ?? 'Category']}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 7, marginTop: 6 }}>
                            {catData.slice(0, 4).map((c, i) => (
                                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                    <span style={{ width: 8, height: 8, borderRadius: '50%', background: getDonutColor(i), flexShrink: 0 }} />
                                    <span style={{ fontSize: 12.5, color: 'var(--text-secondary)', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c.category ?? c.name}</span>
                                    <span style={{ fontSize: 12, color: 'var(--text-subtle)', marginRight: 4 }}>{Number(c.percentage ?? 0).toFixed(0)}%</span>
                                    <span style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--text-primary)' }}>{formatAmount(c.amount ?? 0, currency)}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* ── Insights row (horizontal scroll) ── */}
            {insights.length > 0 && (
                <div style={{ marginBottom: 24 }}>
                    <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 12 }}>Insights</div>
                    <div style={{ display: 'flex', gap: 12, overflowX: 'auto', paddingBottom: 2, scrollbarWidth: 'none' }}>
                        {insights.map((ins, i) => {
                            const rawType = (ins.type ?? ins.title ?? '').toLowerCase()
                            let tag, tagColor, tagBg, iconEl
                            if (rawType.includes('warn') || rawType.includes('alert')) {
                                tag = 'WARNING'; tagColor = '#D97706'; tagBg = '#FEF3C7'
                                iconEl = (
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#D97706" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                        <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
                                        <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                                    </svg>
                                )
                            } else if (rawType.includes('positive') || rawType.includes('success') || rawType.includes('good')) {
                                tag = 'POSITIVE'; tagColor = '#059669'; tagBg = '#D1FAE5'
                                iconEl = (
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#059669" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                        <circle cx="12" cy="12" r="10"/>
                                        <path d="M9 12l2 2 4-4"/>
                                    </svg>
                                )
                            } else {
                                tag = 'INFO'; tagColor = '#2563EB'; tagBg = '#DBEAFE'
                                iconEl = (
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#2563EB" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                        <circle cx="12" cy="12" r="10"/>
                                        <line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
                                    </svg>
                                )
                            }
                            return (
                                <div key={i} style={{
                                    background: 'var(--bg-card)', border: '1px solid var(--border-card)',
                                    borderRadius: 'var(--radius-lg)', padding: '16px 18px', boxShadow: 'var(--shadow-card)',
                                    minWidth: 260, maxWidth: 320, flex: 'none',
                                }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                                        {iconEl}
                                        <span style={{
                                            fontSize: 10.5, fontWeight: 700, letterSpacing: '0.07em',
                                            textTransform: 'uppercase', color: tagColor,
                                            background: tagBg, padding: '2px 8px', borderRadius: 20,
                                        }}>
                                            {tag}
                                        </span>
                                    </div>
                                    <div style={{ fontSize: 13, color: 'var(--text-secondary)', lineHeight: 1.55 }}>
                                        {ins.message ?? ins.description ?? ''}
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                </div>
            )}

            {/* ── Accounts + Recent transactions ── */}
            {(accounts.length > 0 || recent.length > 0) && (
                <div style={{ display: 'grid', gridTemplateColumns: accounts.length && recent.length ? '1fr 1fr' : '1fr', gap: 14 }}>
                    {/* Account balances */}
                    {accounts.length > 0 && (
                        <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-card)', padding: '18px 20px', boxShadow: 'var(--shadow-card)' }}>
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
                                <div style={{ fontSize: 15, fontWeight: 700 }}>Account balances</div>
                                <button
                                    onClick={() => navigate('/accounts')}
                                    style={{ fontSize: 12.5, color: 'var(--primary)', fontWeight: 600, background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
                                >
                                    View all →
                                </button>
                            </div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                                {accounts.map((a, idx) => {
                                    const initials = getInitials(a.name)
                                    const palette = ACCOUNT_COLORS[idx % ACCOUNT_COLORS.length]
                                    return (
                                        <div key={a.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                                <div style={{
                                                    width: 38, height: 38, borderRadius: 10,
                                                    background: palette.bg, color: palette.color,
                                                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                    fontSize: 13, fontWeight: 700, flexShrink: 0,
                                                }}>
                                                    {initials}
                                                </div>
                                                <div>
                                                    <div style={{ fontSize: 13.5, fontWeight: 600 }}>{a.name}</div>
                                                    <span style={{
                                                        fontSize: 10.5, fontWeight: 600, textTransform: 'capitalize',
                                                        color: palette.color, background: palette.bg,
                                                        padding: '1px 7px', borderRadius: 20,
                                                    }}>
                                                        {(a.type ?? '').replace('_', ' ')}
                                                    </span>
                                                </div>
                                            </div>
                                            <div style={{ textAlign: 'right' }}>
                                                <div style={{ fontSize: 14, fontWeight: 700 }}>{formatAmount(a.current_balance ?? 0, currency)}</div>
                                                {a.opening_balance != null && (
                                                    <div style={{ fontSize: 11.5, color: 'var(--text-subtle)' }}>
                                                        from {formatAmount(a.opening_balance, currency)}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    )
                                })}
                            </div>
                        </div>
                    )}

                    {/* Recent transactions */}
                    {recent.length > 0 && (
                        <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-card)', padding: '18px 20px', boxShadow: 'var(--shadow-card)' }}>
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
                                <div style={{ fontSize: 15, fontWeight: 700 }}>Recent transactions</div>
                                <button
                                    onClick={() => navigate('/expenses')}
                                    style={{ fontSize: 12.5, color: 'var(--primary)', fontWeight: 600, background: 'none', border: 'none', cursor: 'pointer', padding: 0 }}
                                >
                                    View all →
                                </button>
                            </div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                                {recent.map(exp => {
                                    const cat = exp.category_name ?? 'Other'
                                    const colors = getCategoryColor(cat)
                                    const account = exp.account_name ?? exp.account?.name ?? null
                                    const subLine = account ? `${cat} · ${account}` : cat
                                    return (
                                        <div key={exp.id} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                            <div style={{
                                                width: 36, height: 36, borderRadius: '50%',
                                                background: colors.bg, display: 'flex', alignItems: 'center',
                                                justifyContent: 'center', flexShrink: 0,
                                            }}>
                                                <span style={{ fontSize: 13, color: colors.text, fontWeight: 700 }}>{cat.charAt(0)}</span>
                                            </div>
                                            <div style={{ flex: 1, minWidth: 0 }}>
                                                <div style={{ fontSize: 13.5, fontWeight: 600, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                                    {exp.notes || cat}
                                                </div>
                                                <div style={{ fontSize: 11.5, color: 'var(--text-subtle)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                                    {subLine}
                                                </div>
                                            </div>
                                            <div style={{ textAlign: 'right', flexShrink: 0 }}>
                                                <div style={{ fontSize: 13.5, fontWeight: 700, color: 'var(--text-primary)' }}>
                                                    {formatAmount(exp.converted_amount ?? exp.amount, currency)}
                                                </div>
                                                <div style={{ fontSize: 11.5, color: 'var(--text-subtle)' }}>
                                                    {formatDate(exp.date)}
                                                </div>
                                            </div>
                                        </div>
                                    )
                                })}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {addOpen && (
                <ExpenseModal
                    onClose={() => setAddOpen(false)}
                    onSaved={() => { setAddOpen(false); loadDashboard(); refreshUnread?.() }}
                />
            )}
        </div>
    )
}
