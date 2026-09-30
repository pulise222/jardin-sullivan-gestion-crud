// src/components/container/TablaPersonas/TablaPersonas.jsx
import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setPeople } from '../../../features/people/personSlice';
import { useGetPeopleQuery, useDeletePersonMutation } from '../../../features/people/personApi';
import "./TablaPersonas.css";

const TablaPersonas = ({ handleEdit }) => {
  const dispatch = useDispatch();
  const personas = useSelector(state => state.people.people);
  const personasFiltradas = useSelector(state => state.people.personasFiltradas);

  const { data, isSuccess, isLoading, isError } = useGetPeopleQuery();
  const [deletePerson] = useDeletePersonMutation();

  useEffect(() => {
    if (isSuccess && data) {
      dispatch(setPeople(data));
    }
  }, [isSuccess, data, dispatch]);

  if (isLoading) return <p>Cargando personas...</p>;
  if (isError) return <p>Error al cargar personas</p>;

  const handleDelete = async (id) => {
    if (!confirm('¿Eliminar esta persona?')) return;
    try {
      await deletePerson(id).unwrap();
    } catch (e) {
      console.error(e);
      alert('No se pudo eliminar la persona');
    }
  };

  const lista = (personasFiltradas.length > 0 ? personasFiltradas : personas) || [];

  return (
    <div className="persona">
      <h2>Listado de Personas</h2>
      <table className='content-table'>
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Apellido</th>
            <th>Tipo Documento</th>
            <th>No Documento</th>
            <th>Correo</th>
            <th>Dirección</th>
            <th>Teléfono</th>
            <th>Rol</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {lista.map((per) => (
            <tr key={per.id}>
              <td>{per.id}</td>
              <td>{per.nombre}</td>
              <td>{per.apellido}</td>
              <td>{per.tipo_documento}</td>
              <td>{per.numero_documento}</td>
              {/* email puede venir del usuario anidado */}
              <td>{per.usuario?.email ?? per.email ?? '—'}</td>
              <td>{per.direccion}</td>
              <td>{per.telefono}</td>
              <td>{per.usuario?.rol ?? per.rol ?? '—'}</td>
              <td>
                <div className="btn-group">
                  <button type="button" className="btn" onClick={() => handleEdit(per)}>
                    <i className="fas fa-edit"></i>
                  </button>
                  <button type="button" className="btn" onClick={() => handleDelete(per.id)}>
                    <i className="fas fa-trash"></i>
                  </button>
                </div>
              </td>
            </tr>
          ))}
          {lista.length === 0 && (
            <tr>
              <td colSpan={10}>No hay personas.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default TablaPersonas;