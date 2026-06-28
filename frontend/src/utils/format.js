const SYMBOLS = { INR: '₹', USD: '$', EUR: '€', GBP: '£' }

/* ₹1,23,456.00 — compact for large numbers (1L, 1.2Cr) */
export function formatAmount(amount, currency = 'INR') {
    const sym = SYMBOLS[currency] ?? currency + ' '
    const n = Number(amount ?? 0)

    if (currency === 'INR') {
        if (n >= 10_000_000) return sym + (n / 10_000_000).toFixed(2) + 'Cr'
        if (n >= 100_000)    return sym + (n / 100_000).toFixed(2) + 'L'
        return sym + n.toLocaleString('en-IN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }

    if (n >= 1_000_000) return sym + (n / 1_000_000).toFixed(2) + 'M'
    if (n >= 1_000)     return sym + (n / 1_000).toFixed(1) + 'K'
    return sym + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

/* "19 Jun" */
export function formatDate(dateStr) {
    if (!dateStr) return ''
    const d = new Date(dateStr + 'T00:00:00')
    return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
}

/* "19 Jun 2026" */
export function formatDateFull(dateStr) {
    if (!dateStr) return ''
    const d = new Date(dateStr + 'T00:00:00')
    return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
}

/* "+12.5%" or "-3.2%" */
export function formatPercent(val) {
    const n = Number(val ?? 0)
    return (n >= 0 ? '+' : '') + n.toFixed(1) + '%'
}

/* "Jun 2026" */
export function formatMonthYear(dateStr) {
    if (!dateStr) return ''
    const d = new Date(dateStr + 'T00:00:00')
    return d.toLocaleDateString('en-IN', { month: 'short', year: 'numeric' })
}

/* Today's greeting: "Good morning", "Good afternoon", "Good evening" */
export function greeting() {
    const h = new Date().getHours()
    if (h < 12) return 'Good morning'
    if (h < 17) return 'Good afternoon'
    return 'Good evening'
}

/* "Thursday, 19 June 2026" */
export function formatLongDate(date = new Date()) {
    return date.toLocaleDateString('en-IN', {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric',
    })
}
