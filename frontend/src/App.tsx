import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout } from 'antd';
import MainLayout from './components/Layout/MainLayout';
import Dashboard from './pages/Dashboard';
import Backtesting from './pages/Backtesting';
import Performance from './pages/Performance';
import './App.css';

const { Content } = Layout;

const App: React.FC = () => {
  return (
    <MainLayout>
      <Content className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/backtesting" element={<Backtesting />} />
          <Route path="/performance" element={<Performance />} />
        </Routes>
      </Content>
    </MainLayout>
  );
};

export default App; 