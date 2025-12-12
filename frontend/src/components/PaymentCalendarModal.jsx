import React from 'react';
import { X, CheckCircle, XCircle } from 'lucide-react';

const PaymentCalendarModal = ({ isOpen, onClose, title, installments, onPay }) => {
    const [payingQuota, setPayingQuota] = React.useState(null);
    const [amount, setAmount] = React.useState('');
    const [method, setMethod] = React.useState('Efectivo');

    if (!isOpen) return null;

    const handlePayClick = (item) => {
        if (item.pagado) {
            // If already paid, maybe allow unmarking? User asked for payment form.
            // For now, let's keep the old behavior for unmarking or disable it?
            // "si cancelo menos de la cuota se reste a la cuota pendiente" implies partial payments.
            // Unmarking might be complex with partial payments. Let's assume "Pagar" opens the form.
            // If fully paid, maybe just show "Pagado".
            return;
        }
        setPayingQuota(item);
        setAmount(item.monto - (item.monto_pagado || 0)); // Default to remaining
        setMethod('Efectivo');
    };

    const handleSubmitPayment = (e) => {
        e.preventDefault();
        onPay(payingQuota, amount, method);
        setPayingQuota(null);
    };

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg w-full max-w-3xl max-h-[80vh] overflow-hidden flex flex-col relative">
                <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-bold text-gray-900 dark:text-white">{title}</h3>
                    <button onClick={onClose} className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="overflow-y-auto flex-1">
                    <table className="w-full">
                        <thead className="bg-gray-50 dark:bg-gray-700 sticky top-0">
                            <tr>
                                <th className="p-3 text-left text-gray-700 dark:text-gray-200">#</th>
                                <th className="p-3 text-left text-gray-700 dark:text-gray-200">Vencimiento</th>
                                <th className="p-3 text-left text-gray-700 dark:text-gray-200">Monto</th>
                                <th className="p-3 text-left text-gray-700 dark:text-gray-200">Abonado</th>
                                <th className="p-3 text-left text-gray-700 dark:text-gray-200">Pendiente</th>
                                <th className="p-3 text-left text-gray-700 dark:text-gray-200">Estado</th>
                                <th className="p-3 text-left text-gray-700 dark:text-gray-200">Acción</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                            {installments.map((item) => {
                                const abonado = parseFloat(item.monto_pagado || 0);
                                const pendiente = parseFloat(item.monto) - abonado;
                                return (
                                    <tr key={item.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-300">
                                        <td className="p-3">{item.numero}</td>
                                        <td className="p-3">{item.fecha_vencimiento}</td>
                                        <td className="p-3">S/ {item.monto}</td>
                                        <td className="p-3 text-green-600">S/ {abonado.toFixed(2)}</td>
                                        <td className="p-3 text-red-600">S/ {pendiente.toFixed(2)}</td>
                                        <td className="p-3">
                                            {item.pagado ? (
                                                <span className="text-green-600 dark:text-green-400 flex items-center"><CheckCircle className="w-4 h-4 mr-1" /> Pagado</span>
                                            ) : (
                                                <span className="text-orange-500 dark:text-orange-400 flex items-center"><XCircle className="w-4 h-4 mr-1" /> Pendiente</span>
                                            )}
                                        </td>
                                        <td className="p-3">
                                            {!item.pagado && (
                                                <button
                                                    onClick={() => handlePayClick(item)}
                                                    className="px-3 py-1 rounded text-white text-sm bg-green-600 hover:bg-green-700"
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

                {/* Payment Form Overlay */}
                {payingQuota && (
                    <div className="absolute inset-0 bg-black bg-opacity-50 flex justify-center items-center">
                        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl w-96">
                            <h4 className="text-lg font-bold mb-4 text-gray-900 dark:text-white">Registrar Pago - Cuota #{payingQuota.numero}</h4>
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
                                        onClick={() => setPayingQuota(null)}
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
        </div>
    );
};

export default PaymentCalendarModal;
