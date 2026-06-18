import client from './client'

export const customerApi = {
  list: (params) => client.get('/customers', { params }),
  get: (id) => client.get(`/customers/${id}`),
  create: (data) => client.post('/customers', data),
  delete: (id) => client.delete(`/customers/${id}`),
}
