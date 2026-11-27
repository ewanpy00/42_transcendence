
import { Link, Outlet } from 'react-router-dom'

function MainLayout() {
  return (
    <div>
      <nav>
        <Link to="/">Home</Link>
        {' | '}
        <Link to="/login">Login</Link>
        {' | '}
        <Link to="/dashboard">Dashboard</Link>
      </nav>

      <main>
        <Outlet />
      </main>
    </div>
  )
}

export default MainLayout
