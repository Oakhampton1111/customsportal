import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppLayout } from './components/layout/AppLayout';
import { 
  Dashboard, 
  TariffTree, 
  AIAssistant, 
  ExportTariffs 
} from './pages';
import './styles/modern-enterprise.css';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
});

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <AppLayout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/tariff-tree" element={<TariffTree />} />
            <Route path="/ai-assistant" element={<AIAssistant />} />
            <Route path="/export-tariffs" element={<ExportTariffs />} />
            
            {/* Legacy route redirects for backward compatibility */}
            <Route path="/duty-calculator" element={<AIAssistant />} />
            <Route path="/search" element={<AIAssistant />} />
            <Route path="/tariff-lookup" element={<TariffTree />} />
          </Routes>
        </AppLayout>
      </Router>
    </QueryClientProvider>
  );
};

export default App;
