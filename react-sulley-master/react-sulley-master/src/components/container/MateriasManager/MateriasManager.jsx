// src/components/container/MateriasManager/MateriasManager.jsx
import React, { useState } from 'react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import {
  useGetMateriasQuery,
  useCreateMateriaMutation,
  useUpdateMateriaMutation,
  useDeleteMateriaMutation
} from '../../../features/materias/materiasApi';

import './MateriasManager.css';

const MateriasManager = () => {
  // 1) Traer lista
  const { data: materias = [], isLoading, isError } = useGetMateriasQuery();

  // 2) Mutations
  const [createMateria, { isLoading: isCreating }] = useCreateMateriaMutation();
  const [updateMateria, { isLoading: isUpdating }] = useUpdateMateriaMutation();
  const [deleteMateria, { isLoading: isDeleting }] = useDeleteMateriaMutation();

  // 3) Estado de edición
  const [editing, setEditing] = useState(null); // {id, nombre} o null

  // 4) Formik (re-inicializa cuando cambia `editing`)
  const formik = useFormik({
    enableReinitialize: true,
    initialValues: { nombre: editing?.nombre || '' },
    validationSchema: Yup.object({
      nombre: Yup.string().required('Este campo es obligatorio'),
    }),
    onSubmit: async (values, { resetForm }) => {
      try {
        if (editing) {
          await updateMateria({ id: editing.id, ...values }).unwrap();
          setEditing(null);
        } else {
          await createMateria(values).unwrap();
        }
        resetForm();
      } catch (err) {
        console.error('Error al guardar materia:', err);
        alert('No se pudo guardar la materia');
      }
    },
  });

  const onEditClick = (m) => {
    setEditing(m);
  };

  const onCancelEdit = () => {
    setEditing(null);
    formik.resetForm();
  };

  const onDeleteClick = async (id) => {
    if (!confirm('¿Eliminar esta materia?')) return;
    try {
      await deleteMateria(id).unwrap();
    } catch (err) {
      console.error('Error al eliminar materia:', err);
      alert('No se pudo eliminar la materia');
    }
  };

  if (isLoading) return <p>Cargando materias…</p>;
  if (isError)   return <p>Error al cargar materias</p>;

  return (
    <div className="materias-manager">
      {/* LISTADO */}
      <div className="materias-list">
        <h2>Materias Existentes</h2>

        {materias.length === 0 ? (
          <p>No hay materias.</p>
        ) : (
          <ul className="materias-ul">
            {materias.map(m => (
              <li key={m.id} className="materia-row">
                <span className="materia-nombre">{m.nombre}</span>
                <div className="materias-actions">
                  <button
                    type="button"
                    className="btn btn-edit"
                    onClick={() => onEditClick(m)}
                    title="Editar"
                  >
                    ✎ Editar
                  </button>
                  <button
                    type="button"
                    className="btn btn-delete"
                    onClick={() => onDeleteClick(m.id)}
                    disabled={isDeleting}
                    title="Eliminar"
                  >
                    🗑 Eliminar
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* FORMULARIO */}
      <div className="materias-form">
        <h2>{editing ? 'Editar Materia' : 'Agregar Nueva Materia'}</h2>
        <form onSubmit={formik.handleSubmit}>
          <div className="form-group">
            <input
              name="nombre"
              type="text"
              placeholder="Nombre de la materia"
              value={formik.values.nombre}
              onChange={formik.handleChange}
              onBlur={formik.handleBlur}
            />
            {formik.touched.nombre && formik.errors.nombre && (
              <div className="error">{formik.errors.nombre}</div>
            )}
          </div>

          <div className="form-actions">
            <button
              type="submit"
              disabled={isCreating || isUpdating}
              className="btn btn-primary"
            >
              {editing
                ? (isUpdating ? 'Guardando…' : 'Guardar cambios')
                : (isCreating ? 'Creando…' : 'Crear Materia')}
            </button>

            {editing && (
              <button type="button" className="btn btn-secondary" onClick={onCancelEdit}>
                Cancelar
              </button>
            )}
          </div>
        </form>
      </div>
    </div>
  );
};

export default MateriasManager;