// src/components/container/AsignacionesForm/AsignacionesTable.jsx
import React from 'react';
import { useGetAsignacionesQuery, useDeleteAsignacionMutation } from '../../../features/asignaciones/asignacionesApi';
import './AsignacionesTable.css';

const AsignacionesTable = ({ onEdit }) => {
  const { data: asignaciones = [], isLoading, isError } = useGetAsignacionesQuery();
  const [del, { isLoading: deleting }] = useDeleteAsignacionMutation();

  if (isLoading) return <p>Cargando asignaciones…</p>;
  if (isError)   return <p>Error al cargar asignaciones.</p>;

  const handleDelete = async (id) => {
    if (!window.confirm('¿Eliminar esta asignación?')) return;
    try { await del(id).unwrap(); }
    catch (e) { console.error(e); alert('No se pudo eliminar'); }
  };

  return (
    <div className="asignaciones-table">
      <table>
        <thead>
          <tr>
            <th style={{width: 30}}>ID</th>
            <th>Curso</th>
            <th>Profesor</th>
            <th>Materia</th>
            <th style={{width:30}}>Configurar</th>
          </tr>
        </thead>
        <tbody className='tb-body-asig'>
          {asignaciones.map(a => (
            <tr key={a.id}>
              <td>{a.id}</td>
              <td>{a.curso?.nombre_curso}</td>
              <td>{a.persona?.nombre} {a.persona?.apellido}</td>
              <td>{a.materia?.nombre}</td>
              <td className="row-actions">
                <button className="btn-config-asig" onClick={() => onEdit(a)}>⚙</button>
                <button className="btn-eliminar-asig" onClick={() => handleDelete(a.id)} disabled={deleting}>🗑</button>
              </td>
            </tr>
          ))}
          
          {asignaciones.length === 0 && (
            <tr><td colSpan="5" style={{textAlign:'center', fontSize:'2rem'}}>Sin asignaciones.</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default AsignacionesTable;
