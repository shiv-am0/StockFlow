import { useState, useEffect, useCallback } from 'react'
import { productApi } from '../api/products'
import { useApp } from '../context/AppContext'
import Modal from '../components/Modal'
import Pagination from '../components/Pagination'
import Loading from '../components/Loading'
import EmptyState from '../components/EmptyState'

const emptyForm = { product_name: '', sku: '', price: '', quantity_in_stock: '' }

export default function Products() {
  const [products, setProducts] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [search, setSearch] = useState('')
  const [loading, setLoading] = useState(true)
  const [modal, setModal] = useState(null)
  const [form, setForm] = useState(emptyForm)
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)
  const { showToast } = useApp()

  const fetchProducts = useCallback(() => {
    setLoading(true)
    productApi.list({ page, page_size: 10, search: search || undefined })
      .then((res) => {
        setProducts(res.data.items)
        setTotal(res.data.total)
        setTotalPages(res.data.total_pages)
      })
      .catch((err) => showToast(err.message, 'error'))
      .finally(() => setLoading(false))
  }, [page, search, showToast])

  useEffect(() => { fetchProducts() }, [fetchProducts])

  const handleSearch = (val) => {
    setSearch(val)
    setPage(1)
  }

  const openAdd = () => {
    setForm(emptyForm)
    setErrors({})
    setModal('add')
  }

  const openEdit = (product) => {
    setForm({
      product_name: product.product_name,
      sku: product.sku,
      price: product.price,
      quantity_in_stock: product.quantity_in_stock,
    })
    setErrors({})
    setModal(product.id)
  }

  const validate = () => {
    const e = {}
    if (!form.product_name.trim()) e.product_name = 'Product name is required'
    if (!form.sku.trim()) e.sku = 'SKU is required'
    else if (!/^[a-zA-Z0-9]+$/.test(form.sku)) e.sku = 'SKU must be alphanumeric only'
    if (!form.price || Number(form.price) <= 0) e.price = 'Price must be positive'
    if (form.quantity_in_stock === '' || Number(form.quantity_in_stock) < 0) e.quantity_in_stock = 'Quantity cannot be negative'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = async () => {
    if (!validate()) return
    setSubmitting(true)
    try {
      const payload = { ...form, price: Number(form.price), quantity_in_stock: Number(form.quantity_in_stock) }
      if (modal === 'add') {
        await productApi.create(payload)
        showToast('Product created successfully')
      } else {
        await productApi.update(modal, payload)
        showToast('Product updated successfully')
      }
      setModal(null)
      fetchProducts()
    } catch (err) {
      showToast(err.message, 'error')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Delete product "${name}"?`)) return
    try {
      await productApi.delete(id)
      showToast('Product deleted')
      fetchProducts()
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
              placeholder="Search products..."
              value={search}
              onChange={(e) => handleSearch(e.target.value)}
            />
          </div>
        </div>
        <button className="btn btn-primary" onClick={openAdd}>+ Add Product</button>
      </div>

      {loading ? <Loading /> : products.length === 0 ? (
        <EmptyState
          title="No products found"
          message={search ? 'Try a different search term' : 'Add your first product to get started'}
          action={<button className="btn btn-primary" onClick={openAdd}>+ Add Product</button>}
        />
      ) : (
        <div className="card" style={{ padding: 0 }}>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Product Name</th>
                  <th>SKU</th>
                  <th>Price</th>
                  <th>Stock</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {products.map((p) => (
                  <tr key={p.id}>
                    <td style={{ fontWeight: 500 }}>{p.product_name}</td>
                    <td>{p.sku}</td>
                    <td>${Number(p.price).toFixed(2)}</td>
                    <td>
                      <span className={p.quantity_in_stock < 10 ? 'badge badge-warning' : ''}>
                        {p.quantity_in_stock}
                      </span>
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button className="btn-icon" style={{ marginRight: 6 }} onClick={() => openEdit(p)} title="Edit">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <path d="M11 4H4a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2v-7" />
                          <path d="M18.5 2.5a2.121 2.121 0 013 3L12 15l-4 1 1-4 9.5-9.5z" />
                        </svg>
                      </button>
                      <button className="btn-icon" onClick={() => handleDelete(p.id, p.product_name)} title="Delete" style={{ color: 'var(--danger)' }}>
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

      {modal && (
        <Modal
          title={modal === 'add' ? 'Add Product' : 'Edit Product'}
          onClose={() => setModal(null)}
          footer={
            <>
              <button className="btn btn-secondary" onClick={() => setModal(null)}>Cancel</button>
              <button className="btn btn-primary" onClick={handleSubmit} disabled={submitting}>
                {submitting ? 'Saving...' : modal === 'add' ? 'Create Product' : 'Save Changes'}
              </button>
            </>
          }
        >
          <div className="form-group">
            <label>Product Name</label>
            <input
              className={`form-control ${errors.product_name ? 'error' : ''}`}
              value={form.product_name}
              onChange={(e) => setForm({ ...form, product_name: e.target.value })}
            />
            {errors.product_name && <p className="error-text">{errors.product_name}</p>}
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>SKU</label>
              <input
                className={`form-control ${errors.sku ? 'error' : ''}`}
                value={form.sku}
                onChange={(e) => setForm({ ...form, sku: e.target.value })}
              />
              {errors.sku && <p className="error-text">{errors.sku}</p>}
            </div>
            <div className="form-group">
              <label>Price ($)</label>
              <input
                type="number"
                step="0.01"
                className={`form-control ${errors.price ? 'error' : ''}`}
                value={form.price}
                onChange={(e) => setForm({ ...form, price: e.target.value })}
              />
              {errors.price && <p className="error-text">{errors.price}</p>}
            </div>
          </div>
          <div className="form-group">
            <label>Quantity in Stock</label>
            <input
              type="number"
              className={`form-control ${errors.quantity_in_stock ? 'error' : ''}`}
              value={form.quantity_in_stock}
              onChange={(e) => setForm({ ...form, quantity_in_stock: e.target.value })}
            />
            {errors.quantity_in_stock && <p className="error-text">{errors.quantity_in_stock}</p>}
          </div>
        </Modal>
      )}
    </div>
  )
}
