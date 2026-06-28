import { useState, useEffect } from 'react'

export default function WakeUpBanner() {
    const [visible, setVisible] = useState(false)
    const [seconds, setSeconds] = useState(0)

    useEffect(() => {
        let ticker = null

        function onSlow() {
            setVisible(true)
            setSeconds(0)
            ticker = setInterval(() => setSeconds(s => s + 1), 1000)
        }

        function onReady() {
            setVisible(false)
            clearInterval(ticker)
        }

        window.addEventListener('lg:slow-request', onSlow)
        window.addEventListener('lg:server-ready', onReady)
        return () => {
            window.removeEventListener('lg:slow-request', onSlow)
            window.removeEventListener('lg:server-ready', onReady)
            clearInterval(ticker)
        }
    }, [])

    if (!visible) return null

    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, zIndex: 1000,
            background: 'linear-gradient(90deg, #312E81 0%, #3730A3 100%)',
            color: '#fff',
            padding: '10px 20px',
            display: 'flex', alignItems: 'center', gap: 12,
            boxShadow: '0 2px 12px rgba(55,48,163,0.3)',
            animation: 'lg-fade .3s ease both',
        }}>
            {/* Spinner */}
            <span style={{
                width: 16, height: 16, flexShrink: 0,
                border: '2px solid rgba(255,255,255,0.35)',
                borderTopColor: '#fff',
                borderRadius: '50%',
                animation: 'lg-spin .7s linear infinite',
                display: 'inline-block',
            }} />

            <span style={{ fontSize: 14, fontWeight: 500 }}>
                Server is waking up on Render — this takes about 30–50 seconds on first load.
            </span>

            <span style={{
                marginLeft: 'auto', flexShrink: 0,
                fontSize: 13, fontWeight: 600,
                background: 'rgba(255,255,255,0.15)',
                padding: '3px 10px', borderRadius: 20,
            }}>
                {seconds}s
            </span>
        </div>
    )
}
