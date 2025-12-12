import React, { useEffect, useState } from 'react';
import api from '../api';
import { Plus } from 'lucide-react';
import ConfirmationModal from '../components/ConfirmationModal';

const Motos = () => {
    const [motos, setMotos] = useState([]);
    const [showForm, setShowForm] = useState(false);
    const [formData, setFormData] = useState({
        placa: '', marca: '', modelo: '', color: '', numero_motor: '', numero_serie: '', anio: '', precio: '', condicion: '0km', estado: 'Disponible'
    });

    const [editingId, setEditingId] = useState(null);

    // Confirmation Modal State
    const [isConfirmOpen, setIsConfirmOpen] = useState(false);
    const [confirmAction, setConfirmAction] = useState(null);
    const [confirmMessage, setConfirmMessage] = useState('');
    const [confirmTitle, setConfirmTitle] = useState('');

    useEffect(() => {
        fetchMotos();
    }, []);

    const fetchMotos = () => {
        api.get('/inventory/motos/')
            .then(res => setMotos(res.data))
            .catch(err => console.error(err));
    };

    const handleEdit = (moto) => {
        setFormData({
            placa: moto.placa,
            marca: moto.marca,
            modelo: moto.modelo,
            color: moto.color,
            numero_motor: moto.numero_motor,
            numero_serie: moto.numero_serie,
            anio: moto.anio,
            precio: moto.precio,
            condicion: moto.condicion,
            estado: moto.estado,
            image: null
        });
        setEditingId(moto.id);
        setShowForm(true);
    };

    const handleFileChange = (e) => {
        setFormData({ ...formData, image: e.target.files[0] });
    };

    const handleSubmit = (e) => {
        e.preventDefault();

        const data = new FormData();
        data.append('placa', formData.placa);
        data.append('marca', formData.marca);
        data.append('modelo', formData.modelo);
        data.append('color', formData.color);
        data.append('numero_motor', formData.numero_motor);
        data.append('numero_serie', formData.numero_serie);
        data.append('anio', formData.anio);
        data.append('precio', formData.precio);
        data.append('condicion', formData.condicion);
        data.append('estado', formData.estado);
        if (formData.image) data.append('image', formData.image);

        if (editingId) {
            api.patch(`/inventory/motos/${editingId}/`, data, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })
                .then(() => {
                    setShowForm(false);
                    fetchMotos();
                    resetForm();
                })
                .catch(err => alert('Error updating moto: ' + JSON.stringify(err.response.data)));
        } else {
            api.post('/inventory/motos/', data, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })
                .then(() => {
                    setShowForm(false);
                    fetchMotos();
                    resetForm();
                })
                .catch(err => alert('Error saving moto: ' + JSON.stringify(err.response.data)));
        }
    };

    const resetForm = () => {
        setFormData({ placa: '', marca: '', modelo: '', color: '', numero_motor: '', numero_serie: '', anio: '', precio: '', condicion: '0km', estado: 'Disponible', image: null });
        setEditingId(null);
    };

    const handleDeleteClick = (id) => {
        setConfirmTitle('Eliminar Moto');
        setConfirmMessage('¿Estás seguro de que deseas eliminar esta moto? Esta acción no se puede deshacer.');
        setConfirmAction(() => () => deleteMoto(id));
        setIsConfirmOpen(true);
    };

    const deleteMoto = async (id) => {
        try {
            await api.delete(`/inventory/motos/${id}/`);
            fetchMotos();
        } catch (err) {
            console.error(err);
            alert('Error deleting moto');
        }
    };

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-3xl font-bold text-gray-800 dark:text-white">Motos</h2>
                <button onClick={() => { setShowForm(!showForm); resetForm(); }} className="bg-blue-600 text-white px-4 py-2 rounded flex items-center hover:bg-blue-700">
                    <Plus className="w-4 h-4 mr-2" /> {showForm ? 'Cerrar' : 'Nueva Moto'}
                </button>
            </div>

            {showForm && (
                <div className="bg-white dark:bg-gray-800 p-6 rounded shadow mb-6 transition-colors duration-200">
                    <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">{editingId ? 'Editar Moto' : 'Registrar Moto'}</h3>
                    <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <input placeholder="Placa" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.placa} onChange={e => setFormData({ ...formData, placa: e.target.value })} required />
                        <input placeholder="Marca" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.marca} onChange={e => setFormData({ ...formData, marca: e.target.value })} required />
                        <input placeholder="Modelo" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.modelo} onChange={e => setFormData({ ...formData, modelo: e.target.value })} required />
                        <input placeholder="Color" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.color} onChange={e => setFormData({ ...formData, color: e.target.value })} required />
                        <input placeholder="N° Motor" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.numero_motor} onChange={e => setFormData({ ...formData, numero_motor: e.target.value })} required />
                        <input placeholder="N° Serie" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.numero_serie} onChange={e => setFormData({ ...formData, numero_serie: e.target.value })} required />
                        <input placeholder="Año" type="number" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.anio} onChange={e => setFormData({ ...formData, anio: e.target.value })} required />
                        <input placeholder="Precio" type="number" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.precio} onChange={e => setFormData({ ...formData, precio: e.target.value })} required />
                        <select className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.condicion} onChange={e => setFormData({ ...formData, condicion: e.target.value })}>
                            <option value="0km">0km</option>
                            <option value="Segunda">Segunda</option>
                        </select>

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
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Placa</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Marca/Modelo</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Precio</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Estado</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                        {motos.map(moto => (
                            <tr key={moto.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-300">
                                <td className="p-4">
                                    {moto.image ? (
                                        <img src={moto.image} alt={moto.modelo} className="w-16 h-16 object-cover rounded" />
                                    ) : (
                                        <div className="w-16 h-16 bg-gray-200 rounded flex items-center justify-center text-xs text-gray-500">No img</div>
                                    )}
                                </td>
                                <td className="p-4">{moto.placa}</td>
                                <td className="p-4">{moto.marca} {moto.modelo}</td>
                                <td className="p-4">S/ {moto.precio}</td>
                                <td className="p-4">
                                    <span className={`px-2 py-1 rounded text-sm ${moto.estado === 'Disponible' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'}`}>
                                        {moto.estado}
                                    </span>
                                </td>
                                <td className="p-4">
                                    <button onClick={() => handleEdit(moto)} className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 font-medium mr-2">Editar</button>
                                    <button onClick={() => handleDeleteClick(moto.id)} className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 font-medium">Eliminar</button>
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

export default Motos;
