import { useState, useEffect, useCallback } from 'react'
import { customerApi } from '../api/customers'
import { useApp } from '../context/AppContext'
import Modal from '../components/Modal'
import Pagination from '../components/Pagination'
import Loading from '../components/Loading'
import EmptyState from '../components/EmptyState'

const emptyForm = { full_name: '', email: '', phone_number: '' }

export default function Customers() {
  const [customers, setCustomers] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [showAdd, setShowAdd] = useState(false)
  const [form, setForm] = useState(emptyForm)
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const { showToast } = useApp()

  const fetchCustomers = useCallback(() => {
    setLoading(true)
    customerApi.list({ page, page_size: 10, search: search || undefined })
      .then((res) => {
        setCustomers(res.data.items)
        setTotal(res.data.total)
        setTotalPages(res.data.total_pages)
      })
      .catch((err) => showToast(err.message, 'error'))
      .finally(() => setLoading(false))
  }, [page, search, showToast])

  useEffect(() => { fetchCustomers() }, [fetchCustomers])

  const handleSearch = (val) => {
    setSearch(val)
    setPage(1)
  }

  const validate = () => {
    const e = {}
    if (!form.full_name.trim()) e.full_name = 'Full name is required'
    if (!form.email.trim()) e.email = 'Email is required'
    else if (!/\S+@\S+\.\S+/.test(form.email)) e.email = 'Invalid email format'
    if (form.phone_number && !/^\+?[0-9]{10,15}$/.test(form.phone_number)) {
      e.phone_number = 'Phone must be 10-15 digits, optionally starting with +'
    }
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = async () => {
    if (!validate()) return
    setSubmitting(true)
    try {
      await customerApi.create(form)
      showToast('Customer created successfully')
      setShowAdd(false)
      setForm(emptyForm)
      fetchCustomers()
    } catch (err) {
      showToast(err.message, 'error')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Delete customer "${name}"?`)) return
    try {
      await customerApi.delete(id)
      showToast('Customer deleted')
      fetchCustomers()
    } catch (err) {
      showToast(err.message, 'error')
    }
  }

  return (
    <div>
      <div className="toolbar">
        <div className="actions-left">
          <div className="search-wrapper">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8" /><path d="M21 21l-4.35-4.35" />
            </svg>
            <input
              type="text"
              className="form-control"
              placeholder="Search customers..."
              value={search}
              onChange={(e) => handleSearch(e.target.value)}
            />
          </div>
        </div>
        <button className="btn btn-primary" onClick={() => { setForm(emptyForm); setErrors({}); setShowAdd(true) }}>
          + Add Customer
        </button>
      </div>

      {loading ? <Loading /> : customers.length === 0 ? (
        <EmptyState
          title="No customers found"
          message={search ? 'Try a different search term' : 'Add your first customer'}
          action={<button className="btn btn-primary" onClick={() => { setForm(emptyForm); setErrors({}); setShowAdd(true) }}>+ Add Customer</button>}
        />
      ) : (
        <div className="card" style={{ padding: 0 }}>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Email</th>
                  <th>Phone</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {customers.map((c) => (
                  <tr key={c.id}>
                    <td style={{ fontWeight: 500 }}>{c.full_name}</td>
                    <td>{c.email}</td>
                    <td>{c.phone_number || '—'}</td>
                    <td style={{ textAlign: 'right' }}>
                      <button className="btn-icon" onClick={() => handleDelete(c.id, c.full_name)} title="Delete" style={{ color: 'var(--danger)' }}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2" />
                        </svg>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
        </div>
      )}

      {showAdd && (
        <Modal
          title="Add Customer"
          onClose={() => setShowAdd(false)}
          footer={
            <>
              <button className="btn btn-secondary" onClick={() => setShowAdd(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleSubmit} disabled={submitting}>
                {submitting ? 'Saving...' : 'Create Customer'}
              </button>
            </>
          }
        >
          <div className="form-group">
            <label>Full Name</label>
            <input
              className={`form-control ${errors.full_name ? 'error' : ''}`}
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
            />
            {errors.full_name && <p className="error-text">{errors.full_name}</p>}
          </div>
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              className={`form-control ${errors.email ? 'error' : ''}`}
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
            {errors.email && <p className="error-text">{errors.email}</p>}
          </div>
          <div className="form-group">
            <label>Phone Number</label>
            <input
              className={`form-control ${errors.phone_number ? 'error' : ''}`}
              value={form.phone_number}
              onChange={(e) => setForm({ ...form, phone_number: e.target.value })}
            />
            {errors.phone_number && <p className="error-text">{errors.phone_number}</p>}
          </div>
        </Modal>
      )}
    </div>
  )
}
