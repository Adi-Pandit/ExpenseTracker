import { useState, useEffect } from 'react'
import { useOutletContext } from 'react-router-dom'
import {
    BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell,
} from 'recharts'
import { getSummary, getTrends, getCategories, getRecent, getInsights } from '../api/dashboard'
import { useAuth } from '../context/AuthContext'
import { formatAmount, formatDate, greeting, formatLongDate } from '../utils/format'
import { getDonutColor, getCategoryColor } from '../utils/colors'
import ExpenseModal from '../components/modals/ExpenseModal'
import { useToast } from '../context/ToastContext'

export default function Dashboard() {
    const { user } = useAuth()
    const toast = useToast()
    const { refreshUnread } = useOutletContext() ?? {}

    const [summary, setSummary] = useState(null)
    const [trendData, setTrendData] = useState([])
    const [catData, setCatData] = useState([])
    const [recent, setRecent] = useState([])
    const [insights, setInsights] = useState([])
    const [loading, setLoading] = useState(true)
    const [addOpen, setAddOpen] = useState(false)

    async function loadDashboard() {
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
            setInsights(Array.isArray(rawInsights) ? rawInsights.slice(0, 3) : [])
        } catch {
            toast.error('Failed to load dashboard.')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => { loadDashboard() }, []) // eslint-disable-line react-hooks/exhaustive-deps

    const currency = user?.base_currency ?? 'INR'
    const pctChange = summary?.percent_change ?? 0

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
            sub: summary?.current_month?.label ?? '',
            value: formatAmount(summary?.current_month?.total_spend ?? 0, currency),
            trend: pctChange,
            color: 'var(--primary)',
            bg: 'var(--primary-light)',
            icon: (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
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
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
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
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
                    <path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z"/>
                    <line x1="7" y1="7" x2="7.01" y2="7"/>
                </svg>
            ),
        },
        {
            label: 'Total balance',
            sub: `${(summary?.account_balances ?? []).length} accounts`,
            value: formatAmount(
                (summary?.account_balances ?? []).reduce((sum, a) => sum + Number(a.current_balance ?? 0), 0),
                currency,
            ),
            trend: null,
            color: '#D97706',
            bg: '#FEF3C7',
            icon: (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
                    <rect x="2" y="5" width="20" height="14" rx="2"/>
                    <line x1="2" y1="10" x2="22" y2="10"/>
                </svg>
            ),
        },
    ]

    return (
        <div className="page">
            {/* ── Header ── */}
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12, marginBottom: 24 }}>
                <div>
                    <h1 style={{ fontSize: 24, fontWeight: 700, margin: 0, letterSpacing: '-0.02em' }}>
                        {greeting()}, {user?.first_name || user?.username || 'there'}
                    </h1>
                    <p style={{ fontSize: 14, color: 'var(--text-muted)', margin: '4px 0 0' }}>{formatLongDate(new Date())}</p>
                </div>
                <button
                    onClick={() => setAddOpen(true)}
                    style={{
                        height: 42, padding: '0 18px', display: 'flex', alignItems: 'center', gap: 8,
                        background: 'var(--primary)', color: '#fff', border: 'none',
                        borderRadius: 10, fontSize: 14, fontWeight: 600, cursor: 'pointer',
                        boxShadow: 'var(--shadow-btn)',
                    }}
                >
                    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                        <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
                    </svg>
                    Add expense
                </button>
            </div>

            {/* ── Summary cards ── */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: 14, marginBottom: 24 }}>
                {summaryCards.map(card => (
                    <div key={card.label} style={{
                        background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)',
                        border: '1px solid var(--border-card)', padding: '18px 20px',
                        boxShadow: 'var(--shadow-card)',
                    }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
                            <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-muted)' }}>{card.label}</span>
                            <span style={{
                                width: 36, height: 36, borderRadius: 9, background: card.bg,
                                color: card.color, display: 'flex', alignItems: 'center', justifyContent: 'center',
                            }}>{card.icon}</span>
                        </div>
                        <div style={{ fontSize: 22, fontWeight: 700, letterSpacing: '-0.02em', marginBottom: 6 }}>{card.value}</div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                            <span style={{ fontSize: 12.5, color: 'var(--text-subtle)' }}>{card.sub}</span>
                            {card.trend !== null && (
                                <span style={{
                                    fontSize: 11.5, fontWeight: 700, padding: '2px 7px', borderRadius: 20,
                                    background: pctChange > 0 ? 'var(--danger-bg)' : 'var(--success-bg)',
                                    color: pctChange > 0 ? 'var(--danger)' : 'var(--success)',
                                }}>
                                    {pctChange > 0 ? '+' : ''}{pctChange.toFixed(1)}%
                                </span>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {/* ── Charts row ── */}
            <div style={{ display: 'grid', gridTemplateColumns: trendData.length ? '1fr 340px' : '1fr', gap: 14, marginBottom: 24 }}>
                {/* Bar chart */}
                <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-card)', padding: '20px 20px 14px', boxShadow: 'var(--shadow-card)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
                        <div>
                            <div style={{ fontSize: 15, fontWeight: 700 }}>Spending trend</div>
                            <div style={{ fontSize: 12, color: 'var(--text-subtle)', marginTop: 2 }}>Daily expense activity</div>
                        </div>
                    </div>
                    {trendData.length ? (
                        <ResponsiveContainer width="100%" height={200}>
                            <BarChart data={trendData} barSize={10} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                                <XAxis dataKey="label" tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: '#9CA3AF' }} interval="preserveStartEnd" />
                                <YAxis hide />
                                <Tooltip
                                    cursor={{ fill: 'var(--primary-light)', radius: 6 }}
                                    contentStyle={{ borderRadius: 10, border: '1px solid var(--border-card)', fontSize: 13, fontFamily: 'var(--font)', boxShadow: 'var(--shadow-float)' }}
                                    labelStyle={{ fontWeight: 600, color: 'var(--text-primary)' }}
                                    formatter={v => [formatAmount(v, currency), 'Spent']}
                                />
                                <Bar dataKey="amount" fill="var(--primary)" radius={[5, 5, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    ) : (
                        <div style={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-subtle)', fontSize: 14 }}>
                            No trend data yet
                        </div>
                    )}
                </div>

                {/* Donut chart */}
                {catData.length > 0 && (
                    <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-card)', padding: '20px', boxShadow: 'var(--shadow-card)' }}>
                        <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 2 }}>By category</div>
                        <div style={{ fontSize: 12, color: 'var(--text-subtle)', marginBottom: 8 }}>This month</div>
                        <ResponsiveContainer width="100%" height={160}>
                            <PieChart>
                                <Pie data={catData} cx="50%" cy="50%" innerRadius={48} outerRadius={72} dataKey="amount" strokeWidth={2} stroke="var(--bg-card)">
                                    {catData.map((_, i) => <Cell key={i} fill={getDonutColor(i)} />)}
                                </Pie>
                                <Tooltip
                                    contentStyle={{ borderRadius: 10, border: '1px solid var(--border-card)', fontSize: 13, fontFamily: 'var(--font)' }}
                                    formatter={(v, _n, p) => [formatAmount(v, currency), p.payload?.category ?? 'Category']}
                                />
                            </PieChart>
                        </ResponsiveContainer>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 7, marginTop: 8 }}>
                            {catData.slice(0, 4).map((c, i) => (
                                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                    <span style={{ width: 8, height: 8, borderRadius: '50%', background: getDonutColor(i), flexShrink: 0 }} />
                                    <span style={{ fontSize: 12.5, color: 'var(--text-secondary)', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c.category ?? c.name}</span>
                                    <span style={{ fontSize: 12.5, fontWeight: 600, color: 'var(--text-primary)' }}>{Number(c.percentage ?? 0).toFixed(0)}%</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>

            {/* ── Insights + Accounts + Recent ── */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 14 }}>
                {/* Insights */}
                {insights.length > 0 && (
                    <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-card)', padding: '18px 20px', boxShadow: 'var(--shadow-card)' }}>
                        <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 14 }}>Insights</div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                            {insights.map((ins, i) => (
                                <div key={i} style={{ display: 'flex', gap: 10, padding: '12px', background: 'var(--bg-muted)', borderRadius: 10 }}>
                                    <span style={{ fontSize: 18, flexShrink: 0 }}>{ins.icon ?? '💡'}</span>
                                    <div>
                                        <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 2 }}>{ins.title ?? ins.type ?? 'Insight'}</div>
                                        <div style={{ fontSize: 12.5, color: 'var(--text-muted)', lineHeight: 1.4 }}>{ins.message ?? ins.description ?? ''}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Account balances */}
                {(summary?.account_balances ?? []).length > 0 && (
                    <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-card)', padding: '18px 20px', boxShadow: 'var(--shadow-card)' }}>
                        <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 14 }}>Accounts</div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                            {(summary.account_balances ?? []).map(a => (
                                <div key={a.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                        <div style={{
                                            width: 34, height: 34, borderRadius: 9,
                                            background: a.type === 'bank' ? 'var(--primary-light)' : a.type === 'credit_card' ? '#FEF3C7' : '#D1FAE5',
                                            display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                                        }}>
                                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={a.type === 'bank' ? 'var(--primary)' : a.type === 'credit_card' ? '#D97706' : '#059669'} strokeWidth="2" strokeLinecap="round">
                                                <rect x="2" y="5" width="20" height="14" rx="2"/><line x1="2" y1="10" x2="22" y2="10"/>
                                            </svg>
                                        </div>
                                        <div>
                                            <div style={{ fontSize: 13.5, fontWeight: 600 }}>{a.name}</div>
                                            <div style={{ fontSize: 11.5, color: 'var(--text-subtle)', textTransform: 'capitalize' }}>{(a.type ?? '').replace('_', ' ')}</div>
                                        </div>
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                        <div style={{ fontSize: 14, fontWeight: 700 }}>{formatAmount(a.current_balance ?? 0, currency)}</div>
                                        <div style={{ fontSize: 11.5, color: 'var(--text-subtle)' }}>balance</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Recent transactions */}
                {recent.length > 0 && (
                    <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-card)', padding: '18px 20px', boxShadow: 'var(--shadow-card)' }}>
                        <div style={{ fontSize: 15, fontWeight: 700, marginBottom: 14 }}>Recent expenses</div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                            {recent.map(exp => {
                                const cat = exp.category_name ?? 'Other'
                                const colors = getCategoryColor(cat)
                                return (
                                    <div key={exp.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                            <div style={{ width: 34, height: 34, borderRadius: 9, background: colors.bg, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                                                <span style={{ fontSize: 13, color: colors.text, fontWeight: 700 }}>{cat.charAt(0)}</span>
                                            </div>
                                            <div>
                                                <div style={{ fontSize: 13.5, fontWeight: 600, maxWidth: 140, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{exp.notes || cat}</div>
                                                <div style={{ fontSize: 11.5, color: 'var(--text-subtle)' }}>{formatDate(exp.date)}</div>
                                            </div>
                                        </div>
                                        <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--danger)' }}>−{formatAmount(exp.converted_amount ?? exp.amount, currency)}</div>
                                    </div>
                                )
                            })}
                        </div>
                    </div>
                )}
            </div>

            {addOpen && (
                <ExpenseModal
                    onClose={() => setAddOpen(false)}
                    onSaved={() => { setAddOpen(false); loadDashboard(); refreshUnread?.() }}
                />
            )}
        </div>
    )
}
