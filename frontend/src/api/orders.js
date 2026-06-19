import client from './client'

export const orderApi = {
  list: (params) => client.get('/orders', { params }),
  get: (id) => client.get(`/orders/${id}`),
  create: (data) => client.post('/orders', data),
  delete: (id) => client.delete(`/orders/${id}`),
  updateStatus: (id, status) => client.patch(`/orders/${id}/status`, { status }),
}
