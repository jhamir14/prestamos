import React, { useEffect, useState } from 'react';
import api from '../api';
import { CheckCircle, XCircle } from 'lucide-react';
import ConfirmationModal from '../components/ConfirmationModal';

const Payments = () => {
    const [installments, setInstallments] = useState([]);
    const [loading, setLoading] = useState(true);

    // Payment Form State
    const [payingItem, setPayingItem] = useState(null);
    const [amount, setAmount] = useState('');
    const [method, setMethod] = useState('Efectivo');

    useEffect(() => {
        fetchInstallments();
    }, []);

    const fetchInstallments = async () => {
        try {
            const [contractsRes, loansRes] = await Promise.all([
                api.get('/contracts/installments/'),
                api.get('/loans/installments/')
            ]);

            const all = [
                ...contractsRes.data.map(i => ({ ...i, type: 'Contrato', source_id: i.contrato })),
                ...loansRes.data.map(i => ({ ...i, type: 'Préstamo', source_id: i.prestamo }))
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

    // Filtered list for display (only overdue and today)
    const displayedInstallments = [...overdue, ...today].sort((a, b) => new Date(a.fecha_vencimiento) - new Date(b.fecha_vencimiento));

    return (
        <div>
            <h2 className="text-3xl font-bold mb-6">Pagos del Día / Vencidos</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
                <div className="bg-red-100 dark:bg-red-900 p-4 rounded text-red-800 dark:text-red-200">
                    <h3 className="font-bold text-lg">Vencidos</h3>
                    <p className="text-2xl">{overdue.length} cuotas</p>
                </div>
                <div className="bg-yellow-100 dark:bg-yellow-900 p-4 rounded text-yellow-800 dark:text-yellow-200">
                    <h3 className="font-bold text-lg">Hoy</h3>
                    <p className="text-2xl">{today.length} cuotas</p>
                </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded shadow overflow-x-auto transition-colors duration-200">
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
                        {displayedInstallments.map((item, idx) => {
                            const abonado = parseFloat(item.monto_pagado || 0);
                            const pendiente = parseFloat(item.monto) - abonado;
                            return (
                                <tr key={`${item.type}-${item.id}`} className="hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-300">
                                    <td className="p-4">{item.fecha_vencimiento}</td>
                                    <td className="p-4">
                                        <div className="font-bold">{item.client_name}</div>
                                        <div className="text-xs text-gray-500">{item.type} #{item.source_id}</div>
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
                        })}
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
