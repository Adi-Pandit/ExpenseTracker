import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || ''

const client = axios.create({
    baseURL: BASE,
    timeout: 65000,   // Render free tier can take up to ~50s to cold-start
})

/* Emit DOM events so React components can react without importing context here */
function emit(name) {
    window.dispatchEvent(new CustomEvent(name))
}

let slowTimer = null
let pendingCount = 0

/* ── Attach token + start slow-request timer ── */
client.interceptors.request.use(cfg => {
    const token = localStorage.getItem('access')
    if (token) cfg.headers.Authorization = `Bearer ${token}`

    pendingCount++
    if (!slowTimer) {
        slowTimer = setTimeout(() => emit('lg:slow-request'), 5000)
    }
    return cfg
})

function onResponse() {
    pendingCount = Math.max(0, pendingCount - 1)
    if (pendingCount === 0) {
        clearTimeout(slowTimer)
        slowTimer = null
        emit('lg:server-ready')
    }
}

/* ── Clear timer + handle 401 + retry on network error ── */
client.interceptors.response.use(
    res => { onResponse(); return res },
    async err => {
        onResponse()

        const original = err.config

        /* Network/timeout while server is waking — retry once after 3s */
        if (!err.response && !original._retried) {
            original._retried = true
            await new Promise(r => setTimeout(r, 3000))
            return client(original)
        }

        /* 401 — refresh token once, then kick to login */
        if (err.response?.status === 401 && !original._retry) {
            original._retry = true
            const refresh = localStorage.getItem('refresh')
            if (refresh) {
                try {
                    const { data } = await axios.post(`${BASE}/auth/refresh/`, { refresh })
                    localStorage.setItem('access', data.access)
                    original.headers.Authorization = `Bearer ${data.access}`
                    return client(original)
                } catch {
                    /* refresh failed — fall through */
                }
            }
            localStorage.removeItem('access')
            localStorage.removeItem('refresh')
            window.location.href = '/login'
        }

        return Promise.reject(err)
    }
)

export default client
