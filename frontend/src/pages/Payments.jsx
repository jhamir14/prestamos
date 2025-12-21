import React, { useEffect, useState } from 'react';
import api from '../api';
import { CheckCircle, XCircle, Filter } from 'lucide-react';
import ConfirmationModal from '../components/ConfirmationModal';

const Payments = () => {
    const [installments, setInstallments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filterType, setFilterType] = useState('default'); // 'default' (overdue+today), 'today', 'overdue', 'all'

    // Payment Form State
    const [payingItem, setPayingItem] = useState(null);
    const [amount, setAmount] = useState('');
    const [method, setMethod] = useState('Efectivo');

    useEffect(() => {
        fetchInstallments();
    }, []);

    const fetchInstallments = async () => {
        try {
            const [contractsRes, loansRes, devicesRes] = await Promise.all([
                api.get('/contracts/installments/'),
                api.get('/loans/installments/'),
                api.get('/devices/installments/')
            ]);

            const all = [
                ...contractsRes.data.map(i => ({ ...i, type: 'Contrato', source_id: i.contrato })),
                ...loansRes.data.map(i => ({ ...i, type: 'Préstamo', source_id: i.prestamo })),
                ...devicesRes.data.map(i => ({ ...i, type: 'Dispositivo', source_id: i.sale }))
            ].sort((a, b) => new Date(a.fecha_vencimiento) - new Date(b.fecha_vencimiento));

            setInstallments(all);
            setLoading(false);
        } catch (err) {
            console.error(err);
            setLoading(false);
        }
    };

    const handlePayClick = (item) => {
        if (item.pagado) return;
        setPayingItem(item);
        setAmount(item.monto - (item.monto_pagado || 0));
        setMethod('Efectivo');
    };

    const handleSubmitPayment = async (e) => {
        e.preventDefault();
        const endpoint = payingItem.type === 'Contrato'
            ? `/contracts/installments/${payingItem.id}/pay/`
            : payingItem.type === 'Dispositivo'
                ? `/devices/installments/${payingItem.id}/pay/`
                : `/loans/installments/${payingItem.id}/pay/`;

        try {
            await api.post(endpoint, {
                monto: amount,
                metodo_pago: method
            });
            setPayingItem(null);
            fetchInstallments();
        } catch (err) {
            console.error(err);
            if (err.response) {
                alert(`Error: ${err.response.status} - ${JSON.stringify(err.response.data)}`);
            } else {
                alert(`Error: ${err.message}`);
            }
        }
    };

    const getTodayString = () => {
        const d = new Date();
        return d.toISOString().split('T')[0];
    };

    const todayStr = getTodayString();

    const overdue = installments.filter(i => !i.pagado && i.fecha_vencimiento < todayStr);
    const today = installments.filter(i => !i.pagado && i.fecha_vencimiento === todayStr);
    const allPending = installments.filter(i => !i.pagado);

    let displayedInstallments = [];
    if (filterType === 'today') {
        displayedInstallments = today;
    } else if (filterType === 'overdue') {
        displayedInstallments = overdue;
    } else if (filterType === 'all') {
        displayedInstallments = allPending;
    } else {
        // Default: Overdue + Today
        displayedInstallments = [...overdue, ...today];
    }

    displayedInstallments.sort((a, b) => new Date(a.fecha_vencimiento) - new Date(b.fecha_vencimiento));

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-3xl font-bold text-gray-800 dark:text-white">Pagos</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div onClick={() => setFilterType('overdue')} className="bg-red-50 dark:bg-red-900/20 border border-red-100 dark:border-red-900/30 p-4 rounded-lg text-red-800 dark:text-red-300 cursor-pointer hover:bg-red-100 dark:hover:bg-red-900/30 transition-all duration-200">
                    <h3 className="font-bold text-lg">Vencidos</h3>
                    <p className="text-2xl font-bold mt-1">{overdue.length} <span className="text-sm font-normal opacity-80">cuotas</span></p>
                </div>
                <div onClick={() => setFilterType('today')} className="bg-amber-50 dark:bg-amber-900/20 border border-amber-100 dark:border-amber-900/30 p-4 rounded-lg text-amber-800 dark:text-amber-300 cursor-pointer hover:bg-amber-100 dark:hover:bg-amber-900/30 transition-all duration-200">
                    <h3 className="font-bold text-lg">Hoy</h3>
                    <p className="text-2xl font-bold mt-1">{today.length} <span className="text-sm font-normal opacity-80">cuotas</span></p>
                </div>
            </div>

            <div className="flex space-x-2 mb-4 overflow-x-auto pb-2">
                <button
                    onClick={() => setFilterType('default')}
                    className={`px-4 py-2 rounded whitespace-nowrap ${filterType === 'default' ? 'bg-gray-800 text-white' : 'bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-200'}`}
                >
                    Prioritarios
                </button>
                <button
                    onClick={() => setFilterType('overdue')}
                    className={`px-4 py-2 rounded whitespace-nowrap ${filterType === 'overdue' ? 'bg-red-600 text-white' : 'bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-200'}`}
                >
                    Vencidos
                </button>
                <button
                    onClick={() => setFilterType('today')}
                    className={`px-4 py-2 rounded whitespace-nowrap ${filterType === 'today' ? 'bg-yellow-500 text-white' : 'bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-200'}`}
                >
                    Hoy
                </button>
                <button
                    onClick={() => setFilterType('all')}
                    className={`px-4 py-2 rounded whitespace-nowrap ${filterType === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-800 dark:bg-gray-700 dark:text-gray-200'}`}
                >
                    Todos (Pendientes)
                </button>
            </div>

            {/* Mobile Cards / Desktop Table */}
            <div className="grid grid-cols-1 gap-4 md:hidden mb-6">
                {displayedInstallments.length > 0 ? displayedInstallments.map((item) => {
                    const abonado = parseFloat(item.monto_pagado || 0);
                    const pendiente = parseFloat(item.monto) - abonado;
                    return (
                        <div key={`${item.type}-${item.id}`} className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow border border-gray-100 dark:border-gray-700">
                            <div className="flex justify-between items-start mb-2">
                                <div>
                                    <h3 className="font-bold text-gray-900 dark:text-white">{item.client_name}</h3>
                                    <div className="text-xs text-gray-500">
                                        {item.type === 'Dispositivo' ? item.device_name :
                                            item.type === 'Contrato' ? item.moto_name :
                                                item.type}
                                        #{item.source_id}
                                    </div>
                                </div>
                                <div>
                                    {item.pagado ? (
                                        <span className="text-green-600 bg-green-100 px-2 py-1 rounded-full text-xs font-semibold dark:bg-green-900 dark:text-green-300">Pagado</span>
                                    ) : (
                                        <span className="text-red-600 bg-red-100 px-2 py-1 rounded-full text-xs font-semibold dark:bg-red-900 dark:text-red-300">Pendiente</span>
                                    )}
                                </div>
                            </div>

                            <div className="grid grid-cols-3 gap-2 text-sm text-gray-600 dark:text-gray-400 mb-4 bg-gray-50 dark:bg-gray-700/30 p-3 rounded-lg border border-gray-100 dark:border-gray-700">
                                <div>
                                    <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Vence</p>
                                    <p className="font-semibold text-red-600 dark:text-red-400">{item.fecha_vencimiento}</p>
                                </div>
                                <div className="text-center">
                                    <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Monto</p>
                                    <p className="font-semibold dark:text-gray-200">S/ {item.monto}</p>
                                </div>
                                <div className="text-right">
                                    <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">Debe</p>
                                    <p className="font-bold text-gray-900 dark:text-white">S/ {pendiente.toFixed(2)}</p>
                                </div>
                            </div>

                            {!item.pagado && (
                                <button
                                    onClick={() => handlePayClick(item)}
                                    className="w-full py-2 bg-green-600 hover:bg-green-700 text-white rounded font-medium transition-colors shadow-sm"
                                >
                                    Registrar Pago
                                </button>
                            )}
                        </div>
                    );
                }) : (
                    <div className="text-center text-gray-500 py-8">No hay pagos pendientes para este filtro.</div>
                )}
            </div>

            <div className="hidden md:block bg-white dark:bg-gray-800 rounded shadow overflow-x-auto transition-colors duration-200">
                <table className="w-full">
                    <thead className="bg-gray-50 dark:bg-gray-700">
                        <tr>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Vencimiento</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Cliente</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Monto</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Abonado</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Pendiente</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Estado</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Acción</th>
                        </tr>
                    </thead>
                    <tbody>
                        {displayedInstallments.length > 0 ? displayedInstallments.map((item, idx) => {
                            const abonado = parseFloat(item.monto_pagado || 0);
                            const pendiente = parseFloat(item.monto) - abonado;
                            return (
                                <tr key={`${item.type}-${item.id}`} className="hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-300">
                                    <td className="p-4">{item.fecha_vencimiento}</td>
                                    <td className="p-4">
                                        <div className="font-bold">{item.client_name}</div>
                                        <div className="text-xs text-gray-500">
                                            {item.type === 'Dispositivo' ? item.device_name :
                                                item.type === 'Contrato' ? item.moto_name :
                                                    item.type}
                                            #{item.source_id}
                                        </div>
                                    </td>
                                    <td className="p-4">S/ {item.monto}</td>
                                    <td className="p-4 text-green-600">S/ {abonado.toFixed(2)}</td>
                                    <td className="p-4 text-red-600">S/ {pendiente.toFixed(2)}</td>
                                    <td className="p-4">
                                        {item.pagado ? (
                                            <span className="text-green-600 dark:text-green-400 flex items-center"><CheckCircle className="w-4 h-4 mr-1" /> Pagado</span>
                                        ) : (
                                            <span className="text-red-600 dark:text-red-400 flex items-center"><XCircle className="w-4 h-4 mr-1" /> Pendiente</span>
                                        )}
                                    </td>
                                    <td className="p-4">
                                        {!item.pagado && (
                                            <button
                                                onClick={() => handlePayClick(item)}
                                                className="px-3 py-1 rounded text-white bg-green-600 hover:bg-green-700"
                                            >
                                                Pagar
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            );
                        }) : (
                            <tr>
                                <td colSpan="7" className="p-4 text-center text-gray-500">No hay pagos pendientes para este filtro.</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            {/* Payment Modal */}
            {payingItem && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl w-96">
                        <h4 className="text-lg font-bold mb-4 text-gray-900 dark:text-white">
                            Registrar Pago - {payingItem.type} #{payingItem.source_id}
                        </h4>
                        <form onSubmit={handleSubmitPayment}>
                            <div className="mb-4">
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Método de Pago</label>
                                <select
                                    value={method}
                                    onChange={(e) => setMethod(e.target.value)}
                                    className="w-full border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                >
                                    <option value="Efectivo">Efectivo</option>
                                    <option value="Yape">Yape</option>
                                </select>
                            </div>
                            <div className="mb-4">
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Monto a Pagar</label>
                                <input
                                    type="number"
                                    step="0.01"
                                    value={amount}
                                    onChange={(e) => setAmount(e.target.value)}
                                    className="w-full border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                    required
                                />
                            </div>
                            <div className="flex justify-end space-x-2">
                                <button
                                    type="button"
                                    onClick={() => setPayingItem(null)}
                                    className="px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300"
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
                                >
                                    Confirmar Pago
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Payments;
