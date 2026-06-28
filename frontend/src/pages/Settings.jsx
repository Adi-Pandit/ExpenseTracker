import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { updateProfile, changePassword } from '../api/auth'
import { useAuth } from '../context/AuthContext'
import { useToast } from '../context/ToastContext'
import { getInitials } from '../utils/colors'

const CURRENCIES = ['INR', 'USD', 'EUR', 'GBP', 'AED', 'SGD', 'CAD', 'AUD', 'JPY']

function Section({ title, description, children }) {
    return (
        <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--border-card)', boxShadow: 'var(--shadow-card)', marginBottom: 16 }}>
            <div style={{ padding: '18px 22px', borderBottom: '1px solid var(--border-subtle)' }}>
                <div style={{ fontSize: 15, fontWeight: 700 }}>{title}</div>
                {description && <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 3 }}>{description}</div>}
            </div>
            <div style={{ padding: '22px' }}>
                {children}
            </div>
        </div>
    )
}

export default function Settings() {
    const { user, setUser, logoutUser } = useAuth()
    const toast = useToast()
    const navigate = useNavigate()

    const [profile, setProfile] = useState({
        first_name: user?.first_name ?? '',
        last_name: user?.last_name ?? '',
        username: user?.username ?? '',
        email: user?.email ?? '',
        base_currency: user?.base_currency ?? 'INR',
    })
    const [savingProfile, setSavingProfile] = useState(false)

    const [pw, setPw] = useState({ old_password: '', new_password: '', confirm: '' })
    const [showPw, setShowPw] = useState(false)
    const [savingPw, setSavingPw] = useState(false)
    const [pwError, setPwError] = useState('')

    async function handleSaveProfile(e) {
        e.preventDefault()
        setSavingProfile(true)
        try {
            const updated = await updateProfile({
                first_name: profile.first_name,
                last_name: profile.last_name,
                base_currency: profile.base_currency,
            })
            setUser(u => ({ ...u, ...updated }))
            toast.success('Profile updated.')
        } catch (err) {
            const msg = err.response?.data
            toast.error(typeof msg === 'object' ? Object.values(msg).flat().join(' ') : 'Failed to update profile.')
        } finally {
            setSavingProfile(false)
        }
    }

    async function handleChangePw(e) {
        e.preventDefault()
        setPwError('')
        if (pw.new_password !== pw.confirm) {
            setPwError('New passwords do not match.')
            return
        }
        if (pw.new_password.length < 8) {
            setPwError('New password must be at least 8 characters.')
            return
        }
        setSavingPw(true)
        try {
            await changePassword({ old_password: pw.old_password, new_password: pw.new_password })
            toast.success('Password changed successfully.')
            setPw({ old_password: '', new_password: '', confirm: '' })
        } catch (err) {
            const msg = err.response?.data
            const errStr = typeof msg === 'object' ? Object.values(msg).flat().join(' ') : 'Failed to change password.'
            setPwError(errStr)
        } finally {
            setSavingPw(false)
        }
    }

    function handleLogout() {
        logoutUser()
        navigate('/login', { replace: true })
    }

    const initials = getInitials((`${user?.first_name ?? ''} ${user?.last_name ?? ''}`.trim() || user?.username) ?? '?')

    return (
        <div className="page" style={{ maxWidth: 640 }}>
            <div style={{ marginBottom: 24 }}>
                <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0, letterSpacing: '-0.02em' }}>Settings</h1>
                <p style={{ fontSize: 13, color: 'var(--text-muted)', margin: '4px 0 0' }}>Manage your profile and preferences.</p>
            </div>

            {/* ── Profile ── */}
            <Section title="Profile" description="Update your personal information.">
                {/* Avatar */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 24, padding: '14px', background: 'var(--bg-muted)', borderRadius: 12 }}>
                    <div style={{ width: 52, height: 52, borderRadius: '50%', background: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                        <span style={{ fontSize: 18, fontWeight: 700, color: '#fff' }}>{initials}</span>
                    </div>
                    <div>
                        <div style={{ fontSize: 15, fontWeight: 700 }}>{user?.first_name ? `${user.first_name} ${user.last_name}`.trim() : user?.username}</div>
                        <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>{user?.email}</div>
                        <div style={{ fontSize: 12, color: 'var(--primary)', fontWeight: 600, marginTop: 2 }}>{user?.base_currency}</div>
                    </div>
                </div>

                <form onSubmit={handleSaveProfile}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 14 }}>
                        <div>
                            <label style={lbl}>First name</label>
                            <input value={profile.first_name} onChange={e => setProfile(p => ({ ...p, first_name: e.target.value }))} style={inp} />
                        </div>
                        <div>
                            <label style={lbl}>Last name</label>
                            <input value={profile.last_name} onChange={e => setProfile(p => ({ ...p, last_name: e.target.value }))} style={inp} />
                        </div>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 14 }}>
                        <div>
                            <label style={lbl}>Username</label>
                            <input value={profile.username} disabled style={{ ...inp, opacity: 0.65, cursor: 'not-allowed' }} />
                        </div>
                        <div>
                            <label style={lbl}>Base currency</label>
                            <select value={profile.base_currency} onChange={e => setProfile(p => ({ ...p, base_currency: e.target.value }))} style={{ ...inp, paddingLeft: 10 }}>
                                {CURRENCIES.map(c => <option key={c} value={c}>{c}</option>)}
                            </select>
                        </div>
                    </div>
                    <div style={{ marginBottom: 20 }}>
                        <label style={lbl}>Email</label>
                        <input type="email" value={profile.email} disabled style={{ ...inp, opacity: 0.65, cursor: 'not-allowed' }} />
                        <div style={{ fontSize: 12, color: 'var(--text-subtle)', marginTop: 5 }}>Email cannot be changed from here.</div>
                    </div>
                    <button type="submit" disabled={savingProfile} style={{ ...primaryBtn, opacity: savingProfile ? 0.7 : 1 }}>
                        {savingProfile ? 'Saving…' : 'Save profile'}
                    </button>
                </form>
            </Section>

            {/* ── Change Password ── */}
            <Section title="Change Password" description="Update your account password.">
                {pwError && (
                    <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8, background: 'var(--danger-bg)', border: '1px solid var(--danger-border)', color: 'var(--danger-dark)', padding: '10px 13px', borderRadius: 9, fontSize: 13, fontWeight: 500, marginBottom: 18 }}>
                        <span style={{ width: 7, height: 7, borderRadius: '50%', background: 'var(--danger)', flexShrink: 0, marginTop: 4 }} />
                        {pwError}
                    </div>
                )}
                <form onSubmit={handleChangePw}>
                    <div style={{ marginBottom: 14 }}>
                        <label style={lbl}>Current password</label>
                        <div style={{ position: 'relative' }}>
                            <input
                                type={showPw ? 'text' : 'password'} value={pw.old_password}
                                onChange={e => { setPwError(''); setPw(p => ({ ...p, old_password: e.target.value })) }}
                                placeholder="••••••••" style={{ ...inp, paddingRight: 50 }} required
                            />
                            <button type="button" onClick={() => setShowPw(p => !p)} style={{ position: 'absolute', right: 8, top: 8, height: 30, padding: '0 8px', border: 'none', background: 'transparent', color: 'var(--text-muted)', cursor: 'pointer', fontSize: 11, fontWeight: 600, borderRadius: 6 }}>
                                {showPw ? 'Hide' : 'Show'}
                            </button>
                        </div>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 14, marginBottom: 22 }}>
                        <div>
                            <label style={lbl}>New password</label>
                            <input type={showPw ? 'text' : 'password'} value={pw.new_password} onChange={e => { setPwError(''); setPw(p => ({ ...p, new_password: e.target.value })) }} placeholder="min. 8 chars" style={inp} required />
                        </div>
                        <div>
                            <label style={lbl}>Confirm new password</label>
                            <input type={showPw ? 'text' : 'password'} value={pw.confirm} onChange={e => { setPwError(''); setPw(p => ({ ...p, confirm: e.target.value })) }} placeholder="repeat" style={inp} required />
                        </div>
                    </div>
                    <button type="submit" disabled={savingPw} style={{ ...primaryBtn, opacity: savingPw ? 0.7 : 1 }}>
                        {savingPw ? 'Updating…' : 'Update password'}
                    </button>
                </form>
            </Section>

            {/* ── Danger zone ── */}
            <div style={{ background: 'var(--bg-card)', borderRadius: 'var(--radius-lg)', border: '1px solid var(--danger-border)', boxShadow: 'var(--shadow-card)' }}>
                <div style={{ padding: '18px 22px', borderBottom: '1px solid var(--danger-border)' }}>
                    <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--danger-dark)' }}>Danger zone</div>
                    <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 3 }}>Sign out of your account.</div>
                </div>
                <div style={{ padding: '22px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
                    <div>
                        <div style={{ fontSize: 14, fontWeight: 600 }}>Log out</div>
                        <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 2 }}>You'll need to log in again to access your account.</div>
                    </div>
                    <button
                        onClick={handleLogout}
                        style={{ height: 40, padding: '0 20px', background: 'var(--danger-bg)', color: 'var(--danger)', border: '1.5px solid var(--danger-border)', borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: 'pointer' }}
                    >
                        Log out
                    </button>
                </div>
            </div>
        </div>
    )
}

const lbl = { display: 'block', fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', marginBottom: 7 }
const inp = {
    width: '100%', height: 44, padding: '0 13px',
    border: '1.5px solid var(--border-input)', borderRadius: 10,
    fontSize: 14.5, outline: 'none', boxSizing: 'border-box',
    fontFamily: 'var(--font)', color: 'var(--text-primary)',
    background: 'var(--bg-card)',
}
const primaryBtn = {
    height: 42, padding: '0 22px', background: 'var(--primary)', color: '#fff',
    border: 'none', borderRadius: 9, fontSize: 14, fontWeight: 600, cursor: 'pointer',
    boxShadow: 'var(--shadow-btn)',
}
