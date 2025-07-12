import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { AuthProvider } from './components/portal/auth/AuthProvider';
import PortalRoutes from './components/portal/PortalRoutes';
import './styles/portal/portal.css';

function App() {
  return (
    <Router>
      <AuthProvider>
        <div className="App">
          <PortalRoutes />
        </div>
      </AuthProvider>
    </Router>
  );
}

export default App;
