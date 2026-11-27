
import {
  BrowserRouter,
  Routes,
  Route,
} from 'react-router-dom'

import MainLayout from './layouts/MainLayout'
import ProtectedRoute from './routes/ProtectedRoute'

import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import DashboardPage from './pages/DashboardPage'

import './App.css'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />

          <Route element={<ProtectedRoute />}>
            <Route
              path="/dashboard"
              element={<DashboardPage />}
            />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
