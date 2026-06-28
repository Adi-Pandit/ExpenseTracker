import client from './client'

export const login = (username, password) =>
  client.post('/auth/login/', { username, password }).then(r => r.data)

export const register = data =>
  client.post('/auth/register/', data).then(r => r.data)

export const getProfile = () =>
  client.get('/auth/profile/').then(r => r.data)

export const updateProfile = data =>
  client.put('/auth/profile/', data).then(r => r.data)

export const changePassword = data =>
  client.post('/auth/change-password/', data).then(r => r.data)
