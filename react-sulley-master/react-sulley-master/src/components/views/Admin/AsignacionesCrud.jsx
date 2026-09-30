// src/components/views/Admin/AsignacionesCrud.jsx
import React, { useState } from 'react';
import AsignacionesForm from '../../container/AsignacionesForm/AsignacionesForm';
import AsignacionesTable from '../../container/AsignacionesTable/AsignacionesTable';

const AsignacionesCrud = () => {
  const [editing, setEditing] = useState(null);

  return (
    <div style={{padding:'20px'}}>
      <AsignacionesForm
        editing={editing}
        onSaved={() => setEditing(null)}   // tras crear/editar, limpiar
        onCancel={() => setEditing(null)}
      />

      <div style={{marginTop:'24px'}}>
        <AsignacionesTable onEdit={setEditing} />
      </div>
    </div>
  );
};

export default AsignacionesCrud;
