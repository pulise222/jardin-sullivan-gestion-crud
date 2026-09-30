// src/components/container/Guardians/GuardianPicker.jsx
import React, { useEffect, useState } from 'react';
import { useLazySearchPeopleQuery } from '../../../features/people/personApi';
import { useAddGuardianToStudentMutation } from '../../../features/students/studentApi';
import './GuardianPicker.css';

const GuardianPicker = ({ studentId, onAssigned, onClose }) => {
  const [q, setQ] = useState('');
  const [trigger, { data: results = [], isFetching }] = useLazySearchPeopleQuery();
  const [addGuardian, { isLoading }] = useAddGuardianToStudentMutation();

  // búsqueda con debounce
  useEffect(() => {
    const t = setTimeout(() => {
      if (q.trim().length >= 2) trigger(q.trim());
    }, 300);
    return () => clearTimeout(t);
  }, [q, trigger]);

  const handleAssign = async (persona) => {
    const ok = window.confirm(`Asignar a "${persona.nombre} ${persona.apellido}" como acudiente?`);
    if (!ok) return;
    try {
      await addGuardian({ studentId, persona_id: persona.id }).unwrap();
      onAssigned?.();
      onClose?.();
    } catch (e) {
      console.error(e);
      alert('No se pudo asignar el acudiente.');
    }
  };

  const goCreateGuardian = () => {
    // navega a personas con preselección de rol
    window.location.href = '/admin?view=personas&new=acudiente';
  };

  return (
    <div className="guardian-picker">
      <div className="search-row">
        <input
          type="text"
          placeholder="Cédula o Nombre"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          className="search-input"
        />
        <button className="icon-btn" aria-label="Buscar" onClick={() => trigger(q.trim())}>
          🔍
        </button>
        <button className="icon-btn close" onClick={onClose} title="Cerrar">✖</button>
      </div>

      <div className="results">
        {isFetching ? <p>Buscando…</p> : (
          results.length ? results.map(p => (
            <div key={p.id} className="result-item">
              <div className="name">
                <strong>{p.nombre} {p.apellido}</strong>
                <small> · {p.numero_documento}</small>
              </div>
              <button
                className="assign-btn"
                onClick={() => handleAssign(p)}
                disabled={isLoading}
                title="Asignar acudiente"
              >
                ➕
              </button>
            </div>
          )) : <p className="muted">Escribe al menos 2 caracteres…</p>
        )}
      </div>

      {/* <button className="add-new" onClick={goCreateGuardian}>
        + Agregar nuevo Acudiente
      </button> */}
    </div>
  );
};

export default GuardianPicker;
