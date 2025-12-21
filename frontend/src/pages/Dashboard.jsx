import React, { useEffect, useState } from 'react';
import api from '../api';
import { DollarSign, Bike, AlertCircle, CheckCircle, Users, Banknote, FileText } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const Dashboard = () => {
    const [metrics, setMetrics] = useState({
        total_prestado: 0,
        total_vendido_motos: 0,
        total_vendido_devices: 0, // NEW
        cuotas_vencidas_hoy: 0,
        motos_disponibles: 0,
        motos_ocupadas: 0,
        devices_disponibles: 0, // NEW
        devices_vendidos: 0, // NEW
        total_clientes: 0,
        prestamos_activos: 0,
        contratos_activos: 0,
        ventas_celulares_activas: 0, // NEW
        recent_activity: [],
        income_history: [],
        portfolio_distribution: [],
        moto_status_data: [],
        device_status_data: [] // NEW
    });

    useEffect(() => {
        api.get('/core/dashboard/')
            .then(res => setMetrics(res.data))
            .catch(err => console.error(err));
    }, []);

    const cards = [
        { title: 'Total Prestado', value: `S/ ${metrics.total_prestado}`, icon: DollarSign, color: 'bg-green-500' },
        { title: 'Ventas Motos', value: `S/ ${metrics.total_vendido_motos}`, icon: Bike, color: 'bg-blue-500' },
        { title: 'Ventas Celulares', value: `S/ ${metrics.total_vendido_devices}`, icon: DollarSign, color: 'bg-pink-500' }, // NEW
        { title: 'Cuotas Vencidas', value: metrics.cuotas_vencidas_hoy, icon: AlertCircle, color: 'bg-red-500' },
        { title: 'Motos Disponibles', value: metrics.motos_disponibles, icon: CheckCircle, color: 'bg-teal-500' },
        { title: 'Celulares Disponibles', value: metrics.devices_disponibles, icon: CheckCircle, color: 'bg-cyan-500' }, // NEW
        { title: 'Total Clientes', value: metrics.total_clientes, icon: Users, color: 'bg-purple-500' },
        { title: 'Préstamos Activos', value: metrics.prestamos_activos, icon: Banknote, color: 'bg-indigo-500' },
        { title: 'Contratos Activos', value: metrics.contratos_activos, icon: FileText, color: 'bg-orange-500' },
        { title: 'Ventas Cel. Activas', value: metrics.ventas_celulares_activas, icon: FileText, color: 'bg-pink-600' }, // NEW
    ];

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];
    const PIE_COLORS_PORTFOLIO = ['#6366f1', '#f97316', '#ec4899']; // Indigo, Orange, Pink
    const PIE_COLORS_MOTOS = ['#14b8a6', '#ef4444']; // Teal, Red
    const PIE_COLORS_DEVICES = ['#06b6d4', '#e11d48']; // Cyan, Rose

    return (
        <div>
            <h2 className="text-3xl font-bold mb-6 text-gray-800 dark:text-white">Dashboard</h2>

            {/* Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
                {cards.map((card, index) => {
                    const Icon = card.icon;
                    return (
                        <div key={index} className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md flex items-center transition-colors duration-200 hover:shadow-lg transform hover:-translate-y-1">
                            <div className={`p-4 rounded-full ${card.color} text-white mr-4 shadow-sm`}>
                                <Icon className="w-8 h-8" />
                            </div>
                            <div>
                                <p className="text-gray-500 dark:text-gray-400 text-sm font-medium">{card.title}</p>
                                <p className="text-2xl font-bold text-gray-900 dark:text-white">{card.value}</p>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                {/* Income History Chart */}
                <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md transition-colors duration-200">
                    <h3 className="text-xl font-bold mb-4 text-gray-800 dark:text-white">Ingresos Mensuales Details</h3>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart
                                data={metrics.income_history}
                                margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
                            >
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} />
                                <XAxis dataKey="name" stroke="#6b7280" />
                                <YAxis stroke="#6b7280" />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', color: '#fff' }}
                                    itemStyle={{ color: '#fff' }}
                                />
                                <Legend />
                                <Bar dataKey="prestamos" name="Préstamos" fill="#6366f1" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="contratos" name="Contratos" fill="#f97316" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="devices" name="Celulares" fill="#ec4899" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Distribution Charts */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Portfolio Distribution */}
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md transition-colors duration-200 flex flex-col items-center">
                        <h3 className="text-lg font-bold mb-4 text-gray-800 dark:text-white text-center">Distribución de Cartera</h3>
                        <div className="h-64 w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={metrics.portfolio_distribution}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        fill="#8884d8"
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {metrics.portfolio_distribution && metrics.portfolio_distribution.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={PIE_COLORS_PORTFOLIO[index % PIE_COLORS_PORTFOLIO.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', color: '#fff' }}
                                    />
                                    <Legend verticalAlign="bottom" height={36} />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Moto Status */}
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md transition-colors duration-200 flex flex-col items-center">
                        <h3 className="text-lg font-bold mb-4 text-gray-800 dark:text-white text-center">Estado de Motos</h3>
                        <div className="h-64 w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={metrics.moto_status_data}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        fill="#8884d8"
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {metrics.moto_status_data && metrics.moto_status_data.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={PIE_COLORS_MOTOS[index % PIE_COLORS_MOTOS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', color: '#fff' }}
                                    />
                                    <Legend verticalAlign="bottom" height={36} />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Device Status - NEW CHART */}
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md transition-colors duration-200 flex flex-col items-center md:col-span-2">
                        <h3 className="text-lg font-bold mb-4 text-gray-800 dark:text-white text-center">Estado de Celulares</h3>
                        <div className="h-64 w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={metrics.device_status_data}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        fill="#8884d8"
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {metrics.device_status_data && metrics.device_status_data.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={PIE_COLORS_DEVICES[index % PIE_COLORS_DEVICES.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', color: '#fff' }}
                                    />
                                    <Legend verticalAlign="bottom" height={36} />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Recent Activity */}
                <div className="lg:col-span-2 bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 transition-colors duration-200">
                    <h3 className="text-xl font-bold mb-4 text-gray-800 dark:text-white">Actividad Reciente</h3>
                    <div className="overflow-x-auto">
                        <div className="md:hidden space-y-4">
                            {metrics.recent_activity && metrics.recent_activity.map((item, idx) => (
                                <div key={idx} className="bg-gray-50 dark:bg-gray-750 p-4 rounded-lg border border-gray-100 dark:border-gray-700">
                                    <div className="flex justify-between items-start mb-2">
                                        <span className={`px-2 py-1 rounded text-xs font-semibold ${item.type === 'Préstamo' ? 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200' : 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'}`}>
                                            {item.type}
                                        </span>
                                        <span className="text-xs text-gray-500">{item.date}</span>
                                    </div>
                                    <div className="flex justify-between items-end">
                                        <div>
                                            <p className="text-sm font-medium text-gray-900 dark:text-white">{item.client}</p>
                                        </div>
                                        <p className="text-sm font-bold text-gray-900 dark:text-white">S/ {item.amount}</p>
                                    </div>
                                </div>
                            ))}
                            {(!metrics.recent_activity || metrics.recent_activity.length === 0) && (
                                <p className="text-center text-gray-500 dark:text-gray-400 py-4">No hay actividad reciente</p>
                            )}
                        </div>

                        <table className="w-full hidden md:table">
                            <thead>
                                <tr className="text-left text-gray-500 dark:text-gray-400 border-b dark:border-gray-700">
                                    <th className="pb-3">Tipo</th>
                                    <th className="pb-3">Cliente</th>
                                    <th className="pb-3">Monto</th>
                                    <th className="pb-3">Fecha</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100 dark:divide-gray-700">
                                {metrics.recent_activity && metrics.recent_activity.map((item, idx) => (
                                    <tr key={idx} className="text-gray-700 dark:text-gray-300">
                                        <td className="py-3">
                                            <span className={`px-2 py-1 rounded text-xs font-semibold ${item.type === 'Préstamo' ? 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200' : 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200'}`}>
                                                {item.type}
                                            </span>
                                        </td>
                                        <td className="py-3">{item.client}</td>
                                        <td className="py-3 font-medium">S/ {item.amount}</td>
                                        <td className="py-3 text-sm text-gray-500 dark:text-gray-400">{item.date}</td>
                                    </tr>
                                ))}
                                {(!metrics.recent_activity || metrics.recent_activity.length === 0) && (
                                    <tr>
                                        <td colSpan="4" className="py-4 text-center text-gray-500 dark:text-gray-400">No hay actividad reciente</td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 transition-colors duration-200">
                    <h3 className="text-xl font-bold mb-4 text-gray-800 dark:text-white">Acciones Rápidas</h3>
                    <div className="space-y-4">
                        <a href="/loans" className="block w-full bg-indigo-600 hover:bg-indigo-700 text-white text-center py-3 rounded-lg font-semibold transition-colors shadow-md">
                            Nuevo Préstamo
                        </a>
                        <a href="/contracts" className="block w-full bg-orange-600 hover:bg-orange-700 text-white text-center py-3 rounded-lg font-semibold transition-colors shadow-md">
                            Nuevo Contrato
                        </a>
                        <a href="/clients" className="block w-full bg-purple-600 hover:bg-purple-700 text-white text-center py-3 rounded-lg font-semibold transition-colors shadow-md">
                            Registrar Cliente
                        </a>
                        <a href="/payments" className="block w-full bg-green-600 hover:bg-green-700 text-white text-center py-3 rounded-lg font-semibold transition-colors shadow-md">
                            Registrar Pago
                        </a>
                        <a href="/devices" className="block w-full bg-cyan-600 hover:bg-cyan-700 text-white text-center py-3 rounded-lg font-semibold transition-colors shadow-md">
                            Registrar Celular
                        </a>
                        <a href="/device-sales" className="block w-full bg-pink-600 hover:bg-pink-700 text-white text-center py-3 rounded-lg font-semibold transition-colors shadow-md">
                            Registrar Venta Celular
                        </a>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
