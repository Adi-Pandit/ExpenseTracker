import client from './client'

/* params: { is_active, frequency, category, account, search } */
export const listRecurring = (params = {}) =>
  client.get('/api/recurring/', { params }).then(r => r.data)

export const createRecurring = data =>
  client.post('/api/recurring/', data).then(r => r.data)

export const updateRecurring = (id, data) =>
  client.patch(`/api/recurring/${id}/`, data).then(r => r.data)

export const deleteRecurring = id =>
  client.delete(`/api/recurring/${id}/`)
