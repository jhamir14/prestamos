import React, { useEffect, useState } from 'react';
import api from '../api';
import { Plus, Smartphone, Trash2, Edit } from 'lucide-react';
import ConfirmationModal from '../components/ConfirmationModal';

const Devices = () => {
    const [devices, setDevices] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const [formData, setFormData] = useState({
        marca: '', modelo: '', precio: '', imei: '', imei2: '', numero_serie: '', color: '', image: null
    });

    const [editingId, setEditingId] = useState(null);

    // Confirmation Modal State
    const [isConfirmOpen, setIsConfirmOpen] = useState(false);
    const [confirmAction, setConfirmAction] = useState(null);
    const [confirmMessage, setConfirmMessage] = useState('');
    const [confirmTitle, setConfirmTitle] = useState('');

    useEffect(() => {
        fetchDevices();
    }, []);

    const fetchDevices = () => {
        api.get('/devices/devices/')
            .then(res => setDevices(res.data))
            .catch(err => console.error(err));
    };

    const handleEdit = (device) => {
        setFormData({
            marca: device.marca,
            modelo: device.modelo,
            precio: device.precio,
            imei: device.imei,
            imei2: device.imei2 || '',
            numero_serie: device.numero_serie,
            color: device.color,
            image: null // Don't populate file input
        });
        setEditingId(device.id);
        setShowForm(true);
    };

    const handleFileChange = (e) => {
        setFormData({ ...formData, image: e.target.files[0] });
    };

    const handleSubmit = (e) => {
        e.preventDefault();

        const data = new FormData();
        data.append('marca', formData.marca);
        data.append('modelo', formData.modelo);
        data.append('precio', formData.precio);
        data.append('imei', formData.imei);
        if (formData.imei2) data.append('imei2', formData.imei2);
        data.append('numero_serie', formData.numero_serie);
        data.append('color', formData.color);
        if (formData.image) data.append('image', formData.image);

        if (editingId) {
            api.patch(`/devices/devices/${editingId}/`, data, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })
                .then(() => {
                    setShowForm(false);
                    fetchDevices();
                    resetForm();
                })
                .catch(err => alert('Error updating device: ' + JSON.stringify(err.response.data)));
        } else {
            api.post('/devices/devices/', data, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })
                .then(() => {
                    setShowForm(false);
                    fetchDevices();
                    resetForm();
                })
                .catch(err => alert('Error saving device: ' + JSON.stringify(err.response.data)));
        }
    };

    const resetForm = () => {
        setFormData({ marca: '', modelo: '', precio: '', imei: '', imei2: '', numero_serie: '', color: '', image: null });
        setEditingId(null);
    };

    const handleDeleteClick = (id) => {
        setConfirmTitle('Eliminar Dispositivo');
        setConfirmMessage('¿Estás seguro de que deseas eliminar este dispositivo? Esta acción no se puede deshacer.');
        setConfirmAction(() => () => deleteDevice(id));
        setIsConfirmOpen(true);
    };

    const deleteDevice = async (id) => {
        try {
            await api.delete(`/devices/devices/${id}/`);
            fetchDevices();
        } catch (err) {
            console.error(err);
            alert('Error deleting device');
        }
    };

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-3xl font-bold text-gray-800 dark:text-white">Dispositivos</h2>
                <button onClick={() => { setShowForm(!showForm); resetForm(); }} className="bg-blue-600 text-white px-4 py-2 rounded flex items-center hover:bg-blue-700">
                    <Plus className="w-4 h-4 mr-2" /> {showForm ? 'Cerrar' : 'Nuevo Dispositivo'}
                </button>
            </div>

            {showForm && (
                <div className="bg-white dark:bg-gray-800 p-6 rounded shadow mb-6 transition-colors duration-200">
                    <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">{editingId ? 'Editar Dispositivo' : 'Registrar Dispositivo'}</h3>
                    <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <input placeholder="Marca" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.marca} onChange={e => setFormData({ ...formData, marca: e.target.value })} required />
                        <input placeholder="Modelo" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.modelo} onChange={e => setFormData({ ...formData, modelo: e.target.value })} required />
                        <input placeholder="Precio" type="number" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.precio} onChange={e => setFormData({ ...formData, precio: e.target.value })} required />
                        <input placeholder="IMEI" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.imei} onChange={e => setFormData({ ...formData, imei: e.target.value })} required />
                        <input placeholder="IMEI 2 (Opcional)" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.imei2} onChange={e => setFormData({ ...formData, imei2: e.target.value })} />
                        <input placeholder="N° Serie" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.numero_serie} onChange={e => setFormData({ ...formData, numero_serie: e.target.value })} required />
                        <input placeholder="Color" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.color} onChange={e => setFormData({ ...formData, color: e.target.value })} required />

                        <div className="md:col-span-1">
                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Imagen</label>
                            <input type="file" accept="image/*" onChange={handleFileChange} className="border p-2 rounded w-full dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
                        </div>

                        <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded md:col-span-3 hover:bg-green-700">{editingId ? 'Actualizar' : 'Guardar'}</button>
                    </form>
                </div>
            )}

            <div className="bg-white dark:bg-gray-800 rounded shadow overflow-x-auto transition-colors duration-200">
                <table className="w-full">
                    <thead className="bg-gray-50 dark:bg-gray-700">
                        <tr>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Imagen</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Dispositivo</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">IMEI / Serie</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Precio</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Estado</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                        {devices.map(dev => (
                            <tr key={dev.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-300">
                                <td className="p-4">
                                    {dev.image ? (
                                        <img src={dev.image} alt={dev.modelo} className="w-16 h-16 object-cover rounded" />
                                    ) : (
                                        <Smartphone className="w-10 h-10 text-gray-400" />
                                    )}
                                </td>
                                <td className="p-4">
                                    <div className="font-bold">{dev.marca} {dev.modelo}</div>
                                    <div className="text-sm text-gray-500 dark:text-gray-400">{dev.color}</div>
                                </td>
                                <td className="p-4">
                                    <div>IMEI: {dev.imei}</div>
                                    <div className="text-xs">SN: {dev.numero_serie}</div>
                                </td>
                                <td className="p-4 text-green-600 font-bold">S/ {dev.precio}</td>
                                <td className="p-4">
                                    <span className={`px-2 py-1 rounded text-sm ${dev.estado === 'Disponible' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'}`}>
                                        {dev.estado}
                                    </span>
                                </td>
                                <td className="p-4">
                                    <div className="flex space-x-2">
                                        <button onClick={() => handleEdit(dev)} className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300" title="Editar">
                                            <Edit className="w-5 h-5" />
                                        </button>
                                        <button onClick={() => handleDeleteClick(dev.id)} className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300" title="Eliminar">
                                            <Trash2 className="w-5 h-5" />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <ConfirmationModal
                isOpen={isConfirmOpen}
                onClose={() => setIsConfirmOpen(false)}
                onConfirm={confirmAction}
                title={confirmTitle}
                message={confirmMessage}
                confirmText="Eliminar"
                isDestructive={true}
            />
        </div>
    );
};

export default Devices;
