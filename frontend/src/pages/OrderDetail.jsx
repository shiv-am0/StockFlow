import { useState, useEffect, useCallback } from 'react'
import { useParams, Link } from 'react-router-dom'
import { orderApi } from '../api/orders'
import { useApp } from '../context/AppContext'
import Loading from '../components/Loading'

const STATUS_COLORS = {
  pending: 'badge-warning',
  delivered: 'badge-success',
  cancelled: 'badge-danger',
}

export default function OrderDetail() {
  const { id } = useParams()
  const [order, setOrder] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [updating, setUpdating] = useState(false)
  const { showToast } = useApp()

  const fetchOrder = useCallback(() => {
    setLoading(true)
    orderApi.get(id)
      .then((res) => setOrder(res.data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [id])

  useEffect(() => { fetchOrder() }, [fetchOrder])

  const handleStatusUpdate = async (newStatus) => {
    setUpdating(true)
    try {
      const res = await orderApi.updateStatus(id, newStatus)
      setOrder(res.data)
      showToast(`Order marked as ${newStatus}`)
    } catch (err) {
      showToast(err.response?.data?.detail || err.message, 'error')
    } finally {
      setUpdating(false)
    }
  }

  if (loading) return <Loading />
  if (error) return <div className="empty-state"><h3>{error}</h3></div>
  if (!order) return <div className="empty-state"><h3>Order not found</h3></div>

  const formatDate = (d) => new Date(d).toLocaleString('en-US', {
    year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit',
  })

  const statusBadgeClass = STATUS_COLORS[order.status] || 'badge-success'

  return (
    <div>
      <Link to="/orders" className="back-link">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M19 12H5M12 19l-7-7 7-7" />
        </svg>
        Back to Orders
      </Link>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h2 style={{ fontSize: 22, fontWeight: 700 }}>Order #{order.id}</h2>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          {order.status === 'pending' && (
            <>
              <button
                className="btn btn-sm btn-success"
                onClick={() => handleStatusUpdate('delivered')}
                disabled={updating}
              >
                {updating ? 'Updating...' : 'Mark Delivered'}
              </button>
              <button
                className="btn btn-sm btn-danger"
                onClick={() => handleStatusUpdate('cancelled')}
                disabled={updating}
              >
                {updating ? 'Updating...' : 'Cancel Order'}
              </button>
            </>
          )}
          <span className={`badge ${statusBadgeClass}`} style={{ fontSize: 14, padding: '4px 14px' }}>
            {order.status}
          </span>
        </div>
      </div>

      <div className="detail-grid">
        <div className="card detail-section">
          <h3>Customer Information</h3>
          <div className="detail-row">
            <span className="detail-label">Name</span>
            <span className="detail-value">{order.customer_name}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Customer ID</span>
            <span className="detail-value">#{order.customer_id}</span>
          </div>
        </div>

        <div className="card detail-section">
          <h3>Order Details</h3>
          <div className="detail-row">
            <span className="detail-label">Order Date</span>
            <span className="detail-value">{formatDate(order.created_at)}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Items</span>
            <span className="detail-value">{order.items.length}</span>
          </div>
          <div className="detail-row">
            <span className="detail-label">Total Amount</span>
            <span className="detail-value" style={{ fontSize: 18, color: 'var(--primary)' }}>
              ${Number(order.total_amount).toFixed(2)}
            </span>
          </div>
        </div>
      </div>

      <div className="card" style={{ padding: 0 }}>
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--gray-200)' }}>
          <h3 style={{ fontSize: 15, fontWeight: 600 }}>Ordered Products</h3>
        </div>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Product</th>
                <th>Unit Price</th>
                <th>Quantity</th>
                <th style={{ textAlign: 'right' }}>Subtotal</th>
              </tr>
            </thead>
            <tbody>
              {order.items.map((item) => (
                <tr key={item.id}>
                  <td style={{ fontWeight: 500 }}>{item.product_name}</td>
                  <td>${Number(item.unit_price).toFixed(2)}</td>
                  <td>{item.quantity}</td>
                  <td style={{ textAlign: 'right', fontWeight: 600 }}>
                    ${Number(item.subtotal).toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr>
                <td colSpan={3} style={{ textAlign: 'right', fontWeight: 600, padding: '14px 16px', fontSize: 15 }}>
                  Total
                </td>
                <td style={{ textAlign: 'right', fontWeight: 700, padding: '14px 16px', fontSize: 16, color: 'var(--primary)' }}>
                  ${Number(order.total_amount).toFixed(2)}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>
  )
}
