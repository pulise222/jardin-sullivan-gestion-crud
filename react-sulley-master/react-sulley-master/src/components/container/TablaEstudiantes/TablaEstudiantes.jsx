// src/components/container/TablaEstudiantes/TablaEstudiantes.jsx
import React, { useEffect  } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { setEstudiantes } from '../../../features/students/studentSlice';
import { useDeleteStudentMutation, useGetStudentsQuery } from '../../../features/students/studentApi';
import AcudienteCell from '../Guardians/AcudienteCell';
import "./TablaEstudiantes.css"

const TablaEstudiantes = ({handleEdit}) => {
  const dispatch = useDispatch()
  const estudiantes = useSelector(s=>s.student.estudiantes)
  const estudiantesFiltrados = useSelector(s=>s.student.estudiantesFiltrados)
  const { data, isSuccess, isLoading, isError } = useGetStudentsQuery();
  const [ deleteStudent ] = useDeleteStudentMutation()

  useEffect(() => {
    if (isSuccess) {
      dispatch(setEstudiantes(data));
    }
  }, [isSuccess, data, dispatch, estudiantes.length, estudiantesFiltrados.length]);

  if (isLoading) return <p>Cargando estudiantes...</p>;
  if (isError) return <p>Error al cargar estudiantes</p>;

  const handleDelete = (id) => {
    deleteStudent(id)
  }

  const lista = (estudiantesFiltrados.length>0 ? estudiantesFiltrados : estudiantes);

  return (
  <div className="student">
  <h2>Listado de Estudiantes</h2>
    <table className='content-table'>
      <thead>
        <tr>
          <th>ID</th>
          <th>Nombre</th>
          <th>Apellido</th>
          <th>Tipo Doc</th>
          <th>Documento</th>
          <th>Correo</th>
          <th>Dirección</th>
          <th>Fecha Nacimiento</th>
          <th>Curso</th>
          <th>Acudiente</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {lista.map(est => (
          <tr key={est.id}>
            <td>{est.id}</td>
            <td>{est.nombre}</td>
            <td>{est.apellido}</td>
            <td>{est.tipo_documento || '—'}</td>
            <td>{est.numero_documento || '—'}</td>
            <td>{est.correo_electronico}</td>
            <td>{est.direccion}</td>
            <td>{est.fecha_nacimiento}</td>
            <td>{est.curso}</td>
            <td>
              <AcudienteCell student={est} />
            </td>
            <td>
              <div className="btn-group">
                  <button className="btn" onClick={()=>handleEdit(est)}><i className="fas fa-edit"></i></button>
                  <button className="btn" onClick={()=>handleDelete(est.id)} ><i className="fas fa-trash"></i></button>
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
  );
};

export default TablaEstudiantes;