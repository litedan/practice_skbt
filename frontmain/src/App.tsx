import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { AuthProvider } from './auth/AuthContext'
import { ProtectedRoute } from './auth/ProtectedRoute'
import { AppLayout } from './components/AppLayout'
import { LoginPage } from './pages/LoginPage'
import { HomePage } from './pages/HomePage'
import { RequestsPage } from './pages/RequestsPage'
import { RequestCreatePage } from './pages/RequestCreatePage'
import { RequestDetailsPage } from './pages/RequestDetailsPage'
import { DocumentsPage } from './pages/DocumentsPage'
import { ProfilePage } from './pages/ProfilePage'
import { HrPanelPage } from './pages/HrPanelPage'
import { HrEmployeePage } from './pages/HrEmployeePage'
import { AdminPage } from './pages/AdminPage'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />

          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/" element={<HomePage />} />
              <Route path="/requests" element={<RequestsPage />} />
              <Route path="/requests/new" element={<RequestCreatePage />} />
              <Route path="/requests/:id" element={<RequestDetailsPage />} />
              <Route path="/documents" element={<DocumentsPage />} />
              <Route path="/profile" element={<ProfilePage />} />

              <Route element={<ProtectedRoute roles={['hr', 'manager']} />}>
                <Route path="/hr" element={<HrPanelPage />} />
                <Route path="/hr/employees/:id" element={<HrEmployeePage />} />
              </Route>

              <Route element={<ProtectedRoute roles={['admin']} />}>
                <Route path="/admin" element={<AdminPage />} />
              </Route>
            </Route>
          </Route>

          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
