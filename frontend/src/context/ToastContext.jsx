import { createContext, useContext, useState, useCallback } from 'react'

const ToastContext = createContext(null)

let _id = 0

export function ToastProvider({ children }) {
    const [toasts, setToasts] = useState([])

    const add = useCallback((message, type = 'success') => {
        const id = ++_id
        setToasts(prev => [...prev, { id, message, type }])
        setTimeout(() => {
            setToasts(prev => prev.filter(t => t.id !== id))
        }, 3500)
    }, [])

    const remove = useCallback(id => {
        setToasts(prev => prev.filter(t => t.id !== id))
    }, [])

    const toast = {
        success: msg => add(msg, 'success'),
        error:   msg => add(msg, 'error'),
    }

    return (
        <ToastContext.Provider value={toast}>
            {children}
            <ToastStack toasts={toasts} onRemove={remove} />
        </ToastContext.Provider>
    )
}

export function useToast() {
    return useContext(ToastContext)
}

/* ── Rendered inside the provider so it's always on top ── */
function ToastStack({ toasts, onRemove }) {
    if (!toasts.length) return null

    return (
        <div style={{
            position: 'fixed',
            top: 20,
            right: 20,
            zIndex: 9999,
            display: 'flex',
            flexDirection: 'column',
            gap: 10,
            pointerEvents: 'none',
        }}>
            {toasts.map(t => (
                <div
                    key={t.id}
                    onClick={() => onRemove(t.id)}
                    style={{
                        pointerEvents: 'all',
                        animation: 'lg-toast-in 0.25s ease both',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 10,
                        padding: '12px 16px',
                        borderRadius: 12,
                        fontSize: 14,
                        fontWeight: 500,
                        fontFamily: 'var(--font)',
                        cursor: 'pointer',
                        boxShadow: '0 8px 24px rgba(16,24,40,0.14)',
                        minWidth: 260,
                        maxWidth: 360,
                        ...(t.type === 'success'
                            ? { background: '#fff', color: '#111827', borderLeft: '4px solid #059669' }
                            : { background: '#fff', color: '#111827', borderLeft: '4px solid #E11D48' }
                        ),
                    }}
                >
                    <span style={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        flexShrink: 0,
                        background: t.type === 'success' ? '#059669' : '#E11D48',
                    }} />
                    {t.message}
                </div>
            ))}
        </div>
    )
}
