import client from './client'

/* Returns [{ id, name, owner }] — global categories have owner: null */
export const listCategories = () =>
  client.get('/api/categories/').then(r => r.data)
