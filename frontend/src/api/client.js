import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL || ''

const client = axios.create({ baseURL: BASE })

client.interceptors.request.use(cfg => {
    const token = localStorage.getItem('access')
    if (token) cfg.headers.Authorization = `Bearer ${token}`
    return cfg
})

client.interceptors.response.use(
    res => res,
    async err => {
        const original = err.config

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
