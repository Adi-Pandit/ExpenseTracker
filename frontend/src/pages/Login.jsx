import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { login } from '../api/auth'
import { useAuth } from '../context/AuthContext'
import { useIsMobile } from '../hooks/useWindowWidth'
import Logo from '../components/Logo'

export default function Login() {
    const navigate = useNavigate()
    const { loginUser } = useAuth()
    const isMobile = useIsMobile()

    const [form, setForm] = useState({ username: '', password: '' })
    const [showPw, setShowPw] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    function set(k, v) { setForm(f => ({ ...f, [k]: v })); setError('') }

    async function handleSubmit(e) {
        e.preventDefault()
        if (!form.username || !form.password) { setError('Please fill in all fields.'); return }
        setLoading(true)
        try {
            const data = await login(form.username, form.password)
            loginUser(data)
            navigate('/dashboard', { replace: true })
        } catch (err) {
            const msg = err.response?.data
            setError(
                typeof msg === 'string' ? msg
                : Array.isArray(msg) ? msg[0]
                : msg?.detail ?? msg?.non_field_errors?.[0] ?? 'Invalid credentials.'
            )
        } finally {
            setLoading(false)
        }
    }

    return (
        <div style={{ minHeight: '100vh', display: 'flex', fontFamily: 'var(--font)' }}>
            {/* ── Brand panel (desktop) ── */}
            {!isMobile && (
                <div style={{
                    width: '44%', flexShrink: 0,
                    background: 'linear-gradient(160deg, #3730A3 0%, #312E81 55%, #1E1B4B 100%)',
                    padding: 56, display: 'flex', flexDirection: 'column',
                    justifyContent: 'space-between', position: 'relative', overflow: 'hidden',
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 12, position: 'relative', zIndex: 2 }}>
                        <Logo size={38} bg="#fff" color="#3730A3" />
                        <span style={{ fontSize: 22, fontWeight: 700, color: '#fff', letterSpacing: '-0.02em' }}>Ledgerly</span>
                    </div>
                    <div style={{ position: 'relative', zIndex: 2 }}>
                        <h1 style={{ fontSize: 40, lineHeight: 1.12, fontWeight: 700, color: '#fff', letterSpacing: '-0.03em', margin: '0 0 18px', textWrap: 'balance' }}>
                            Every rupee, accounted for.
                        </h1>
                        <p style={{ fontSize: 17, lineHeight: 1.55, color: '#C7D2FE', margin: 0, maxWidth: 380 }}>
                            Track expenses, manage accounts and stay ahead of your spending with insights that actually help.
                        </p>
                        <div style={{ display: 'flex', gap: 28, marginTop: 40 }}>
                            {[['₹2.1L', 'tracked this year'], ['4', 'linked accounts'], ['98%', 'budget on track']].map(([v, l]) => (
                                <div key={l}>
                                    <div style={{ fontSize: 28, fontWeight: 700, color: '#fff' }}>{v}</div>
                                    <div style={{ fontSize: 13, color: '#A5B4FC', marginTop: 2 }}>{l}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                    <div style={{ position: 'relative', zIndex: 2, fontSize: 13, color: '#A5B4FC' }}>
                        Bank-grade encryption · Your data stays yours
                    </div>
                    {/* decorative circles */}
                    <div style={{ position: 'absolute', right: -90, bottom: -90, width: 340, height: 340, borderRadius: '50%', background: 'rgba(129,140,248,0.16)' }} />
                    <div style={{ position: 'absolute', right: 60, top: 90, width: 150, height: 150, borderRadius: '50%', background: 'rgba(129,140,248,0.10)' }} />
                </div>
            )}

            {/* ── Form panel ── */}
            <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '40px 24px' }}>
                <div style={{ width: '100%', maxWidth: 380, animation: 'lg-fade .4s ease both' }}>
                    {isMobile && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 28 }}>
                            <Logo size={34} />
                            <span style={{ fontSize: 20, fontWeight: 700, letterSpacing: '-0.02em' }}>Ledgerly</span>
                        </div>
                    )}

                    <h2 style={{ fontSize: 27, fontWeight: 700, letterSpacing: '-0.02em', margin: '0 0 6px' }}>Welcome back</h2>
                    <p style={{ fontSize: 15, color: 'var(--text-muted)', margin: '0 0 26px' }}>Sign in to your account to continue.</p>

                    {error && (
                        <div style={{
                            display: 'flex', alignItems: 'center', gap: 9,
                            background: 'var(--danger-bg)', border: '1px solid var(--danger-border)',
                            color: 'var(--danger-dark)', padding: '11px 13px', borderRadius: 10,
                            fontSize: 13.5, fontWeight: 500, marginBottom: 18,
                        }}>
                            <span style={{ width: 7, height: 7, borderRadius: '50%', background: 'var(--danger)', flexShrink: 0 }} />
                            {error}
                        </div>
                    )}

                    <form onSubmit={handleSubmit}>
                        <label style={lbl}>Username or Email</label>
                        <input
                            value={form.username} onChange={e => set('username', e.target.value)}
                            placeholder="you@example.com" autoComplete="username"
                            style={{ ...inp, marginBottom: 18 }}
                        />

                        <label style={lbl}>Password</label>
                        <div style={{ position: 'relative', marginBottom: 16 }}>
                            <input
                                value={form.password} onChange={e => set('password', e.target.value)}
                                type={showPw ? 'text' : 'password'} placeholder="••••••••"
                                autoComplete="current-password"
                                style={{ ...inp, paddingRight: 46 }}
                            />
                            <button
                                type="button" onClick={() => setShowPw(p => !p)}
                                style={{
                                    position: 'absolute', right: 16, top: 6,
                                    height: 34, width: 34, border: 'none', background: 'transparent',
                                    color: 'var(--text-muted)', cursor: 'pointer',
                                    fontSize: 12, fontWeight: 600, borderRadius: 8,
                                }}
                            >
                                {showPw ? 'Hide' : 'Show'}
                            </button>
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 22 }}>
                            <label style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 13.5, color: 'var(--text-secondary)', cursor: 'pointer' }}>
                                <input type="checkbox" style={{ width: 16, height: 16, accentColor: 'var(--primary)', cursor: 'pointer' }} />
                                Remember me
                            </label>
                            <span style={{ fontSize: 13.5, color: 'var(--primary)', fontWeight: 600, cursor: 'pointer' }}>
                                Forgot password?
                            </span>
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
                            {loading ? 'Signing in…' : 'Log in'}
                        </button>
                    </form>

                    <p style={{ textAlign: 'center', fontSize: 14, color: 'var(--text-muted)', margin: '26px 0 0' }}>
                        Don't have an account?{' '}
                        <Link to="/register" style={{ color: 'var(--primary)', fontWeight: 600 }}>Register</Link>
                    </p>
                </div>
            </div>
        </div>
    )
}

const lbl = { display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 7 }
const inp = {
    width: '100%', height: 46, padding: '0 14px',
    border: '1.5px solid var(--border-input)', borderRadius: 10,
    fontSize: 15, outline: 'none', boxSizing: 'border-box',
    fontFamily: 'var(--font)', color: 'var(--text-primary)',
    background: 'var(--bg-card)',
}
