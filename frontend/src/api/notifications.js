import client from './client'

/* params: { is_read } — pass is_read=false to get only unread */
export const listNotifications = (params = {}) =>
  client.get('/api/notifications/', { params }).then(r => r.data)

export const markRead = id =>
  client.put(`/api/notifications/${id}/read/`).then(r => r.data)
