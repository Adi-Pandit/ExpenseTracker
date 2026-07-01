import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { register } from '../api/auth'
import { useAuth } from '../context/AuthContext'
import { useIsMobile } from '../hooks/useWindowWidth'
import Logo from '../components/Logo'

const CURRENCIES = ['INR', 'USD', 'EUR', 'GBP', 'AED', 'SGD', 'CAD', 'AUD']

export default function Register() {
    const navigate = useNavigate()
    const { loginUser } = useAuth()
    const isMobile = useIsMobile()

    const [form, setForm] = useState({
        first_name: '', last_name: '',
        username: '', email: '',
        password: '', confirm_password: '',
        base_currency: 'INR',
    })
    const [showPw, setShowPw] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    function set(k, v) { setForm(f => ({ ...f, [k]: v })); setError('') }

    async function handleSubmit(e) {
        e.preventDefault()
        if (form.password !== form.confirm_password) {
            setError('Passwords do not match.')
            return
        }
        setLoading(true)
        try {
            const data = await register({
                first_name: form.first_name,
                last_name: form.last_name,
                username: form.username,
                email: form.email,
                password: form.password,
                password_confirm: form.confirm_password,
                base_currency: form.base_currency,
            })
            loginUser(data)
            navigate('/dashboard', { replace: true })
        } catch (err) {
            const msg = err.response?.data
            if (typeof msg === 'object' && msg !== null) {
                const LABELS = {
                    username: 'Username',
                    email: 'Email address',
                    password: 'Password',
                    password_confirm: 'Confirm password',
                    first_name: 'First name',
                    last_name: 'Last name',
                    base_currency: 'Currency',
                }
                const [field, messages] = Object.entries(msg)[0] ?? []
                if (field) {
                    const text = [].concat(messages).join(' ')
                    const label = LABELS[field]
                    setError(label ? `${label}: ${text}` : text)
                } else {
                    setError('Registration failed.')
                }
            } else {
                setError(typeof msg === 'string' ? msg : 'Registration failed.')
            }
        } finally {
            setLoading(false)
        }
    }

    return (
        <div style={{ minHeight: '100vh', display: 'flex', fontFamily: 'var(--font)' }}>
            {/* ── Brand panel ── */}
            {!isMobile && (
                <div style={{
                    width: '40%', flexShrink: 0,
                    background: 'linear-gradient(160deg, #3730A3 0%, #312E81 55%, #1E1B4B 100%)',
                    padding: 56, display: 'flex', flexDirection: 'column',
                    justifyContent: 'space-between', position: 'relative', overflow: 'hidden',
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12, position: 'relative', zIndex: 2 }}>
                        <Logo size={38} bg="#fff" color="#3730A3" />
                        <span style={{ fontSize: 22, fontWeight: 700, color: '#fff', letterSpacing: '-0.02em' }}>Ledgerly</span>
                    </div>
                    <div style={{ position: 'relative', zIndex: 2 }}>
                        <h1 style={{ fontSize: 38, lineHeight: 1.12, fontWeight: 700, color: '#fff', letterSpacing: '-0.03em', margin: '0 0 16px' }}>
                            Your finances, finally clear.
                        </h1>
                        <p style={{ fontSize: 16, lineHeight: 1.6, color: '#C7D2FE', margin: 0 }}>
                            Join thousands of people who track every expense, spot trends, and stay on top of their money — all in one clean place.
                        </p>
                        <div style={{ marginTop: 36, display: 'flex', flexDirection: 'column', gap: 16 }}>
                            {[
                                ['Multi-currency', 'Track INR, USD, EUR and more in one place'],
                                ['Smart insights', 'Understand where your money really goes'],
                                ['Recurring support', 'Never miss a subscription or bill'],
                            ].map(([title, desc]) => (
                                <div key={title} style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
                                    <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#A5B4FC', marginTop: 6, flexShrink: 0 }} />
                                    <div>
                                        <div style={{ fontWeight: 600, color: '#fff', fontSize: 14 }}>{title}</div>
                                        <div style={{ color: '#C7D2FE', fontSize: 13, marginTop: 2 }}>{desc}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                    <div style={{ position: 'relative', zIndex: 2, fontSize: 13, color: '#A5B4FC' }}>
                        Free forever · No credit card required
                    </div>
                    <div style={{ position: 'absolute', right: -80, bottom: -80, width: 300, height: 300, borderRadius: '50%', background: 'rgba(129,140,248,0.15)' }} />
                    <div style={{ position: 'absolute', left: -60, top: '40%', width: 200, height: 200, borderRadius: '50%', background: 'rgba(129,140,248,0.08)' }} />
                </div>
            )}

            {/* ── Form panel ── */}
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '40px 24px', overflowY: 'auto' }}>
                <div style={{ width: '100%', maxWidth: 420, animation: 'lg-fade .4s ease both' }}>
                    {isMobile && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 28 }}>
                            <Logo size={34} />
                            <span style={{ fontSize: 20, fontWeight: 700, letterSpacing: '-0.02em' }}>Ledgerly</span>
                        </div>
                    )}

                    <h2 style={{ fontSize: 26, fontWeight: 700, letterSpacing: '-0.02em', margin: '0 0 6px' }}>Create your account</h2>
                    <p style={{ fontSize: 14.5, color: 'var(--text-muted)', margin: '0 0 24px' }}>Get started — it only takes a minute.</p>

                    {error && (
                        <div style={{
                            display: 'flex', alignItems: 'flex-start', gap: 9,
                            background: 'var(--danger-bg)', border: '1px solid var(--danger-border)',
                            color: 'var(--danger-dark)', padding: '11px 13px', borderRadius: 10,
                            fontSize: 13.5, fontWeight: 500, marginBottom: 18,
                        }}>
                            <span style={{ width: 7, height: 7, borderRadius: '50%', background: 'var(--danger)', flexShrink: 0, marginTop: 3 }} />
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit}>
                        {/* First + Last name */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
                            <div>
                                <label style={lbl}>First name</label>
                                <input value={form.first_name} onChange={e => set('first_name', e.target.value)} placeholder="Aarav" style={inp} required />
                            </div>
                            <div>
                                <label style={lbl}>Last name</label>
                                <input value={form.last_name} onChange={e => set('last_name', e.target.value)} placeholder="Sharma" style={inp} />
                            </div>
                        </div>

                        {/* Username + Currency */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 16 }}>
                            <div>
                                <label style={lbl}>Username</label>
                                <input value={form.username} onChange={e => set('username', e.target.value)} placeholder="aarav99" autoComplete="username" style={inp} required />
                            </div>
                            <div>
                                <label style={lbl}>Base currency</label>
                                <select value={form.base_currency} onChange={e => set('base_currency', e.target.value)} style={{ ...inp, paddingLeft: 10 }}>
                                    {CURRENCIES.map(c => <option key={c} value={c}>{c}</option>)}
                                </select>
                            </div>
                        </div>

                        {/* Email */}
                        <div style={{ marginBottom: 16 }}>
                            <label style={lbl}>Email address</label>
                            <input type="email" value={form.email} onChange={e => set('email', e.target.value)} placeholder="aarav@example.com" autoComplete="email" style={inp} required />
                        </div>

                        {/* Password + Confirm */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 22 }}>
                            <div>
                                <label style={lbl}>Password</label>
                                <div style={{ position: 'relative' }}>
                                    <input
                                        value={form.password} onChange={e => set('password', e.target.value)}
                                        type={showPw ? 'text' : 'password'} placeholder="min. 8 chars"
                                        autoComplete="new-password" style={{ ...inp, paddingRight: 46 }} required
                                    />
                                    <button
                                        type="button" onClick={() => setShowPw(p => !p)}
                                        style={{ position: 'absolute', right: 6, top: 6, height: 34, width: 34, border: 'none', background: 'transparent', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 11, fontWeight: 600, borderRadius: 7 }}
                                    >
                                        {showPw ? 'Hide' : 'Show'}
                                    </button>
                                </div>
                            </div>
                            <div>
                                <label style={lbl}>Confirm</label>
                                <input
                                    value={form.confirm_password} onChange={e => set('confirm_password', e.target.value)}
                                    type={showPw ? 'text' : 'password'} placeholder="repeat"
                                    autoComplete="new-password" style={inp} required
                                />
                            </div>
                        </div>

                        <button
                            type="submit" disabled={loading}
                            style={{
                                width: '100%', height: 47,
                                background: loading ? 'var(--primary-hover)' : 'var(--primary)',
                                color: '#fff', border: 'none', borderRadius: 9,
                                fontSize: 15, fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer',
                                boxShadow: 'var(--shadow-btn)',
                                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                            }}
                        >
                            {loading ? <span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} /> : null}
                            {loading ? 'Creating account…' : 'Create account'}
                        </button>
                    </form>

                    <p style={{ textAlign: 'center', fontSize: 14, color: 'var(--text-muted)', margin: '22px 0 0' }}>
                        Already have an account?{' '}
                        <Link to="/login" style={{ color: 'var(--primary)', fontWeight: 600 }}>Log in</Link>
                    </p>
                </div>
            </div>
        </div>
    )
}

const lbl = { display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 6 }
const inp = {
    width: '100%', height: 44, padding: '0 13px',
    border: '1.5px solid var(--border-input)', borderRadius: 10,
    fontSize: 14.5, outline: 'none', boxSizing: 'border-box',
    fontFamily: 'var(--font)', color: 'var(--text-primary)',
    background: 'var(--bg-card)',
}
