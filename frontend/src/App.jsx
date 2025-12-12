import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Clients from './pages/Clients';
import Motos from './pages/Motos';
import Contracts from './pages/Contracts';
import Loans from './pages/Loans';
import Payments from './pages/Payments';
import Login from './pages/Login';
import Admins from './pages/Admins';
import Profile from './pages/Profile';
import GenerateContract from './pages/GenerateContract';
import Devices from './pages/Devices';
import DeviceSales from './pages/DeviceSales';
import { ThemeProvider } from './context/ThemeContext';

const PrivateRoute = () => {
  const token = localStorage.getItem('access');
  return token ? <Outlet /> : <Navigate to="/login" />;
};

function App() {
  return (
    <ThemeProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route element={<PrivateRoute />}>
            <Route element={<Layout />}>
              <Route path="/" element={<Dashboard />} />
              <Route path="/clients" element={<Clients />} />
              <Route path="/motos" element={<Motos />} />
              <Route path="/devices" element={<Devices />} />
              <Route path="/contracts" element={<Contracts />} />
              <Route path="/device-sales" element={<DeviceSales />} />
              <Route path="/generate-contract" element={<GenerateContract />} />
              <Route path="/loans" element={<Loans />} />
              <Route path="/payments" element={<Payments />} />
              <Route path="/admins" element={<Admins />} />
              <Route path="/profile" element={<Profile />} />
            </Route>
          </Route>
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
