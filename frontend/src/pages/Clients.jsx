import React, { useEffect, useState } from 'react';
import api from '../api';
import { Plus, Search } from 'lucide-react';
import ConfirmationModal from '../components/ConfirmationModal';

const Clients = () => {
    const [clients, setClients] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [showForm, setShowForm] = useState(false);

    // ... existing state ...
    const [formData, setFormData] = useState({
        nombres: '', apellidos: '', dni: '', email: '', domicilio: '', telefono: ''
    });

    const [editingId, setEditingId] = useState(null);

    // Confirmation Modal State
    const [isConfirmOpen, setIsConfirmOpen] = useState(false);
    const [confirmAction, setConfirmAction] = useState(null);
    const [confirmMessage, setConfirmMessage] = useState('');
    const [confirmTitle, setConfirmTitle] = useState('');

    useEffect(() => {
        fetchClients();
    }, []);

    const fetchClients = () => {
        api.get('/users/clients/')
            .then(res => setClients(res.data))
            .catch(err => console.error(err));
    };

    const handleEdit = (client) => {
        setFormData({
            nombres: client.nombres,
            apellidos: client.apellidos,
            dni: client.dni,
            email: client.email,
            domicilio: client.domicilio,
            telefono: client.telefono
        });
        setEditingId(client.id);
        setShowForm(true);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (editingId) {
            api.put(`/users/clients/${editingId}/`, formData)
                .then(() => {
                    setShowForm(false);
                    fetchClients();
                    setFormData({ nombres: '', apellidos: '', dni: '', email: '', domicilio: '', telefono: '' });
                    setEditingId(null);
                })
                .catch(err => alert('Error updating client: ' + JSON.stringify(err.response.data)));
        } else {
            api.post('/users/clients/', formData)
                .then(() => {
                    setShowForm(false);
                    fetchClients();
                    setFormData({ nombres: '', apellidos: '', dni: '', email: '', domicilio: '', telefono: '' });
                })
                .catch(err => alert('Error saving client: ' + JSON.stringify(err.response.data)));
        }
    };

    const handleDeleteClick = (id) => {
        setConfirmTitle('Eliminar Cliente');
        setConfirmMessage('¿Estás seguro de que deseas eliminar este cliente? Esta acción no se puede deshacer.');
        setConfirmAction(() => () => deleteClient(id));
        setIsConfirmOpen(true);
    };

    const deleteClient = async (id) => {
        try {
            await api.delete(`/users/clients/${id}/`);
            fetchClients();
        } catch (err) {
            console.error(err);
            alert('Error deleting client');
        }
    };

    const filteredClients = clients.filter(client =>
        client.nombres.toLowerCase().includes(searchTerm.toLowerCase()) ||
        client.apellidos.toLowerCase().includes(searchTerm.toLowerCase()) ||
        client.dni.includes(searchTerm)
    );

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-3xl font-bold text-gray-800 dark:text-white">Clientes</h2>
                <div className="flex space-x-2">
                    <div className="relative">
                        <input
                            type="text"
                            placeholder="Buscar cliente..."
                            className="border p-2 pl-8 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                        <Search className="w-4 h-4 absolute left-2.5 top-3 text-gray-500" />
                    </div>
                    <button onClick={() => { setShowForm(!showForm); setEditingId(null); setFormData({ nombres: '', apellidos: '', dni: '', email: '', domicilio: '', telefono: '' }); }} className="bg-blue-600 text-white px-4 py-2 rounded flex items-center hover:bg-blue-700">
                        <Plus className="w-4 h-4 mr-2" /> {showForm ? 'Cerrar' : 'Nuevo Cliente'}
                    </button>
                </div>
            </div>

            {showForm && (
                <div className="bg-white dark:bg-gray-800 p-6 rounded shadow mb-6 transition-colors duration-200">
                    <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">{editingId ? 'Editar Cliente' : 'Registrar Cliente'}</h3>
                    <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <input placeholder="Nombres" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.nombres} onChange={e => setFormData({ ...formData, nombres: e.target.value })} required />
                        <input placeholder="Apellidos" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.apellidos} onChange={e => setFormData({ ...formData, apellidos: e.target.value })} required />
                        <input placeholder="DNI" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.dni} onChange={e => setFormData({ ...formData, dni: e.target.value })} required />
                        <input placeholder="Email (Gmail)" type="email" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.email} onChange={e => setFormData({ ...formData, email: e.target.value })} required />
                        <input placeholder="Teléfono" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.telefono} onChange={e => setFormData({ ...formData, telefono: e.target.value })} />
                        <textarea placeholder="Domicilio" className="border p-2 rounded md:col-span-2 dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.domicilio} onChange={e => setFormData({ ...formData, domicilio: e.target.value })} />
                        <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded md:col-span-2 hover:bg-green-700">{editingId ? 'Actualizar' : 'Guardar'}</button>
                    </form>
                </div>
            )}

            <div className="bg-white dark:bg-gray-800 rounded shadow overflow-x-auto transition-colors duration-200">
                <table className="w-full">
                    <thead className="bg-gray-50 dark:bg-gray-700">
                        <tr>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Nombre</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">DNI</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Email</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Teléfono</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Acciones</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                        {filteredClients.map(client => (
                            <tr key={client.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-300">
                                <td className="p-4">{client.nombres} {client.apellidos}</td>
                                <td className="p-4">{client.dni}</td>
                                <td className="p-4">{client.email}</td>
                                <td className="p-4">{client.telefono}</td>
                                <td className="p-4">
                                    <button onClick={() => handleEdit(client)} className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 font-medium mr-2">Editar</button>
                                    <button onClick={() => handleDeleteClick(client.id)} className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 font-medium">Eliminar</button>
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

export default Clients;
