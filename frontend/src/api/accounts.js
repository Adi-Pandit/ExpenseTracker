import client from './client'

export const listAccounts = () =>
  client.get('/api/accounts/').then(r => r.data)

export const createAccount = data =>
  client.post('/api/accounts/', data).then(r => r.data)

export const updateAccount = (id, data) =>
  client.patch(`/api/accounts/${id}/`, data).then(r => r.data)

export const deleteAccount = id =>
  client.delete(`/api/accounts/${id}/`)
