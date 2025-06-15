import React from 'react';
import { Header } from './Header';

interface AppLayoutProps {
  children: React.ReactNode;
}

export const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  return (
    <div className="app-layout">
      <Header />
      
      {/* Main Content with top padding to account for fixed header */}
      <main className="app-layout__content">
        {children}
      </main>
    </div>
  );
};
