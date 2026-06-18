import { useState, useEffect } from 'react'
import { dashboardApi } from '../api/dashboard'
import Loading from '../components/Loading'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    dashboardApi.stats()
      .then((res) => setStats(res.data))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <Loading />
  if (!stats) return null

  const cards = [
    { label: 'Total Products', value: stats.total_products, icon: '📦', color: 'blue' },
    { label: 'Total Customers', value: stats.total_customers, icon: '👥', color: 'green' },
    { label: 'Total Orders', value: stats.total_orders, icon: '📋', color: 'yellow' },
    { label: 'Low Stock Items', value: stats.low_stock_count, icon: '⚠️', color: 'red' },
  ]

  return (
    <div>
      <div className="stats-grid">
        {cards.map((card) => (
          <div key={card.label} className="card stat-card">
            <div className={`stat-icon ${card.color}`}>{card.icon}</div>
            <div className="stat-info">
              <h3>{card.value}</h3>
              <p>{card.label}</p>
            </div>
          </div>
        ))}
      </div>

      {stats.low_stock_products?.length > 0 && (
        <div className="card" style={{ padding: 0 }}>
          <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--gray-200)' }}>
            <h3 style={{ fontSize: 15, fontWeight: 600 }}>Low Stock Alerts</h3>
          </div>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Product</th>
                  <th>SKU</th>
                  <th>Stock</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {stats.low_stock_products.map((p) => (
                  <tr key={p.id}>
                    <td style={{ fontWeight: 500 }}>{p.product_name}</td>
                    <td>{p.sku}</td>
                    <td>{p.quantity_in_stock}</td>
                    <td>
                      <span className={`badge ${p.quantity_in_stock === 0 ? 'badge-danger' : 'badge-warning'}`}>
                        {p.quantity_in_stock === 0 ? 'Out of Stock' : 'Low Stock'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
