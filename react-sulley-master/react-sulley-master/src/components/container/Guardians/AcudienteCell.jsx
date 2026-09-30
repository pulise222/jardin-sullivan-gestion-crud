// src/components/container/Guardians/AcudienteCell.jsx
import React, { useState } from 'react';
import { useGetStudentGuardiansQuery } from '../../../features/students/studentApi';
import GuardianPicker from './GuardianPicker';
import './AcudienteCell.css'
const AcudienteCell = ({ student }) => {
  const { id: studentId } = student;
  const { data: guardians = [], refetch, isFetching } = useGetStudentGuardiansQuery(studentId);
  const [openPicker, setOpenPicker] = useState(false);

  if (isFetching) return <span>Cargando…</span>;

  // Si ya tiene acudiente(s)
  if (guardians.length > 0 && !openPicker) {
    const g = guardians[0]; // muestra el primero
    return (
      <div style={{display:'flex',gap:8,alignItems:'center'}}>
        <div>
          <strong>{g.nombre} {g.apellido}</strong>
          <div style={{fontSize:12,color:'#64748b'}}>{g.numero_documento}</div>
        </div>
        <button className="small-btn" onClick={() => setOpenPicker(true)} title="Cambiar Acudiente">⚙️</button>
      </div>
    );
  }

  // No tiene — o se quiere abrir el buscador
  return (
    <GuardianPicker
      studentId={studentId}
      onAssigned={() => refetch()}
      onClose={() => setOpenPicker(false)}
    />
  );
};

export default AcudienteCell;
