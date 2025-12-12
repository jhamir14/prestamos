import React, { useEffect, useState } from 'react';
import api from '../api';
import { Plus, Shield } from 'lucide-react';
import ConfirmationModal from '../components/ConfirmationModal';

const Admins = () => {
    const [admins, setAdmins] = useState([]);
    const [currentUser, setCurrentUser] = useState(null);
    const [showForm, setShowForm] = useState(false);
    const [formData, setFormData] = useState({
        username: '', email: '', password: '', role: 'admin'
    });

    const [editingId, setEditingId] = useState(null);

    // Confirmation Modal State
    const [isConfirmOpen, setIsConfirmOpen] = useState(false);
    const [confirmAction, setConfirmAction] = useState(null);
    const [confirmMessage, setConfirmMessage] = useState('');
    const [confirmTitle, setConfirmTitle] = useState('');

    useEffect(() => {
        fetchCurrentUser();
        fetchAdmins();
    }, []);

    const fetchCurrentUser = () => {
        api.get('/users/me/')
            .then(res => setCurrentUser(res.data))
            .catch(err => console.error(err));
    };

    const fetchAdmins = () => {
        api.get('/users/admins/')
            .then(res => setAdmins(res.data))
            .catch(err => console.error(err));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (editingId) {
            // Update logic (password optional, role optional)
            // Note: Our serializer expects 'role' only on create usually, but let's see.
            // If we want to update role, we might need to adjust serializer or view.
            // For now, let's assume update is mostly for password/email.
            api.put(`/users/admins/${editingId}/`, formData)
                .then(() => {
                    setShowForm(false);
                    setEditingId(null);
                    fetchAdmins();
                    setFormData({ username: '', email: '', password: '', role: 'admin' });
                })
                .catch(err => alert('Error updating admin: ' + JSON.stringify(err.response.data)));
        } else {
            api.post('/users/admins/', formData)
                .then(() => {
                    setShowForm(false);
                    fetchAdmins();
                    setFormData({ username: '', email: '', password: '', role: 'admin' });
                })
                .catch(err => alert('Error creating admin: ' + JSON.stringify(err.response.data)));
        }
    };

    const handleEdit = (admin) => {
        setFormData({
            username: admin.username,
            email: admin.email,
            password: '',
            role: admin.is_superuser ? 'superadmin' : 'admin'
        });
        setEditingId(admin.id);
        setShowForm(true);
    };

    const handleDeleteClick = (id) => {
        setConfirmTitle('Eliminar Administrador');
        setConfirmMessage('¿Estás seguro de que deseas eliminar este administrador?');
        setConfirmAction(() => () => deleteAdmin(id));
        setIsConfirmOpen(true);
    };

    const deleteAdmin = async (id) => {
        try {
            await api.delete(`/users/admins/${id}/`);
            fetchAdmins();
        } catch (err) {
            console.error(err);
            alert('Error deleting admin');
        }
    };

    const isSuperUser = currentUser?.is_superuser;

    return (
        <div>
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-3xl font-bold text-gray-800 dark:text-white">Administradores</h2>
                {isSuperUser && (
                    <button onClick={() => { setShowForm(!showForm); setEditingId(null); setFormData({ username: '', email: '', password: '', role: 'admin' }); }} className="bg-blue-600 text-white px-4 py-2 rounded flex items-center hover:bg-blue-700">
                        <Plus className="w-4 h-4 mr-2" /> {showForm ? 'Cancelar' : 'Nuevo Admin'}
                    </button>
                )}
            </div>

            {showForm && isSuperUser && (
                <div className="bg-white dark:bg-gray-800 p-6 rounded shadow mb-6 transition-colors duration-200">
                    <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">{editingId ? 'Editar Administrador' : 'Registrar Administrador'}</h3>
                    <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <input placeholder="Usuario" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.username} onChange={e => setFormData({ ...formData, username: e.target.value })} required />
                        <input placeholder="Email" type="email" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.email} onChange={e => setFormData({ ...formData, email: e.target.value })} required />
                        <select className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.role} onChange={e => setFormData({ ...formData, role: e.target.value })}>
                            <option value="admin">Admin Normal</option>
                            <option value="superadmin">Super Admin</option>
                        </select>
                        <input placeholder="Contraseña (Dejar en blanco para mantener)" type="password" className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" value={formData.password} onChange={e => setFormData({ ...formData, password: e.target.value })} />
                        <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded md:col-span-4 hover:bg-green-700">{editingId ? 'Actualizar' : 'Guardar'}</button>
                    </form>
                </div>
            )}

            <div className="bg-white dark:bg-gray-800 rounded shadow overflow-x-auto transition-colors duration-200">
                <table className="w-full">
                    <thead className="bg-gray-50 dark:bg-gray-700">
                        <tr>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">ID</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Usuario</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Email</th>
                            <th className="p-4 text-left text-gray-700 dark:text-gray-200">Rol</th>
                            {isSuperUser && <th className="p-4 text-left text-gray-700 dark:text-gray-200">Acciones</th>}
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                        {admins.map(admin => (
                            <tr key={admin.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-300">
                                <td className="p-4">{admin.id}</td>
                                <td className="p-4">{admin.username}</td>
                                <td className="p-4">{admin.email}</td>
                                <td className="p-4 flex items-center text-blue-600 dark:text-blue-400">
                                    <Shield className="w-4 h-4 mr-1" /> {admin.is_superuser ? 'Superadmin' : 'Admin'}
                                </td>
                                {isSuperUser && (
                                    <td className="p-4">
                                        <button onClick={() => handleEdit(admin)} className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 mr-2">Editar</button>
                                        <button onClick={() => handleDeleteClick(admin.id)} className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300">Eliminar</button>
                                    </td>
                                )}
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

export default Admins;
