import client from './client'

/* { current_month, last_month, percent_change, top_category, top_expenses, account_balances } */
export const getSummary = () =>
  client.get('/dashboard/summary/').then(r => r.data)

/* { period, daily_expenses: [{ date, amount }] } */
export const getTrends = () =>
  client.get('/dashboard/trends/').then(r => r.data)

/* { period, total_spend, breakdown: [{ category, amount, percentage }] } */
export const getCategories = () =>
  client.get('/dashboard/categories/').then(r => r.data)

/* { recent_transactions: [{ id, amount, currency, converted_amount, base_currency, date, notes, category, account }] } */
export const getRecent = () =>
  client.get('/dashboard/recent/').then(r => r.data)

/* array of insight objects */
export const getInsights = () =>
  client.get('/dashboard/insights/').then(r => r.data)
