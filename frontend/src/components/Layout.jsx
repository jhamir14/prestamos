import React from 'react';
import { Link, useLocation, Outlet } from 'react-router-dom';
import { LayoutDashboard, Users, Bike, FileText, Banknote, Calendar, Shield, Moon, Sun, LogOut, User, Smartphone, ShoppingCart, Menu, X } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';
import { useState } from 'react';

const Layout = () => {
    const location = useLocation();
    const { theme, toggleTheme } = useTheme();
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);

    const navItems = [
        { name: 'Dashboard', path: '/', icon: LayoutDashboard },
        { name: 'Clientes', path: '/clients', icon: Users },
        { name: 'Motos', path: '/motos', icon: Bike },
        { name: 'Dispositivos', path: '/devices', icon: Smartphone },
        { name: 'Contratos', path: '/contracts', icon: FileText },
        { name: 'Ventas Celulares', path: '/device-sales', icon: ShoppingCart },
        { name: 'Generar Contrato', path: '/generate-contract', icon: FileText },
        { name: 'Préstamos', path: '/loans', icon: Banknote },
        { name: 'Pagos', path: '/payments', icon: Calendar },
        { name: 'Admins', path: '/admins', icon: Shield },
    ];

    const toggleSidebar = () => setIsSidebarOpen(!isSidebarOpen);

    return (
        <div className="flex h-screen bg-gray-100 dark:bg-gray-900 transition-colors duration-200">
            {/* Mobile Header */}
            <div className="md:hidden fixed top-0 w-full bg-white dark:bg-gray-800 shadow-md z-20 flex justify-between items-center p-4">
                <div className="flex items-center">
                    <img src="/logoJP.png" alt="Logo" className="h-8 w-auto mr-2" />
                    <span className="font-bold text-blue-600 dark:text-blue-400">JP Motors</span>
                </div>
                <div className="flex items-center space-x-2">
                    <button onClick={toggleTheme} className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300">
                        {theme === 'light' ? <Moon size={20} /> : <Sun size={20} />}
                    </button>
                    <button onClick={toggleSidebar} className="text-gray-700 dark:text-gray-200">
                        {isSidebarOpen ? <X size={24} /> : <Menu size={24} />}
                    </button>
                </div>
            </div>

            {/* Sidebar Overlay */}
            {isSidebarOpen && (
                <div
                    className="fixed inset-0 bg-black bg-opacity-50 z-20 md:hidden"
                    onClick={() => setIsSidebarOpen(false)}
                ></div>
            )}

            {/* Sidebar */}
            <div className={`
                fixed md:static inset-y-0 left-0 w-64 bg-white dark:bg-gray-800 shadow-lg flex flex-col z-30 transform transition-transform duration-300 ease-in-out
                ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}
            `}>
                <div className="p-6 flex flex-col items-center relative border-b dark:border-gray-700 hidden md:flex">
                    <button onClick={toggleTheme} className="absolute top-2 right-2 p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300">
                        {theme === 'light' ? <Moon size={16} /> : <Sun size={16} />}
                    </button>
                    <div className="flex flex-col items-center mt-2">
                        <img src="/logoJP.png" alt="Logo" className="h-12 w-auto mb-2" />
                        <h1 className="text-lg font-bold text-blue-600 dark:text-blue-400 text-center leading-tight">Inversiones JP<br />Motors</h1>
                    </div>
                </div>

                {/* Mobile Sidebar Header */}
                <div className="p-6 flex items-center justify-between border-b dark:border-gray-700 md:hidden">
                    <span className="text-lg font-bold text-blue-600 dark:text-blue-400">Menú</span>
                    <button onClick={() => setIsSidebarOpen(false)}>
                        <X size={24} className="text-gray-600 dark:text-gray-300" />
                    </button>
                </div>

                <nav className="mt-6 flex-1 overflow-y-auto">
                    {navItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = location.pathname === item.path;
                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                onClick={() => setIsSidebarOpen(false)}
                                className={`flex items-center px-6 py-3 text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-gray-700 hover:text-blue-600 dark:hover:text-blue-400 ${isActive ? 'bg-blue-50 dark:bg-gray-700 text-blue-600 dark:text-blue-400 border-r-4 border-blue-600 dark:border-blue-400' : ''
                                    }`}
                            >
                                <Icon className="w-5 h-5 mr-3" />
                                <span className="font-medium">{item.name}</span>
                            </Link>
                        );
                    })}
                </nav>
                <div className="p-4 border-t dark:border-gray-700">
                    <Link
                        to="/profile"
                        onClick={() => setIsSidebarOpen(false)}
                        className={`flex items-center w-full px-6 py-3 text-gray-700 dark:text-gray-300 hover:bg-blue-50 dark:hover:bg-gray-700 hover:text-blue-600 dark:hover:text-blue-400 rounded transition-colors duration-200 mb-2 ${location.pathname === '/profile' ? 'bg-blue-50 dark:bg-gray-700 text-blue-600 dark:text-blue-400' : ''}`}
                    >
                        <User className="w-5 h-5 mr-3" />
                        <span className="font-medium">Mi Perfil</span>
                    </Link>
                    <button
                        onClick={() => {
                            localStorage.removeItem('access');
                            localStorage.removeItem('refresh');
                            window.location.href = '/login';
                        }}
                        className="flex items-center w-full px-6 py-3 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-gray-700 rounded transition-colors duration-200"
                    >
                        <LogOut className="w-5 h-5 mr-3" />
                        <span className="font-medium">Cerrar Sesión</span>
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 overflow-auto pt-16 md:pt-0">
                <div className="p-4 md:p-8">
                    <Outlet />
                </div>
            </div>
        </div>
    );
};

export default Layout;
