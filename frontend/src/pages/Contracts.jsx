import React, { useEffect, useState } from 'react';
import api from '../api';
import { Plus, Download, Calendar, FileText } from 'lucide-react';
import PaymentCalendarModal from '../components/PaymentCalendarModal';
import ConfirmationModal from '../components/ConfirmationModal';

const Contracts = () => {
    const [contracts, setContracts] = useState([]);
    const [clients, setClients] = useState([]);
    const [motos, setMotos] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const [formData, setFormData] = useState({
        cliente: '', moto: '', tipo: 'Venta', monto_inicial: '', interes: 54.47, cuotas_totales: '', metodo_pago: 'Diario', fecha_contrato: new Date().toISOString().split('T')[0]
    });
    const [calculation, setCalculation] = useState(null);

    // Modal State
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedContractInstallments, setSelectedContractInstallments] = useState([]);
    const [modalTitle, setModalTitle] = useState('');

    // Confirmation Modal State
    const [isConfirmOpen, setIsConfirmOpen] = useState(false);
    const [confirmAction, setConfirmAction] = useState(null);
    const [confirmMessage, setConfirmMessage] = useState('');
    const [confirmTitle, setConfirmTitle] = useState('');
    const [confirmDestructive, setConfirmDestructive] = useState(false);

    useEffect(() => {
        fetchContracts();
        fetchClients();
        fetchMotos();
    }, []);

    const fetchContracts = () => {
        api.get('/contracts/contracts/')
            .then(res => setContracts(res.data))
            .catch(err => console.error(err));
    };

    const fetchClients = () => {
        api.get('/users/clients/').then(res => setClients(res.data));
    };

    const fetchMotos = () => {
        api.get('/inventory/motos/').then(res => setMotos(res.data));
    };

    const calculate = () => {
        const moto = motos.find(m => m.id === parseInt(formData.moto));
        if (!moto || !formData.monto_inicial || !formData.cuotas_totales) return;

        const restante = parseFloat(moto.precio) - parseFloat(formData.monto_inicial);
        const total = restante * (1 + (parseFloat(formData.interes) / 100));
        const cuota = total / parseInt(formData.cuotas_totales);

        setCalculation({
            restante: restante.toFixed(2),
            total: total.toFixed(2),
            cuota: cuota.toFixed(2)
        });
    };

    useEffect(() => {
        calculate();
    }, [formData.moto, formData.monto_inicial, formData.interes, formData.cuotas_totales]);

    const handleSubmit = (e) => {
        e.preventDefault();
        api.post('/contracts/contracts/', formData)
            .then(() => {
                setShowForm(false);
                fetchContracts();
                fetchMotos();
                setFormData({ cliente: '', moto: '', tipo: 'Venta', monto_inicial: '', interes: 54.47, cuotas_totales: '', metodo_pago: 'Diario' });
                setCalculation(null);
            })
            .catch(err => alert('Error saving contract: ' + JSON.stringify(err.response.data)));
    };

    const handleDownloadPdf = async (contract, type) => {
        try {
            const endpoint = type === 'schedule'
                ? `/contracts/contracts/${contract.id}/download_schedule_pdf/`
                : `/contracts/contracts/${contract.id}/download_contract_pdf/`;

            const response = await api.get(endpoint, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;

            const client = clients.find(c => c.id === contract.cliente);
            const clientName = client ? `${client.nombres}_${client.apellidos}`.replace(/ /g, '_') : 'cliente';

            link.setAttribute('download', type === 'schedule' ? `calendario_pagos_${clientName}.pdf` : `contrato_legal_${clientName}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error('Error downloading PDF:', err);
            alert('Error downloading PDF');
        }
    };

    const handleOpenCalendar = async (contract) => {
        try {
            // Assuming the contract object already has 'cuotas' or we fetch them. 
            // If 'cuotas' are not nested, we might need a separate endpoint or filter.
            // For now, let's assume we need to fetch them or they are in the contract detail.
            // Let's try fetching the specific contract details which usually includes nested serializers.
            const res = await api.get(`/contracts/contracts/${contract.id}/`);
            setSelectedContractInstallments(res.data.cuotas);
            setModalTitle(`Calendario - Contrato #${contract.id}`);
            setIsModalOpen(true);
        } catch (err) {
            console.error(err);
            alert('Error fetching installments');
        }
    };

    const [filterStatus, setFilterStatus] = useState('Activo');

    const filteredContracts = contracts.filter(contract => contract.estado === filterStatus);

    const handlePaymentSubmit = async (installment, amount, method) => {
        try {
            await api.post(`/contracts/installments/${installment.id}/pay/`, {
                monto: amount,
                metodo_pago: method
            });

            // Refresh modal data
            const res = await api.get(`/contracts/contracts/${installment.contrato}/`);
            setSelectedContractInstallments(res.data.cuotas);

            // Refresh main list
            fetchContracts();
        } catch (err) {
            console.error(err);
            alert('Error processing payment');
        }
    };

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-3xl font-bold text-gray-800 dark:text-white">Contratos</h2>
                <button onClick={() => setShowForm(!showForm)} className="bg-blue-600 text-white px-4 py-2 rounded flex items-center hover:bg-blue-700">
                    <Plus className="w-4 h-4 mr-2" /> Nuevo Contrato
                </button>
            </div>

            <div className="flex space-x-4 mb-6">
                <button
                    onClick={() => setFilterStatus('Activo')}
                    className={`px-4 py-2 rounded font-medium ${filterStatus === 'Activo' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'}`}
                >
                    Activos
                </button>
                <button
                    onClick={() => setFilterStatus('Pagado')}
                    className={`px-4 py-2 rounded font-medium ${filterStatus === 'Pagado' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300'}`}
                >
                    Historial (Pagados)
                </button>
            </div>

            {showForm && (
                <div className="bg-white dark:bg-gray-800 p-6 rounded shadow mb-6 transition-colors duration-200">
                    <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Registrar Contrato</h3>
                    <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <select className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.cliente} onChange={e => setFormData({ ...formData, cliente: e.target.value })} required>
                            <option value="">Seleccionar Cliente</option>
                            {clients.map(c => <option key={c.id} value={c.id}>{c.nombres} {c.apellidos}</option>)}
                        </select>
                        <select className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.moto} onChange={e => setFormData({ ...formData, moto: e.target.value })} required>
                            <option value="">Seleccionar Moto</option>
                            {motos.filter(m => m.estado === 'Disponible').map(m => <option key={m.id} value={m.id}>{m.marca} {m.modelo} - {m.placa} (S/ {m.precio})</option>)}
                        </select>
                        <select className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.tipo} onChange={e => setFormData({ ...formData, tipo: e.target.value })}>
                            <option value="Venta">Venta</option>
                            <option value="Alquiler">Alquiler</option>
                        </select>
                        <input placeholder="Monto Inicial" type="number" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.monto_inicial} onChange={e => setFormData({ ...formData, monto_inicial: e.target.value })} required />
                        <input placeholder="Interés %" type="number" step="0.01" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.interes} onChange={e => setFormData({ ...formData, interes: e.target.value })} required />
                        <input placeholder="Cuotas Totales" type="number" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.cuotas_totales} onChange={e => setFormData({ ...formData, cuotas_totales: e.target.value })} required />
                        <input placeholder="Fecha Contrato" type="date" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.fecha_contrato} onChange={e => setFormData({ ...formData, fecha_contrato: e.target.value })} required />
                        <select className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.metodo_pago} onChange={e => setFormData({ ...formData, metodo_pago: e.target.value })}>
                            <option value="Diario">Diario</option>
                            <option value="Semanal">Semanal</option>
                        </select>

                        {calculation && (
                            <div className="md:col-span-2 bg-gray-50 dark:bg-gray-700 p-4 rounded">
                                <p className="dark:text-white"><strong>Restante:</strong> S/ {calculation.restante}</p>
                                <p className="dark:text-white"><strong>Total Deuda:</strong> S/ {calculation.total}</p>
                                <p className="dark:text-white"><strong>Cuota:</strong> S/ {calculation.cuota}</p>
                            </div>
                        )}

                        <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded md:col-span-2 hover:bg-green-700">Guardar</button>
                    </form>
                </div>
            )}

            <div className="bg-white dark:bg-gray-800 rounded shadow overflow-x-auto transition-colors duration-200">
                <table className="w-full">
                    <thead className="bg-gray-50 dark:bg-gray-700">
                        <tr>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">ID</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Cliente</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Moto</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Tipo</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Deuda Total</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                        {filteredContracts.map(contract => (
                            <tr key={contract.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-300">
                                <td className="p-4">{contract.id}</td>
                                <td className="p-4">{clients.find(c => c.id === contract.cliente)?.nombres}</td>
                                <td className="p-4">{motos.find(m => m.id === contract.moto)?.placa}</td>
                                <td className="p-4">{contract.tipo}</td>
                                <td className="p-4">S/ {contract.monto_total_deuda}</td>
                                <td className="p-4 flex space-x-2">
                                    <button onClick={() => handleOpenCalendar(contract)} className="text-green-600 hover:text-green-800 dark:text-green-400 dark:hover:text-green-300" title="Ver Calendario">
                                        <Calendar className="w-5 h-5" />
                                    </button>
                                    <button onClick={() => handleDownloadPdf(contract, 'schedule')} className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300" title="Descargar Calendario">
                                        <FileText className="w-5 h-5" />
                                    </button>
                                    <button onClick={() => handleDownloadPdf(contract, 'contract')} className="text-purple-600 hover:text-purple-800 dark:text-purple-400 dark:hover:text-purple-300" title="Descargar Contrato Legal">
                                        <Download className="w-5 h-5" />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <PaymentCalendarModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                title={modalTitle}
                installments={selectedContractInstallments}
                onPay={handlePaymentSubmit}
            />

            <ConfirmationModal
                isOpen={isConfirmOpen}
                onClose={() => setIsConfirmOpen(false)}
                onConfirm={confirmAction}
                title={confirmTitle}
                message={confirmMessage}
                isDestructive={confirmDestructive}
            />
        </div>
    );
};

export default Contracts;
