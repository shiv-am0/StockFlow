import { useLocation } from 'react-router-dom'

const pageTitles = {
  '/dashboard': 'Dashboard',
  '/products': 'Products',
  '/customers': 'Customers',
  '/orders': 'Orders',
}

export default function Header({ onMenuClick }) {
  const location = useLocation()
  const basePath = '/' + location.pathname.split('/')[1]
  const title = pageTitles[basePath] || 'StockFlow'

  return (
    <header className="header">
      <button className="mobile-toggle" onClick={onMenuClick}>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M3 12h18M3 6h18M3 18h18" />
        </svg>
      </button>
      <h1 className="header-title">{title}</h1>
    </header>
  )
}
