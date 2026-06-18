import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { orderApi } from '../api/orders'
import { productApi } from '../api/products'
import { customerApi } from '../api/customers'
import { useApp } from '../context/AppContext'
import Modal from '../components/Modal'
import Pagination from '../components/Pagination'
import Loading from '../components/Loading'
import EmptyState from '../components/EmptyState'

export default function Orders() {
  const [orders, setOrders] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [customers, setCustomers] = useState([])
  const [products, setProducts] = useState([])
  const [selectedCustomer, setSelectedCustomer] = useState('')
  const [orderItems, setOrderItems] = useState([{ product_id: '', quantity: '' }])
  const [submitting, setSubmitting] = useState(false)
  const [errors, setErrors] = useState({})
  const { showToast } = useApp()

  const fetchOrders = useCallback(() => {
    setLoading(true)
    orderApi.list({ page, page_size: 10 })
      .then((res) => {
        setOrders(res.data.items)
        setTotal(res.data.total)
        setTotalPages(res.data.total_pages)
      })
      .catch((err) => showToast(err.message, 'error'))
      .finally(() => setLoading(false))
  }, [page, showToast])

  useEffect(() => { fetchOrders() }, [fetchOrders])

  const openCreate = async () => {
    try {
      const [custRes, prodRes] = await Promise.all([
        customerApi.list({ page_size: 200 }),
        productApi.list({ page_size: 200 }),
      ])
      setCustomers(custRes.data.items)
      setProducts(prodRes.data.items)
      setSelectedCustomer('')
      setOrderItems([{ product_id: '', quantity: '' }])
      setErrors({})
      setShowCreate(true)
    } catch (err) {
      showToast(err.message, 'error')
    }
  }

  const addItem = () => setOrderItems([...orderItems, { product_id: '', quantity: '' }])

  const removeItem = (idx) => {
    if (orderItems.length === 1) return
    setOrderItems(orderItems.filter((_, i) => i !== idx))
  }

  const updateItem = (idx, field, value) => {
    const items = [...orderItems]
    items[idx][field] = value
    setOrderItems(items)
  }

  const getProductName = (id) => {
    const p = products.find((x) => x.id === Number(id))
    return p ? p.product_name : 'Unknown'
  }

  const getUnitPrice = (id) => {
    const p = products.find((x) => x.id === Number(id))
    return p ? Number(p.price) : 0
  }

  const getStock = (id) => {
    const p = products.find((x) => x.id === Number(id))
    return p ? p.quantity_in_stock : 0
  }

  const previewTotal = orderItems.reduce((sum, item) => {
    if (!item.product_id || !item.quantity) return sum
    return sum + getUnitPrice(item.product_id) * Number(item.quantity)
  }, 0)

  const validate = () => {
    const e = {}
    if (!selectedCustomer) e.customer = 'Please select a customer'
    const validItems = orderItems.filter((i) => i.product_id && i.quantity)
    if (validItems.length === 0) e.items = 'Add at least one product'
    orderItems.forEach((item, idx) => {
      if (item.product_id) {
        const qty = Number(item.quantity)
        if (!qty || qty < 1) e[`item_${idx}`] = 'Quantity must be at least 1'
        else if (qty > getStock(item.product_id)) e[`item_${idx}`] = `Only ${getStock(item.product_id)} in stock`
      }
    })
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = async () => {
    if (!validate()) return
    setSubmitting(true)
    try {
      const items = orderItems
        .filter((i) => i.product_id && i.quantity)
        .map((i) => ({ product_id: Number(i.product_id), quantity: Number(i.quantity) }))
      await orderApi.create({ customer_id: Number(selectedCustomer), items })
      showToast('Order created successfully')
      setShowCreate(false)
      fetchOrders()
    } catch (err) {
      showToast(err.message, 'error')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id) => {
    if (!window.confirm(`Delete order #${id}?`)) return
    try {
      await orderApi.delete(id)
      showToast('Order deleted')
      fetchOrders()
    } catch (err) {
      showToast(err.message, 'error')
    }
  }

  const formatDate = (d) => new Date(d).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })

  return (
    <div>
      <div className="toolbar">
        <div />
        <button className="btn btn-primary" onClick={openCreate}>+ New Order</button>
      </div>

      {loading ? <Loading /> : orders.length === 0 ? (
        <EmptyState
          title="No orders found"
          message="Create your first order to get started"
          action={<button className="btn btn-primary" onClick={openCreate}>+ New Order</button>}
        />
      ) : (
        <div className="card" style={{ padding: 0 }}>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Order #</th>
                  <th>Customer</th>
                  <th>Amount</th>
                  <th>Status</th>
                  <th>Date</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((o) => (
                  <tr key={o.id}>
                    <td style={{ fontWeight: 500 }}>
                      <Link to={`/orders/${o.id}`} style={{ color: 'var(--primary)' }}>#{o.id}</Link>
                    </td>
                    <td>{o.customer_name}</td>
                    <td>${Number(o.total_amount).toFixed(2)}</td>
                    <td><span className="badge badge-success">{o.status}</span></td>
                    <td>{formatDate(o.created_at)}</td>
                    <td style={{ textAlign: 'right' }}>
                      <Link to={`/orders/${o.id}`} className="btn btn-sm btn-secondary" style={{ marginRight: 6 }}>View</Link>
                      <button className="btn btn-sm btn-danger" onClick={() => handleDelete(o.id)}>Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <Pagination page={page} totalPages={totalPages} onPageChange={setPage} />
        </div>
      )}

      {showCreate && (
        <Modal
          title="Create Order"
          onClose={() => setShowCreate(false)}
          footer={
            <>
              <button className="btn btn-secondary" onClick={() => setShowCreate(false)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleSubmit} disabled={submitting}>
                {submitting ? 'Creating...' : 'Create Order'}
              </button>
            </>
          }
        >
          <div className="form-group">
            <label>Customer</label>
            <select
              className={`form-control ${errors.customer ? 'error' : ''}`}
              value={selectedCustomer}
              onChange={(e) => setSelectedCustomer(e.target.value)}
            >
              <option value="">Select a customer...</option>
              {customers.map((c) => (
                <option key={c.id} value={c.id}>{c.full_name} ({c.email})</option>
              ))}
            </select>
            {errors.customer && <p className="error-text">{errors.customer}</p>}
          </div>

          <div style={{ marginTop: 20 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <label style={{ fontSize: 13, fontWeight: 600, color: 'var(--gray-700)' }}>Products</label>
              <button className="btn btn-sm btn-secondary" onClick={addItem}>+ Add Item</button>
            </div>

            {orderItems.map((item, idx) => (
              <div key={idx} style={{ display: 'flex', gap: 10, alignItems: 'flex-start', marginBottom: 10 }}>
                <div style={{ flex: 1 }}>
                  <select
                    className="form-control"
                    value={item.product_id}
                    onChange={(e) => updateItem(idx, 'product_id', e.target.value)}
                  >
                    <option value="">Select product...</option>
                    {products.map((p) => (
                      <option key={p.id} value={p.id} disabled={p.quantity_in_stock === 0}>
                        {p.product_name} (${Number(p.price).toFixed(2)}) — Stock: {p.quantity_in_stock}
                      </option>
                    ))}
                  </select>
                </div>
                <div style={{ width: 100 }}>
                  <input
                    type="number"
                    className="form-control"
                    placeholder="Qty"
                    min="1"
                    value={item.quantity}
                    onChange={(e) => updateItem(idx, 'quantity', e.target.value)}
                  />
                </div>
                {item.product_id && item.quantity && (
                  <div style={{ width: 80, padding: '9px 0', textAlign: 'right', fontWeight: 600, color: 'var(--gray-700)', fontSize: 14 }}>
                    ${(getUnitPrice(item.product_id) * Number(item.quantity)).toFixed(2)}
                  </div>
                )}
                <button className="btn-icon" onClick={() => removeItem(idx)} disabled={orderItems.length === 1} style={{ flexShrink: 0 }}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M18 6L6 18M6 6l12 12" />
                  </svg>
                </button>
              </div>
            ))}
            {errors.items && <p className="error-text">{errors.items}</p>}
          </div>

          {orderItems.some((i) => i.product_id && i.quantity) && (
            <div className="order-preview">
              <h4>Order Preview</h4>
              {orderItems.filter((i) => i.product_id && i.quantity).map((item, idx) => (
                <div key={idx} className="preview-item">
                  <span>{getProductName(item.product_id)} × {item.quantity}</span>
                  <span>${(getUnitPrice(item.product_id) * Number(item.quantity)).toFixed(2)}</span>
                </div>
              ))}
              <div className="preview-total">
                <span>Total</span>
                <span>${previewTotal.toFixed(2)}</span>
              </div>
            </div>
          )}
        </Modal>
      )}
    </div>
  )
}
