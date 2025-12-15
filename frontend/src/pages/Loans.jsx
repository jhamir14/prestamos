import React, { useEffect, useState } from 'react';
import api from '../api';
import { Plus, Download, Calendar, Trash2 } from 'lucide-react';
import PaymentCalendarModal from '../components/PaymentCalendarModal';
import ConfirmationModal from '../components/ConfirmationModal';
import SearchableSelect from '../components/SearchableSelect';

const Loans = () => {
    const [loans, setLoans] = useState([]);
    const [clients, setClients] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const getLocalDate = () => {
        const d = new Date();
        const offset = d.getTimezoneOffset() * 60000;
        const localISOTime = (new Date(d - offset)).toISOString().slice(0, 10);
        return localISOTime;
    };

    const [formData, setFormData] = useState({
        cliente: '', monto_prestado: '', interes: 10.00, cuotas_totales: '', frecuencia: 'Diario', fecha_inicio: getLocalDate()
    });
    const [calculation, setCalculation] = useState(null);

    // Modal State
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedLoanInstallments, setSelectedLoanInstallments] = useState([]);
    const [modalTitle, setModalTitle] = useState('');

    // Confirmation Modal State
    const [isConfirmOpen, setIsConfirmOpen] = useState(false);
    const [confirmAction, setConfirmAction] = useState(null);
    const [confirmMessage, setConfirmMessage] = useState('');
    const [confirmTitle, setConfirmTitle] = useState('');
    const [confirmDestructive, setConfirmDestructive] = useState(false);

    useEffect(() => {
        fetchLoans();
        fetchClients();
    }, []);

    const fetchLoans = () => {
        api.get('/loans/loans/')
            .then(res => setLoans(res.data))
            .catch(err => console.error(err));
    };

    const fetchClients = () => {
        api.get('/users/clients/').then(res => setClients(res.data));
    };

    const calculate = () => {
        if (!formData.monto_prestado || !formData.cuotas_totales) return;

        const total = parseFloat(formData.monto_prestado) * (1 + (parseFloat(formData.interes) / 100));
        const cuota = total / parseInt(formData.cuotas_totales);

        setCalculation({
            total: total.toFixed(2),
            cuota: cuota.toFixed(2)
        });
    };

    useEffect(() => {
        calculate();
    }, [formData.monto_prestado, formData.interes, formData.cuotas_totales]);

    const handleSubmit = (e) => {
        e.preventDefault();
        api.post('/loans/loans/', formData)
            .then(() => {
                setShowForm(false);
                fetchLoans();
                setFormData({ cliente: '', monto_prestado: '', interes: 10.00, cuotas_totales: '', frecuencia: 'Diario', fecha_inicio: getLocalDate() });
                setCalculation(null);
            })
            .catch(err => alert('Error saving loan: ' + JSON.stringify(err.response.data)));
    };

    const handleDeleteClick = (id) => {
        setConfirmTitle('Eliminar Préstamo');
        setConfirmMessage('¿Estás seguro de que deseas eliminar este préstamo? Esta acción no se puede deshacer.');
        setConfirmDestructive(true);
        setConfirmAction(() => () => deleteLoan(id));
        setIsConfirmOpen(true);
    };

    const deleteLoan = async (id) => {
        try {
            await api.delete(`/loans/loans/${id}/`);
            fetchLoans();
        } catch (err) {
            console.error(err);
            alert('Error deleting loan');
        }
    };

    const handleDownloadPdf = async (loan) => {
        try {
            const response = await api.get(`/loans/loans/${loan.id}/download_pdf/`, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;

            const client = clients.find(c => c.id === loan.cliente);
            const clientName = client ? `${client.nombres}_${client.apellidos}`.replace(/ /g, '_') : 'cliente';

            link.setAttribute('download', `prestamo_${clientName}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error('Error downloading PDF:', err);
            alert('Error downloading PDF');
        }
    };

    const confirmDownload = (loan) => {
        const client = clients.find(c => c.id === loan.cliente);
        const clientName = client ? `${client.nombres}_${client.apellidos}`.replace(/ /g, '_') : 'cliente';
        const pdfName = `prestamo_${clientName}.pdf`;

        setConfirmTitle('Confirmar Descarga');
        setConfirmMessage(`¿Deseas descargar el pdf con el nombre ${pdfName}?`);
        setConfirmDestructive(false);
        setConfirmAction(() => () => handleDownloadPdf(loan));
        setIsConfirmOpen(true);
    };

    const handleOpenCalendar = async (loan) => {
        try {
            const res = await api.get(`/loans/loans/${loan.id}/`);
            setSelectedLoanInstallments(res.data.cuotas);
            setModalTitle(`Calendario - Préstamo #${loan.id}`);
            setIsModalOpen(true);
        } catch (err) {
            console.error(err);
            alert('Error fetching installments');
        }
    };

    const [filterStatus, setFilterStatus] = useState('Activo');

    const filteredLoans = loans.filter(loan => loan.estado === filterStatus);

    const handlePaymentSubmit = async (installment, amount, method) => {
        try {
            await api.post(`/loans/installments/${installment.id}/pay/`, {
                monto: amount,
                metodo_pago: method
            });

            // Refresh modal data
            const res = await api.get(`/loans/loans/${installment.prestamo}/`);
            setSelectedLoanInstallments(res.data.cuotas);

            // Refresh main list
            fetchLoans();
        } catch (err) {
            console.error(err);
            alert('Error processing payment');
        }
    };

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-3xl font-bold text-gray-800 dark:text-white">Préstamos</h2>
                <button onClick={() => setShowForm(!showForm)} className="bg-blue-600 text-white px-4 py-2 rounded flex items-center hover:bg-blue-700">
                    <Plus className="w-4 h-4 mr-2" /> Nuevo Préstamo
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
                    <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Registrar Préstamo</h3>
                    <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="z-50">
                            <SearchableSelect
                                options={clients}
                                value={formData.cliente}
                                onChange={(e) => setFormData({ ...formData, cliente: e.target.value })}
                                placeholder="Seleccionar Cliente"
                            />
                        </div>
                        <input placeholder="Monto Prestado" type="number" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.monto_prestado} onChange={e => setFormData({ ...formData, monto_prestado: e.target.value })} required />
                        <input placeholder="Interés %" type="number" step="0.01" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.interes} onChange={e => setFormData({ ...formData, interes: e.target.value })} required />
                        <input placeholder="Cuotas Totales" type="number" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.cuotas_totales} onChange={e => setFormData({ ...formData, cuotas_totales: e.target.value })} required />
                        <input placeholder="Fecha Inicio" type="date" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.fecha_inicio} onChange={e => setFormData({ ...formData, fecha_inicio: e.target.value })} required />
                        <select className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.frecuencia} onChange={e => setFormData({ ...formData, frecuencia: e.target.value })}>
                            <option value="Diario">Diario</option>
                            <option value="Semanal">Semanal</option>
                        </select>

                        {calculation && (
                            <div className="md:col-span-2 bg-gray-50 dark:bg-gray-700 p-4 rounded">
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
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Monto</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Deuda Total</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Frecuencia</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                        {filteredLoans.map(loan => (
                            <tr key={loan.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-300">
                                <td className="p-4">{loan.id}</td>
                                <td className="p-4">{clients.find(c => c.id === loan.cliente)?.nombres}</td>
                                <td className="p-4">S/ {loan.monto_prestado}</td>
                                <td className="p-4">S/ {loan.monto_total_deuda}</td>
                                <td className="p-4">{loan.frecuencia}</td>
                                <td className="p-4 flex space-x-2">
                                    <button onClick={() => handleOpenCalendar(loan)} className="text-green-600 hover:text-green-800 dark:text-green-400 dark:hover:text-green-300" title="Ver Calendario">
                                        <Calendar className="w-5 h-5" />
                                    </button>
                                    <button onClick={() => confirmDownload(loan)} className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300" title="Descargar PDF">
                                        <Download className="w-5 h-5" />
                                    </button>
                                    <button onClick={() => handleDeleteClick(loan.id)} className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300" title="Eliminar">
                                        <Trash2 className="w-5 h-5" />
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
                installments={selectedLoanInstallments}
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

export default Loans;
