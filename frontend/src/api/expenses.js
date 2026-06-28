import client from './client'

/* params: { search, category, account, start_date, end_date, min_amount, max_amount, page } */
export const listExpenses = (params = {}) =>
  client.get('/api/expenses/', { params }).then(r => r.data)

export const createExpense = data =>
  client.post('/api/expenses/', data).then(r => r.data)

export const updateExpense = (id, data) =>
  client.patch(`/api/expenses/${id}/`, data).then(r => r.data)

export const deleteExpense = id =>
  client.delete(`/api/expenses/${id}/`)

/* format: 'csv' | 'xlsx' | 'pdf' — returns raw axios response (blob) */
export const exportExpenses = (params = {}) =>
  client.get('/api/export/', { params, responseType: 'blob' })
