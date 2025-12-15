import React, { useState, useEffect, useRef } from 'react';
import { ChevronDown, Search, X } from 'lucide-react';

const SearchableSelect = ({ options, value, onChange, placeholder = "Seleccionar...", labelKey = "label", valueKey = "id" }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const wrapperRef = useRef(null);

    // Close when clicking outside
    useEffect(() => {
        function handleClickOutside(event) {
            if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        }
        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [wrapperRef]);

    const getLabel = (opt) => {
        if (!opt) return '';
        if (typeof labelKey === 'function') {
            return labelKey(opt);
        }
        // Specific for this app's clients if keys exist
        if (opt.nombres && opt.apellidos) return `${opt.nombres} ${opt.apellidos}`;

        return opt[labelKey];
    };

    // Find selected option label
    const selectedOption = options.find(opt => String(opt[valueKey]) === String(value));

    // Safety check for options being null/undefined or not array
    const safeOptions = Array.isArray(options) ? options : [];

    const filteredOptions = safeOptions.filter(opt => {
        const label = getLabel(opt).toLowerCase();
        const search = searchTerm.toLowerCase();
        return label.includes(search);
    });

    const handleSelect = (opt) => {
        onChange({ target: { value: opt[valueKey] } }); // Mimic event object for compatibility with existing handlers
        setIsOpen(false);
        setSearchTerm('');
    };

    return (
        <div className="relative" ref={wrapperRef}>
            <div
                className="border p-2 rounded dark:bg-gray-700 dark:border-gray-600 dark:text-white flex justify-between items-center cursor-pointer bg-white dark:bg-gray-700"
                onClick={() => setIsOpen(!isOpen)}
            >
                <span className={!selectedOption ? "text-gray-500" : "dark:text-white"}>
                    {selectedOption ? getLabel(selectedOption) : placeholder}
                </span>
                <ChevronDown size={16} className="text-gray-500" />
            </div>

            {isOpen && (
                <div className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border dark:border-gray-600 rounded shadow-lg max-h-60 overflow-hidden flex flex-col">
                    <div className="p-2 border-b dark:border-gray-600 flex items-center bg-gray-50 dark:bg-gray-700">
                        <Search size={16} className="text-gray-400 mr-2" />
                        <input
                            type="text"
                            className="w-full bg-transparent outline-none text-gray-700 dark:text-gray-200"
                            placeholder="Buscar..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            autoFocus
                            onClick={(e) => e.stopPropagation()}
                        />
                        {searchTerm && (
                            <button onClick={(e) => { e.stopPropagation(); setSearchTerm(''); }} className="text-gray-400 hover:text-gray-600">
                                <X size={16} />
                            </button>
                        )}
                    </div>
                    <div className="overflow-y-auto max-h-48">
                        {filteredOptions.length > 0 ? (
                            filteredOptions.map(opt => (
                                <div
                                    key={opt[valueKey]}
                                    className={`p-2 hover:bg-blue-50 dark:hover:bg-gray-700 cursor-pointer text-gray-800 dark:text-gray-200 ${String(opt[valueKey]) === String(value) ? 'bg-blue-100 dark:bg-gray-600' : ''}`}
                                    onClick={() => handleSelect(opt)}
                                >
                                    {getLabel(opt)}
                                </div>
                            ))
                        ) : (
                            <div className="p-2 text-gray-500 text-center text-sm">No se encontraron resultados</div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default SearchableSelect;
