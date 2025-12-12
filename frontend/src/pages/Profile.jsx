import React, { useEffect, useState } from 'react';
import api from '../api';
import { User, Mail, Camera, Save } from 'lucide-react';

const Profile = () => {
    const [user, setUser] = useState({
        username: '', email: '', first_name: '', last_name: '', additional_info: '', photo: null
    });
    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchProfile();
    }, []);

    const fetchProfile = async () => {
        try {
            const res = await api.get('/users/me/');
            setUser(res.data);
            if (res.data.photo) {
                setPreview(res.data.photo);
            }
            setLoading(false);
        } catch (err) {
            console.error(err);
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        setUser({ ...user, [e.target.name]: e.target.value });
    };

    const handleImageChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setPreview(URL.createObjectURL(file));
            setUser({ ...user, photo: file });
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const formData = new FormData();
        formData.append('email', user.email);
        formData.append('first_name', user.first_name);
        formData.append('last_name', user.last_name);
        formData.append('additional_info', user.additional_info || '');
        if (user.photo instanceof File) {
            formData.append('photo', user.photo);
        }

        try {
            const res = await api.put('/users/me/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            alert('Perfil actualizado correctamente');
            setUser(res.data);
            if (res.data.photo) {
                setPreview(res.data.photo);
            }
        } catch (err) {
            console.error(err);
            alert('Error al actualizar perfil');
        }
    };

    if (loading) return <div>Cargando...</div>;

    return (
        <div className="max-w-2xl mx-auto bg-white dark:bg-gray-800 p-8 rounded shadow">
            <h2 className="text-3xl font-bold mb-6 text-gray-800 dark:text-white">Mi Perfil</h2>

            <form onSubmit={handleSubmit} className="space-y-6">
                <div className="flex flex-col items-center mb-6">
                    <div className="relative w-32 h-32 mb-4">
                        {preview ? (
                            <img src={preview} alt="Profile" className="w-full h-full rounded-full object-cover border-4 border-blue-100" />
                        ) : (
                            <div className="w-full h-full rounded-full bg-gray-200 flex items-center justify-center text-gray-500">
                                <User size={48} />
                            </div>
                        )}
                        <label className="absolute bottom-0 right-0 bg-blue-600 p-2 rounded-full text-white cursor-pointer hover:bg-blue-700">
                            <Camera size={20} />
                            <input type="file" className="hidden" onChange={handleImageChange} accept="image/*" />
                        </label>
                    </div>
                    <p className="text-gray-500 dark:text-gray-400">@{user.username}</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label className="block text-gray-700 dark:text-gray-300 mb-2">Nombre</label>
                        <input name="first_name" value={user.first_name} onChange={handleChange} className="w-full border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
                    </div>
                    <div>
                        <label className="block text-gray-700 dark:text-gray-300 mb-2">Apellido</label>
                        <input name="last_name" value={user.last_name} onChange={handleChange} className="w-full border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white" />
                    </div>
                    <div className="md:col-span-2">
                        <label className="block text-gray-700 dark:text-gray-300 mb-2">Email</label>
                        <div className="flex items-center border rounded dark:bg-gray-700 dark:border-gray-600">
                            <Mail className="ml-2 text-gray-400" size={20} />
                            <input name="email" value={user.email} onChange={handleChange} className="w-full p-2 bg-transparent outline-none dark:text-white" />
                        </div>
                    </div>
                    <div className="md:col-span-2">
                        <label className="block text-gray-700 dark:text-gray-300 mb-2">Información Adicional</label>
                        <textarea name="additional_info" value={user.additional_info || ''} onChange={handleChange} className="w-full border p-2 rounded h-32 dark:bg-gray-700 dark:border-gray-600 dark:text-white" placeholder="Cuéntanos algo sobre ti..."></textarea>
                    </div>
                </div>

                <button type="submit" className="w-full bg-blue-600 text-white py-3 rounded font-bold hover:bg-blue-700 flex justify-center items-center">
                    <Save className="mr-2" /> Guardar Cambios
                </button>
            </form>
        </div>
    );
};

export default Profile;
