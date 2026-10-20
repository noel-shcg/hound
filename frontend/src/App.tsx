import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Dashboard } from './dashboard/Dashboard';
import { authApi } from './api/auth';

// Management pages (to be implemented)
const ManagementLogin = () => <div className="page">Login Page - To be implemented</div>;
const ManagementDashboard = () => <div className="page">Management Dashboard - To be implemented</div>;

function App() {
  return (
    <Router>
      <Routes>
        {/* Dashboard - no authentication required */}
        <Route path="/" element={<Dashboard />} />
        
        {/* Management interface - authentication required */}
        <Route path="/management/login" element={<ManagementLogin />} />
        <Route
          path="/management/*"
          element={
            authApi.isAuthenticated() ? (
              <ManagementDashboard />
            ) : (
              <Navigate to="/management/login" replace />
            )
          }
        />
        
        {/* Catch all - redirect to dashboard */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
