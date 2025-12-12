import React, { useEffect, useState } from 'react';
import api from '../api';
import { FileText, Download, Search } from 'lucide-react';

const GenerateContract = () => {
    const [contracts, setContracts] = useState([]);
    const [clients, setClients] = useState([]);
    const [motos, setMotos] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            const [contractsRes, clientsRes, motosRes] = await Promise.all([
                api.get('/contracts/contracts/'),
                api.get('/users/clients/'),
                api.get('/inventory/motos/')
            ]);
            setContracts(contractsRes.data);
            setClients(clientsRes.data);
            setMotos(motosRes.data);
            setLoading(false);
        } catch (err) {
            console.error(err);
            setLoading(false);
        }
    };

    const handleDownloadPdf = async (contract) => {
        try {
            const response = await api.get(`/contracts/contracts/${contract.id}/download_contract_pdf/`, {
                responseType: 'blob',
            });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            const clientName = getClientName(contract.cliente).replace(/ /g, '_');
            link.setAttribute('download', `contrato_legal_${clientName}.pdf`);
            document.body.appendChild(link);
            link.click();
            link.remove();
        } catch (err) {
            console.error('Error downloading PDF:', err);
            alert('Error downloading PDF');
        }
    };

    const getClientName = (id) => {
        const client = clients.find(c => c.id === id);
        return client ? `${client.nombres} ${client.apellidos}` : 'Desconocido';
    };

    const getMotoInfo = (id) => {
        const moto = motos.find(m => m.id === id);
        return moto ? `${moto.marca} ${moto.modelo} - ${moto.placa}` : 'Desconocido';
    };

    const filteredContracts = contracts.filter(contract => {
        const clientName = getClientName(contract.cliente).toLowerCase();
        const motoInfo = getMotoInfo(contract.moto).toLowerCase();
        const search = searchTerm.toLowerCase();
        return clientName.includes(search) || motoInfo.includes(search) || contract.id.toString().includes(search);
    });

    if (loading) return <div>Cargando...</div>;

    return (
        <div>
            <h2 className="text-3xl font-bold mb-6 text-gray-800 dark:text-white">Generar Contratos</h2>

            <div className="bg-white dark:bg-gray-800 p-6 rounded shadow mb-6">
                <p className="text-gray-600 dark:text-gray-300 mb-4">
                    Seleccione un contrato existente para generar el documento PDF legal con los términos y condiciones actualizados.
                </p>

                <div className="relative mb-4">
                    <input
                        type="text"
                        placeholder="Buscar por cliente, moto o ID..."
                        className="w-full border p-3 pl-10 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                        value={searchTerm}
                        onChange={e => setSearchTerm(e.target.value)}
                    />
                    <Search className="absolute left-3 top-3.5 text-gray-400" size={20} />
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full">
                        <thead className="bg-gray-50 dark:bg-gray-700">
                            <tr>
                                <th className="p-4 text-left text-gray-700 dark:text-gray-200">ID</th>
                                <th className="p-4 text-left text-gray-700 dark:text-gray-200">Cliente</th>
                                <th className="p-4 text-left text-gray-700 dark:text-gray-200">Moto</th>
                                <th className="p-4 text-left text-gray-700 dark:text-gray-200">Fecha</th>
                                <th className="p-4 text-left text-gray-700 dark:text-gray-200">Acción</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                            {filteredContracts.map(contract => (
                                <tr key={contract.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-gray-300">
                                    <td className="p-4">#{contract.id}</td>
                                    <td className="p-4">{getClientName(contract.cliente)}</td>
                                    <td className="p-4">{getMotoInfo(contract.moto)}</td>
                                    <td className="p-4">{contract.fecha_contrato}</td>
                                    <td className="p-4">
                                        <button
                                            onClick={() => handleDownloadPdf(contract)}
                                            className="bg-blue-600 text-white px-4 py-2 rounded flex items-center hover:bg-blue-700 transition-colors"
                                        >
                                            <FileText className="w-4 h-4 mr-2" /> Generar PDF
                                        </button>
                                    </td>
                                </tr>
                            ))}
                            {filteredContracts.length === 0 && (
                                <tr>
                                    <td colSpan="5" className="p-4 text-center text-gray-500 dark:text-gray-400">
                                        No se encontraron contratos.
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
};

export default GenerateContract;
