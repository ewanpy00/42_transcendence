
import { Navigate, Outlet } from 'react-router-dom'

function ProtectedRoute() {
  const isLoggedIn = false

  if (!isLoggedIn) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}

export default ProtectedRoute
