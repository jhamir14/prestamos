import React, { useEffect, useState } from 'react';
import api from '../api';
import { Plus, ShoppingCart, Calendar, Trash2, Eye, X, Download } from 'lucide-react';
import PaymentCalendarModal from '../components/PaymentCalendarModal';
import ConfirmationModal from '../components/ConfirmationModal';

const DeviceSales = () => {
    // ... (existing state)
    const [sales, setSales] = useState([]);
    const [devices, setDevices] = useState([]);
    const [clients, setClients] = useState([]);
    const [showForm, setShowForm] = useState(false);

    const getLocalDate = () => {
        const d = new Date();
        const offset = d.getTimezoneOffset() * 60000;
        return (new Date(d - offset)).toISOString().slice(0, 10);
    };

    const [formData, setFormData] = useState({
        device: '',
        cliente: '',
        tipo: 'Contado', // Contado, Credito
        fecha_venta: getLocalDate(),
        monto_inicial: '',
        interes: 10.00,
        cuotas_totales: 1,
        metodo_pago: 'Diario',
        sistema_operativo: 'Android',
        icloud_email: '',
        icloud_password: ''
    });

    const [calculation, setCalculation] = useState(null);

    // Modal State
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedInstallments, setSelectedInstallments] = useState([]);
    const [modalTitle, setModalTitle] = useState('');

    // View Details Modal State
    const [isViewModalOpen, setIsViewModalOpen] = useState(false);
    const [selectedSaleForView, setSelectedSaleForView] = useState(null);

    // Confirmation
    const [isConfirmOpen, setIsConfirmOpen] = useState(false);
    const [confirmAction, setConfirmAction] = useState(null);
    const [confirmMessage, setConfirmMessage] = useState('');

    useEffect(() => {
        fetchSales();
        fetchDevices();
        fetchClients();
    }, []);

    const fetchSales = () => {
        api.get('/devices/sales/').then(res => setSales(res.data));
    };

    const fetchDevices = () => {
        api.get('/devices/devices/').then(res => setDevices(res.data.filter(d => d.estado === 'Disponible')));
    };

    const fetchClients = () => {
        api.get('/users/clients/').then(res => setClients(res.data));
    };

    const calculate = () => {
        if (formData.tipo === 'Contado') {
            setCalculation(null);
            return;
        }

        const selectedDevice = devices.find(d => d.id === parseInt(formData.device));
        if (!selectedDevice || !formData.monto_inicial || !formData.cuotas_totales) return;

        const restante = parseFloat(selectedDevice.precio) - parseFloat(formData.monto_inicial);
        if (restante < 0) return;

        const total_deuda = restante * (1 + (parseFloat(formData.interes) / 100));
        const cuota = total_deuda / parseInt(formData.cuotas_totales);

        setCalculation({
            precio_moto: parseFloat(selectedDevice.precio).toFixed(2),
            restante: restante.toFixed(2),
            total_deuda: total_deuda.toFixed(2),
            cuota: cuota.toFixed(2)
        });
    };

    useEffect(() => {
        calculate();
    }, [formData.device, formData.monto_inicial, formData.interes, formData.cuotas_totales, formData.tipo]);

    const handleSubmit = (e) => {
        e.preventDefault();
        api.post('/devices/sales/', formData)
            .then(() => {
                setShowForm(false);
                fetchSales();
                fetchDevices(); // Refresh inventory
                setFormData({
                    device: '', cliente: '', tipo: 'Contado', fecha_venta: getLocalDate(),
                    monto_inicial: '', interes: 10.00, cuotas_totales: 1, metodo_pago: 'Diario',
                    sistema_operativo: 'Android', icloud_email: '', icloud_password: ''
                });
                setCalculation(null);
            })
            .catch(err => alert('Error saving sale: ' + JSON.stringify(err.response.data)));
    };

    const handleOpenCalendar = async (sale) => {
        if (sale.tipo === 'Contado') return;
        try {
            const res = await api.get(`/devices/sales/${sale.id}/`);
            setSelectedInstallments(res.data.installments);
            setModalTitle(`Plan de Pagos - ${sale.device_details.modelo}`);
            setIsModalOpen(true);
        } catch (err) {
            console.error(err);
        }
    };

    const handleViewClick = (sale) => {
        setSelectedSaleForView(sale);
        setIsViewModalOpen(true);
    };

    const handlePaymentSubmit = async (installment, amount, method) => {
        try {
            await api.post(`/devices/installments/${installment.id}/pay/`, {
                monto: amount,
                metodo_pago: method
            });
            // Refresh
            const res = await api.get(`/devices/sales/${installment.sale}/`);
            setSelectedInstallments(res.data.installments);
            fetchSales();
        } catch (err) {
            console.error(err);
            alert('Error processing payment');
        }
    };

    const handleDownloadPDF = async (sale) => {
        try {
            const response = await api.get(`/devices/sales/${sale.id}/download_schedule_pdf/`, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `${sale.cliente}_venta_celular.pdf`); // Fallback name, backend header usually takes precedence
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error('Error downloading PDF:', err);
            alert('Error al descargar el PDF');
        }
    };

    const handleDeleteClick = (id) => {
        setConfirmMessage('¿Estás seguro de eliminar esta venta?');
        setConfirmAction(() => () => deleteSale(id));
        setIsConfirmOpen(true);
    };

    const deleteSale = async (id) => {
        try {
            await api.delete(`/devices/sales/${id}/`);
            fetchSales();
            fetchDevices();
        } catch (err) {
            console.error(err);
            alert('Error deleting sale');
        }
    };

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-3xl font-bold text-gray-800 dark:text-white">Ventas Celulares</h2>
                <button onClick={() => setShowForm(!showForm)} className="bg-blue-600 text-white px-4 py-2 rounded flex items-center hover:bg-blue-700">
                    <Plus className="w-4 h-4 mr-2" /> Nueva Venta
                </button>
            </div>

            {showForm && (
                <div className="bg-white dark:bg-gray-800 p-6 rounded shadow mb-6 transition-colors duration-200">
                    <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Registrar Venta</h3>
                    <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <select className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.device} onChange={e => setFormData({ ...formData, device: e.target.value })} required>
                            <option value="">Seleccionar Dispositivo</option>
                            {devices.map(d => <option key={d.id} value={d.id}>{d.marca} {d.modelo} - S/ {d.precio}</option>)}
                        </select>
                        <select className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.cliente} onChange={e => setFormData({ ...formData, cliente: e.target.value })} required>
                            <option value="">Seleccionar Cliente</option>
                            {clients.map(c => <option key={c.id} value={c.id}>{c.nombres} {c.apellidos}</option>)}
                        </select>
                        <select className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.tipo} onChange={e => setFormData({ ...formData, tipo: e.target.value })}>
                            <option value="Contado">Contado</option>
                            <option value="Credito">Crédito</option>
                        </select>

                        <input type="date" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.fecha_venta} onChange={e => setFormData({ ...formData, fecha_venta: e.target.value })} required />

                        <select className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.sistema_operativo} onChange={e => setFormData({ ...formData, sistema_operativo: e.target.value })}>
                            <option value="Android">Android</option>
                            <option value="IOS">IOS</option>
                        </select>

                        {formData.sistema_operativo === 'IOS' && (
                            <>
                                <input placeholder="iCloud Email" type="email" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.icloud_email} onChange={e => setFormData({ ...formData, icloud_email: e.target.value })} />
                                <input placeholder="iCloud Contraseña" type="text" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.icloud_password} onChange={e => setFormData({ ...formData, icloud_password: e.target.value })} />
                            </>
                        )}

                        {formData.tipo === 'Credito' && (
                            <>
                                <input placeholder="Inicial" type="number" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.monto_inicial} onChange={e => setFormData({ ...formData, monto_inicial: e.target.value })} required />
                                <input placeholder="Interés %" type="number" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.interes} onChange={e => setFormData({ ...formData, interes: e.target.value })} required />
                                <input placeholder="Cuotas" type="number" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.cuotas_totales} onChange={e => setFormData({ ...formData, cuotas_totales: e.target.value })} required />
                                <select className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.metodo_pago} onChange={e => setFormData({ ...formData, metodo_pago: e.target.value })}>
                                    <option value="Diario">Diario</option>
                                    <option value="Semanal">Semanal</option>
                                </select>
                            </>
                        )}

                        {calculation && (
                            <div className="md:col-span-2 bg-gray-50 dark:bg-gray-700 p-4 rounded text-gray-900 dark:text-white">
                                <p><strong>Precio Venta:</strong> S/ {calculation.precio_moto}</p>
                                <p><strong>Restante:</strong> S/ {calculation.restante}</p>
                                <p><strong>Total con Interés:</strong> S/ {calculation.total_deuda}</p>
                                <p><strong>Monto Cuota:</strong> S/ {calculation.cuota}</p>
                            </div>
                        )}

                        <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded md:col-span-2 hover:bg-green-700">Registrar Venta</button>
                    </form>
                </div>
            )}

            <div className="bg-white dark:bg-gray-800 rounded shadow overflow-x-auto transition-colors duration-200">
                <table className="w-full">
                    <thead className="bg-gray-50 dark:bg-gray-700">
                        <tr>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Fecha</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Dispositivo</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Cliente</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Tipo</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Estado</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                        {sales.map(sale => (
                            <tr key={sale.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-300">
                                <td className="p-4">{sale.fecha_venta}</td>
                                <td className="p-4">{sale.device_details?.modelo}</td>
                                <td className="p-4">{clients.find(c => c.id === sale.cliente)?.nombres}</td>
                                <td className="p-4">{sale.tipo}</td>
                                <td className="p-4">
                                    <span className={`px-2 py-1 rounded text-sm ${sale.estado === 'Activo' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'}`}>
                                        {sale.estado}
                                    </span>
                                </td>
                                <td className="p-4 flex space-x-2">
                                    <button onClick={() => handleViewClick(sale)} className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300">
                                        <Eye className="w-5 h-5" />
                                    </button>
                                    {sale.tipo === 'Credito' && (
                                        <>
                                            <button onClick={() => handleOpenCalendar(sale)} className="text-green-600 hover:text-green-800 dark:text-green-400 dark:hover:text-green-300" title="Ver Calendario">
                                                <Calendar className="w-5 h-5" />
                                            </button>
                                            <button onClick={() => handleDownloadPDF(sale)} className="text-purple-600 hover:text-purple-800 dark:text-purple-400 dark:hover:text-purple-300" title="Descargar PDF">
                                                <Download className="w-5 h-5" />
                                            </button>
                                        </>
                                    )}
                                    <button onClick={() => handleDeleteClick(sale.id)} className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300">
                                        <Trash2 className="w-5 h-5" />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {/* View Details Modal */}
            {isViewModalOpen && selectedSaleForView && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl max-w-md w-full relative">
                        <button
                            onClick={() => setIsViewModalOpen(false)}
                            className="absolute top-4 right-4 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
                        >
                            <X size={24} />
                        </button>
                        <h3 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Detalles de Venta</h3>

                        <div className="space-y-3 text-gray-700 dark:text-gray-300">
                            <p><strong>Dispositivo:</strong> {selectedSaleForView.device_details?.modelo}</p>
                            <p><strong>Cliente:</strong> {clients.find(c => c.id === selectedSaleForView.cliente)?.nombres} {clients.find(c => c.id === selectedSaleForView.cliente)?.apellidos}</p>
                            <p><strong>Fecha Venta:</strong> {selectedSaleForView.fecha_venta}</p>
                            <p><strong>Tipo:</strong> {selectedSaleForView.tipo}</p>
                            <p><strong>Estado:</strong> {selectedSaleForView.estado}</p>

                            <hr className="dark:border-gray-700" />

                            <p><strong>SO:</strong> {selectedSaleForView.sistema_operativo}</p>
                            {selectedSaleForView.sistema_operativo === 'IOS' && (
                                <>
                                    <p><strong>iCloud Email:</strong> {selectedSaleForView.icloud_email || 'N/A'}</p>
                                    <p><strong>iCloud Password:</strong> {selectedSaleForView.icloud_password || 'N/A'}</p>
                                </>
                            )}

                            {selectedSaleForView.tipo === 'Credito' && (
                                <>
                                    <hr className="dark:border-gray-700" />
                                    <p><strong>Monto Inicial:</strong> S/ {selectedSaleForView.monto_inicial}</p>
                                    <p><strong>Interés:</strong> {selectedSaleForView.interes}%</p>
                                    <p><strong>Total Deuda:</strong> S/ {selectedSaleForView.monto_total_deuda}</p>
                                    <p><strong>Cuotas:</strong> {selectedSaleForView.cuotas_totales} ({selectedSaleForView.metodo_pago})</p>
                                </>
                            )}
                        </div>
                    </div>
                </div>
            )}

            <PaymentCalendarModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                title={modalTitle}
                installments={selectedInstallments}
                onPay={handlePaymentSubmit}
            />

            <ConfirmationModal
                isOpen={isConfirmOpen}
                onClose={() => setIsConfirmOpen(false)}
                onConfirm={confirmAction}
                message={confirmMessage}
                isDestructive={true}
            />
        </div>
    );
};

export default DeviceSales;
