/* Category name → { bg, text } badge colors */
const CAT_MAP = {
    'Food & Dining':    { bg: '#FEF3C7', text: '#D97706' },
    'Transport':        { bg: '#DBEAFE', text: '#2563EB' },
    'Housing':          { bg: '#EDE9FE', text: '#7C3AED' },
    'Entertainment':    { bg: '#FCE7F3', text: '#DB2777' },
    'Shopping':         { bg: '#D1FAE5', text: '#059669' },
    'Health & Medical': { bg: '#FEE2E2', text: '#EF4444' },
    'Utilities':        { bg: '#FEF9C3', text: '#CA8A04' },
    'Education':        { bg: '#E0E7FF', text: '#4338CA' },
    'Travel':           { bg: '#CCFBF1', text: '#0D9488' },
    'Personal Care':    { bg: '#FDF4FF', text: '#A855F7' },
    'Subscriptions':    { bg: '#E0E7FF', text: '#6366F1' },
    'Rent':             { bg: '#EDE9FE', text: '#7C3AED' },
    'Groceries':        { bg: '#FEF3C7', text: '#D97706' },
    'Others':           { bg: '#F3F4F6', text: '#6B7280' },
}

/* Fallback palette cycles by first char code */
const FALLBACK = [
    { bg: '#E0E7FF', text: '#4338CA' },
    { bg: '#D1FAE5', text: '#059669' },
    { bg: '#FEF3C7', text: '#D97706' },
    { bg: '#DBEAFE', text: '#2563EB' },
    { bg: '#FCE7F3', text: '#DB2777' },
    { bg: '#FEE2E2', text: '#EF4444' },
    { bg: '#CCFBF1', text: '#0D9488' },
    { bg: '#FDF4FF', text: '#A855F7' },
]

export function getCategoryColor(name) {
    if (!name) return { bg: '#F3F4F6', text: '#6B7280' }
    return CAT_MAP[name] ?? FALLBACK[(name.charCodeAt(0) ?? 0) % FALLBACK.length]
}

/* Ordered donut slice colors */
const DONUT = [
    '#3730A3', '#6366F1', '#8B5CF6', '#EC4899',
    '#EF4444', '#F97316', '#EAB308', '#22C55E',
    '#14B8A6', '#0EA5E9',
]

export function getDonutColor(index) {
    return DONUT[index % DONUT.length]
}

/* "Aarav Sharma" → "AS", "hdfc savings" → "HS" */
export function getInitials(name) {
    if (!name) return '?'
    return name
        .split(/\s+/)
        .map(w => w[0])
        .join('')
        .slice(0, 2)
        .toUpperCase()
}

/* Account type → badge colors */
const ACCOUNT_BADGE = {
    bank:        { bg: '#EEF2FF', text: '#4338CA' },
    cash:        { bg: '#D1FAE5', text: '#059669' },
    credit_card: { bg: '#FEE2E2', text: '#B91C1C' },
}

export function getAccountBadge(type) {
    return ACCOUNT_BADGE[type] ?? { bg: '#F3F4F6', text: '#6B7280' }
}

export function getAccountLabel(type) {
    const labels = { bank: 'Bank', cash: 'Cash', credit_card: 'Credit Card' }
    return labels[type] ?? type
}
