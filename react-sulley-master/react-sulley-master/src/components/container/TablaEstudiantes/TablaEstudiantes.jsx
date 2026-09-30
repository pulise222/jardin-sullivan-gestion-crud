// src/components/container/TablaEstudiantes/TablaEstudiantes.jsx
import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setEstudiantes } from '../../../features/students/studentSlice';
import { useDeleteStudentMutation, useGetStudentsQuery } from '../../../features/students/studentApi';
import AcudienteCell from '../Guardians/AcudienteCell';
// "TablaEstudiantes.css" se conserva porque la tabla de Personas todavía usa algunas de sus clases;
// los estilos de esta tabla ahora están en src/styles/panel.css (clases "pn-…").
import './TablaEstudiantes.css';

// "2019-05-14" → "14/05/2019". Se parte el texto a mano para evitar que la zona horaria cambie el día.
const formatDate = (iso) => {
  if (!iso) return '—';
  const [y, m, d] = String(iso).split('-');
  return y && m && d ? `${d}/${m}/${y}` : iso;
};

const TablaEstudiantes = ({ handleEdit }) => {
  const dispatch = useDispatch();
  const estudiantes = useSelector((s) => s.student.estudiantes);
  const estudiantesFiltrados = useSelector((s) => s.student.estudiantesFiltrados);
  const { data, isSuccess, isLoading, isError } = useGetStudentsQuery();
  const [deleteStudent] = useDeleteStudentMutation();

  useEffect(() => {
    if (isSuccess) {
      dispatch(setEstudiantes(data));
    }
  }, [isSuccess, data, dispatch, estudiantes.length, estudiantesFiltrados.length]);

  // ---- Estados de la pantalla: cargando, error o sin datos ----
  if (isLoading) {
    return (
      <div className="pn-card pn-state" role="status">
        <span className="pn-spinner" aria-hidden="true"></span>
        <strong>Cargando estudiantes…</strong>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="pn-card pn-state" role="alert">
        <i className="fas fa-triangle-exclamation" aria-hidden="true"></i>
        <strong>No pudimos cargar los estudiantes</strong>
        <span>Revisa que el servidor esté encendido e inténtalo de nuevo.</span>
      </div>
    );
  }

  // Antes se borraba al primer clic. Ahora pedimos confirmación (eliminar no se puede deshacer).
  const handleDelete = (est) => {
    if (window.confirm(`¿Eliminar a ${est.nombre} ${est.apellido}? Esta acción no se puede deshacer.`)) {
      deleteStudent(est.id);
    }
  };

  const lista = estudiantesFiltrados.length > 0 ? estudiantesFiltrados : estudiantes;

  if (lista.length === 0) {
    return (
      <div className="pn-card pn-state">
        <i className="fas fa-children" aria-hidden="true"></i>
        <strong>Aún no hay estudiantes</strong>
        <span>Usa el botón “Agregar estudiante” para crear el primero.</span>
      </div>
    );
  }

  return (
    <div className="pn-card">
      <div className="pn-table-wrap">
        <table className="pn-table">
          <thead>
            <tr>
              <th>Estudiante</th>
              <th>Documento</th>
              <th>Nacimiento</th>
              <th>Dirección</th>
              <th>Curso</th>
              <th>Acudiente</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {lista.map((est) => (
              <tr key={est.id}>
                <td>
                  <div className="pn-person">
                    {/* Círculo con la inicial del nombre */}
                    <span className="pn-avatar" aria-hidden="true">{(est.nombre || '?').charAt(0)}</span>
                    <div>
                      <strong>{est.nombre} {est.apellido}</strong>
                      <small>{est.correo_electronico || 'Sin correo'}</small>
                    </div>
                  </div>
                </td>
                <td>
                  <span className="pn-chip">{est.tipo_documento || '—'}</span>{' '}
                  <span className="pn-muted">{est.numero_documento || ''}</span>
                </td>
                <td className="pn-muted">{formatDate(est.fecha_nacimiento)}</td>
                <td className="pn-muted">{est.direccion || '—'}</td>
                <td>
                  {est.curso ? (
                    <span className="pn-chip is-accent">{est.curso}</span>
                  ) : (
                    <span className="pn-muted">Sin curso</span>
                  )}
                </td>
                <td>
                  <AcudienteCell student={est} />
                </td>
                <td>
                  <div className="pn-actions">
                    <button
                      type="button"
                      className="pn-icon-btn"
                      onClick={() => handleEdit(est)}
                      aria-label={`Editar a ${est.nombre} ${est.apellido}`}
                      title="Editar"
                    >
                      <i className="fas fa-pen" aria-hidden="true"></i>
                    </button>
                    <button
                      type="button"
                      className="pn-icon-btn is-danger"
                      onClick={() => handleDelete(est)}
                      aria-label={`Eliminar a ${est.nombre} ${est.apellido}`}
                      title="Eliminar"
                    >
                      <i className="fas fa-trash" aria-hidden="true"></i>
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default TablaEstudiantes;
