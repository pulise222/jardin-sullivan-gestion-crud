// // src/components/AsignacionesForm/AsignacionesForm.jsx
// import React from 'react';
// import { useFormik } from 'formik';
// import * as Yup from 'yup';

// import { useGetPeopleQuery } from '../../../features/people/personApi';
// import { useGetMateriasQuery } from '../../../features/materias/materiasApi';
// import { 
//     useGetCoursesQuery, 
//     useAssignCursoProfesorMateriaMutation 
// } from '../../../features/cursos/cursosApi'

// import './AsignacionesForm.css';

// const AsignacionesForm = () => {
//   // 1) Traer datos
//   const {
//     data: cursos = [],
//     isLoading: loadingCursos,
//     isError: errorCursos
//   } = useGetCoursesQuery();

//   const {
//     data: personas = [],
//     isLoading: loadingPersonas,
//     isError: errorPersonas
//   } = useGetPeopleQuery();

//   const {
//     data: materias = [],
//     isLoading: loadingMaterias,
//     isError: errorMaterias
//   } = useGetMateriasQuery();

//   const [
//     assign,
//     { isLoading: isSubmitting }
//   ] = useAssignCursoProfesorMateriaMutation();

//   // 2) Formik
//   const formik = useFormik({
//     initialValues: {
//       curso_id: '',
//       persona_id: '',
//       materia_id: ''
//     },
//     validationSchema: Yup.object({
//       curso_id: Yup.number().required('Requerido'),
//       persona_id: Yup.number().required('Requerido'),
//       materia_id: Yup.number().required('Requerido')
//     }),
//     onSubmit: async (values, { resetForm }) => {
//       console.log(values);
//       try {
//         await assign(values).unwrap();
//         alert('Asignación creada con éxito');
//         resetForm();
//       } catch (err) {
//         console.error(err);
//         alert('Error al crear la asignación');
//       }
//     }
//   });

//   // 3) Manejar estados de carga
//   if (loadingCursos || loadingPersonas || loadingMaterias) {
//     return <p>Cargando datos…</p>;
//   }
//   if (errorCursos || errorPersonas || errorMaterias) {
//     return <p>Error al cargar las listas.</p>;
//   }

//   return (
//     <div className="asignaciones-form">
//       <h2>Asignar Profesor y Materia</h2>
//       <form onSubmit={formik.handleSubmit}>
//         {/* Curso */}
//         <label>
//           Curso
//           <select
//             name="curso_id"
//             value={formik.values.curso_id}
//             onChange={formik.handleChange}
//             onBlur={formik.handleBlur}
//           >
//             <option value="">-- Seleccione curso --</option>
//             {cursos.map(c =>
//               <option key={c.id} value={c.id}>{c.nombre_curso}</option>
//             )}
//           </select>
//         </label>
//         {formik.touched.curso_id && formik.errors.curso_id && (
//           <div className="error">{formik.errors.curso_id}</div>
//         )}

//         {/* Profesor */}
//         <label>
//           Profesor
//           <select
//             name="persona_id"
//             value={formik.values.persona_id}
//             onChange={formik.handleChange}
//             onBlur={formik.handleBlur}
//           >
//             <option value="">-- Seleccione profesor --</option>
//             {personas
//                 // .filter(p => p.rol === 'Profesor') // o el campo que uses
//                .map(p =>
//                  <option key={p.id} value={p.id}>
//                    {p.nombre} {p.apellido}
//                  </option>
//                )}
//           </select>
//         </label>
//         {formik.touched.persona_id && formik.errors.persona_id && (
//           <div className="error">{formik.errors.persona_id}</div>
//         )}

//         {/* Materia */}
//         <label>
//           Materia
//           <select
//             name="materia_id"
//             value={formik.values.materia_id}
//             onChange={formik.handleChange}
//             onBlur={formik.handleBlur}
//           >
//             <option value="">-- Seleccione materia --</option>
//             {materias.map(m =>
//               <option key={m.id} value={m.id}>{m.nombre}</option>
//             )}
//           </select>
//         </label>
//         {formik.touched.materia_id && formik.errors.materia_id && (
//           <div className="error">{formik.errors.materia_id}</div>
//         )}

//         <button type="submit" disabled={isSubmitting}>
//           {isSubmitting ? 'Asignando…' : 'Asignar'}
//         </button>
//       </form>
//     </div>
//   );
// };

// export default AsignacionesForm;









// src/components/AsignacionesForm/AsignacionesForm.jsx

import React, { useEffect } from 'react';
import { useFormik } from 'formik';
import * as Yup from 'yup';

import { useGetCoursesQuery } from '../../../features/cursos/cursosApi';
import { useGetPeopleQuery } from '../../../features/people/personApi';
import { useGetMateriasQuery } from '../../../features/materias/materiasApi';
import { 
  useCreateAsignacionMutation,
  useUpdateAsignacionMutation,
} from '../../../features/asignaciones/asignacionesApi';

import './AsignacionesForm.css';

const AsignacionesForm = ({ editing, onSaved, onCancel }) => {
  const { data: cursos = [] }   = useGetCoursesQuery();
  const { data: personas = [] } = useGetPeopleQuery();
  const { data: materias = [] } = useGetMateriasQuery();

  const [createAsignacion, { isLoading: creating }] = useCreateAsignacionMutation();
  const [updateAsignacion, { isLoading: updating }] = useUpdateAsignacionMutation();

  const formik = useFormik({
    initialValues: {
      curso_id:   '',
      persona_id: '',
      materia_id: '',
    },
    validationSchema: Yup.object({
      curso_id:   Yup.number().required('Requerido'),
      persona_id: Yup.number().required('Requerido'),
      materia_id: Yup.number().required('Requerido'),
    }),
    onSubmit: async (values, { resetForm }) => {
      try {
        if (editing?.id) {
          await updateAsignacion({ id: editing.id, ...values }).unwrap();
        } else {
          await createAsignacion(values).unwrap();
        }
        resetForm();
        onSaved?.();
      } catch (err) {
        console.error(err);
        alert(err?.data?.detail || 'No se pudo guardar');
      }
    },
    enableReinitialize: true,
  });

  // Cargar valores al entrar en modo edición
  useEffect(() => {
    if (editing) {
      formik.setValues({
        curso_id:   editing.curso?.id   ?? '',
        persona_id: editing.persona?.id ?? '',
        materia_id: editing.materia?.id ?? '',
      });
    } else {
      formik.resetForm();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [editing]);

  const busy = creating || updating;

  return (
    <div className="asignaciones-form">
      <h2>{editing ? 'Editar Asignación' : 'Asignar Profesor y Materia'}</h2>
      <form onSubmit={formik.handleSubmit}>
        <label>Curso
          <select name="curso_id" value={formik.values.curso_id} onChange={formik.handleChange} onBlur={formik.handleBlur}>
            <option value="">-- Seleccione curso --</option>
            {cursos.map(c => <option key={c.id} value={c.id}>{c.nombre_curso}</option>)}
          </select>
        </label>
        {formik.touched.curso_id && formik.errors.curso_id && <div className="error">{formik.errors.curso_id}</div>}

        <label>Profesor
          <select name="persona_id" value={formik.values.persona_id} onChange={formik.handleChange} onBlur={formik.handleBlur}>
            <option value="">-- Seleccione profesor --</option>
            {personas.map(p => (
              <option key={p.id} value={p.id}>{p.nombre} {p.apellido}</option>
            ))}
          </select>
        </label>
        {formik.touched.persona_id && formik.errors.persona_id && <div className="error">{formik.errors.persona_id}</div>}

        <label>Materia
          <select name="materia_id" value={formik.values.materia_id} onChange={formik.handleChange} onBlur={formik.handleBlur}>
            <option value="">-- Seleccione materia --</option>
            {materias.map(m => <option key={m.id} value={m.id}>{m.nombre}</option>)}
          </select>
        </label>
        {formik.touched.materia_id && formik.errors.materia_id && <div className="error">{formik.errors.materia_id}</div>}

        <div className="form-actions">
          {editing && (
            <button type="button" className="btn-secondary" onClick={onCancel} disabled={busy}>
              Cancelar
            </button>
          )}
          <button type="submit" disabled={busy}>
            {busy ? 'Guardando…' : (editing ? 'Actualizar' : 'Asignar')}
          </button>
        </div>
      </form>
    </div>
  );
};

export default AsignacionesForm;
