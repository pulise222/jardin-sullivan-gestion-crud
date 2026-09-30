import React, { useMemo, useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { Formik, Form, Field, ErrorMessage } from 'formik';
import * as Yup from 'yup';

import {
  useGetActividadesPorCursoQuery,
  useCrearActividadEnCursoMutation,
  useGetEntregasByActividadQuery,
  useActualizarEntregaMutation,
  useActualizarActividadMutation,   // <-- NUEVO
  useEliminarActividadMutation,     // <-- NUEVO
} from '../../../features/actividades/actividadesApi';

import {
  setActividadSeleccionada,
  toggleFormulario,
} from '../../../features/actividades/actividadesSlice';

import './css/Activities.css';

const schemaActividad = Yup.object({
  titulo: Yup.string().required('Requerido'),
  descripcion: Yup.string().required('Requerido'),
  fecha: Yup.date().required('Requerido'),
  fecha_entrega: Yup.date().nullable(true),
});

const Activities = () => {
  const dispatch = useDispatch();

  // CPM del curso+materia seleccionado
  const cpm = useSelector((s) =>
    s.clase?.claseEnCurso?.dictada_por ?? s.courses?.curso_profesor_materia
  );
  const cursoId = cpm?.curso?.id;
  const cpmId = cpm?.id;

  const mostrarFormulario = useSelector((s) => s.actividades.mostrarFormulario);
  const actividadSeleccionada = useSelector((s) => s.actividades.actividadSeleccionada);
  const actividadId = actividadSeleccionada?.id || null;

  // Lista de actividades
  const { data: actividades, isLoading, refetch } = useGetActividadesPorCursoQuery(
    { cursoId, todas: 0 },
    { skip: !cursoId }
  );

  // Filtro server-side para la tabla relación
  const [detalleFiltro, setDetalleFiltro] = useState('entregadas'); // 'entregadas' | 'pendientes' | 'todas'

  // Entregas de la actividad (RELACIÓN)
  const {
    data: entregas,
    isLoading: loadingEntregas,
    refetch: refetchEntregas,
  } = useGetEntregasByActividadQuery(
    { actividadId, estado: detalleFiltro },
    { skip: !actividadId }
  );

  // Mutations
  const [crearActividad] = useCrearActividadEnCursoMutation();
  const [actualizarEntrega] = useActualizarEntregaMutation();
  const [actualizarActividad] = useActualizarActividadMutation();  // <-- NUEVO
  const [eliminarActividad] = useEliminarActividadMutation();      // <-- NUEVO

  const hoyISO = useMemo(() => new Date().toISOString().slice(0, 10), []);

  const handleCrearActividad = async (values, { resetForm }) => {
    if (!cursoId || !cpmId) {
      alert('No hay CPM/Curso seleccionado.');
      return;
    }
    try {
      await crearActividad({
        cursoId,
        payload: { ...values, cpm_id: cpmId },
      }).unwrap();
      resetForm();
      dispatch(toggleFormulario(false));
      refetch();
    } catch (e) {
      console.error(e);
      alert('No se pudo crear la actividad');
    }
  };

  const handleVerDetalle = (actividad) => {
    dispatch(setActividadSeleccionada(actividad));
    setDetalleFiltro('entregadas'); // por defecto, las entregadas
  };

  // >>> NUEVO: actualizar fecha de entrega de la actividad
  const handleActualizarFechaEntrega = async () => {
    if (!actividadId) return;
    const nueva = prompt('Nueva fecha de entrega (YYYY-MM-DD):', actividadSeleccionada?.fecha_entrega ?? '');
    if (!nueva) return;
    try {
      const updated = await actualizarActividad({
        actividadId,
        data: { fecha_entrega: nueva },
      }).unwrap();

      // Actualizo la actividad en la lista y en la selección visible
      dispatch(setActividadSeleccionada({ ...actividadSeleccionada, ...updated }));
      refetch(); // refresca la lista (para ver el nuevo valor en la tarjeta)
      alert('Fecha de entrega actualizada.');
    } catch (e) {
      console.error(e);
      alert('No se pudo actualizar la fecha de entrega');
    }
  };

  // >>> NUEVO: eliminar actividad
  const handleEliminarActividad = async () => {
    if (!actividadId) return;
    if (!confirm('¿Eliminar esta actividad?')) return;
    try {
      await eliminarActividad(actividadId).unwrap();
      dispatch(setActividadSeleccionada(null));
      refetch(); // refresca la lista general
      alert('Actividad eliminada.');
    } catch (e) {
      console.error(e);
      alert('No se pudo eliminar la actividad');
    }
  };

  // Acciones sobre una fila de actividad_estudiante
  const marcarEntregada = async (ae) => {
    try {
      await actualizarEntrega({
        actividadEstudianteId: ae.id,
        actividadId,
        data: { entregado_en: new Date().toISOString() },
      }).unwrap();
      refetchEntregas();
    } catch (e) {
      console.error(e);
      alert('No se pudo marcar como entregada');
    }
  };

  const calificar = async (ae) => {
    if (!ae.entregado_en) {
      alert('No puedes calificar hasta que esté marcada como entregada.');
      return;
    }
    const notaStr = prompt('Nota (0-5, admite 0.0–5.0):', ae.calificacion ?? '');
    if (notaStr === null) return;
    const nota = Number(notaStr);
    if (Number.isNaN(nota) || nota < 0 || nota > 5) {
      alert('Nota inválida. Debe estar entre 0 y 5.');
      return;
    }
    try {
      await actualizarEntrega({
        actividadEstudianteId: ae.id,
        actividadId,
        data: { calificacion: nota },
      }).unwrap();
      refetchEntregas();
    } catch (e) {
      console.error(e);
      alert('No se pudo calificar');
    }
  };

  const abrirEntregable = (ae) => {
    const url = ae.entregable_url;
    if (!url) {
      alert('Este estudiante no tiene entregable adjunto.');
      return;
    }
    window.open(url, '_blank', 'noopener,noreferrer');
  };

  if (!cpm) return <p>Seleccione un curso para ver y gestionar actividades.</p>;

  return (
    <div className="activities-wrapper">
      {/* Header */}
      <div className="activities-header">
        <div className="left">
          <h2>Actividades</h2>
          <p className="subtitle">
            Curso: <strong>{cpm?.curso?.nombre_curso ?? cpm?.curso?.id}</strong> · Materia:{' '}
            <strong>{cpm?.materia?.nombre ?? cpm?.materia?.id}</strong>
          </p>
        </div>
        <div className="right">
          <button className="btn-primary" onClick={() => dispatch(toggleFormulario())}>
            {mostrarFormulario ? 'Cerrar formulario' : 'Nueva actividad'}
          </button>
        </div>
      </div>

      {/* Formulario de creación */}
      {mostrarFormulario && (
        <div className="card form-card">
          <Formik
            initialValues={{ titulo: '', descripcion: '', fecha: hoyISO, fecha_entrega: '' }}
            validationSchema={schemaActividad}
            onSubmit={handleCrearActividad}
          >
            {({ isSubmitting }) => (
              <Form className="form-actividad">
                <div className="row">
                  <div className="field">
                    <label>Título*</label>
                    <Field name="titulo" />
                    <ErrorMessage name="titulo" component="div" className="error" />
                  </div>
                  <div className="field">
                    <label>Fecha*</label>
                    <Field type="date" name="fecha" />
                    <ErrorMessage name="fecha" component="div" className="error" />
                  </div>
                  <div className="field">
                    <label>Fecha de entrega</label>
                    <Field type="date" name="fecha_entrega" />
                    <ErrorMessage name="fecha_entrega" component="div" className="error" />
                  </div>
                </div>
                <div className="row">
                  <div className="field full">
                    <label>Descripción*</label>
                    <Field as="textarea" name="descripcion" rows={4} />
                    <ErrorMessage name="descripcion" component="div" className="error" />
                  </div>
                </div>
                <div className="actions">
                  <button type="submit" className="btn-primary" disabled={isSubmitting}>
                    {isSubmitting ? 'Creando…' : 'Crear'}
                  </button>
                </div>
              </Form>
            )}
          </Formik>
        </div>
      )}

      {/* Lista de actividades */}
      <div className="card">
        {isLoading ? (
          <p>Cargando actividades…</p>
        ) : (actividades || []).length === 0 ? (
          <p>No hay actividades.</p>
        ) : (
          <div className="activities-list">
            {(actividades || []).map((a) => (
              <div className="activity-item" key={a.id}>
                <div className="info">
                  <h4 className="title">{a.titulo}</h4>
                  <p className="desc">{a.descripcion}</p>
                  <div className="meta">
                    <span>Fecha: {a.fecha}</span>
                    {a.fecha_entrega ? <span> · Entrega: {a.fecha_entrega}</span> : null}
                  </div>
                </div>
                <div className="item-actions">
                  <button className="btn-secondary" onClick={() => handleVerDetalle(a)}>
                    Ver detalle
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Detalle de actividad */}
      {actividadId && (
        <div className="card detail-card">
          <div className="detail-header">
            <h3>Entregas de la actividad</h3>

            {/* >>> NUEVO: acciones sobre la actividad */}
            <div className="detail-actions" style={{ display: 'flex', gap: 8 }}>
              <button className="btn-secondary" onClick={handleActualizarFechaEntrega}>
                Actualizar entrega
              </button>
              <button className="btn-danger" onClick={handleEliminarActividad}>
                Eliminar actividad
              </button>
            </div>
          </div>

          {/* Tabs de filtro */}
          <div className="detail-tabs">
            <button
              className={`tab ${detalleFiltro === 'entregadas' ? 'active' : ''}`}
              onClick={() => setDetalleFiltro('entregadas')}
            >
              Entregadas
            </button>
            <button
              className={`tab ${detalleFiltro === 'pendientes' ? 'active' : ''}`}
              onClick={() => setDetalleFiltro('pendientes')}
            >
              Pendientes
            </button>
            <button
              className={`tab ${detalleFiltro === 'todas' ? 'active' : ''}`}
              onClick={() => setDetalleFiltro('todas')}
            >
              Todas
            </button>
          </div>

          {loadingEntregas ? (
            <p>Cargando entregas…</p>
          ) : (
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Estudiante</th>
                    <th>Entregado</th>
                    <th>Nota</th>
                    <th>Acciones</th>
                  </tr>
                </thead>
                <tbody>
                  {(entregas || []).map((ae) => (
                    <tr key={ae.id}>
                      <td>{ae.estudiante_nombre}</td>
                      <td>{ae.entregado_en ? new Date(ae.entregado_en).toLocaleString() : '—'}</td>
                      <td>{ae.calificacion ?? '—'}</td>
                      <td className="row-actions">
                        <button
                          className="btn-secondary"
                          onClick={() => abrirEntregable(ae)}
                          disabled={!ae.entregable_url}
                          title={ae.entregable_url ? 'Abrir entregable' : 'Sin adjunto'}
                        >
                          Ver entregable
                        </button>
                        {!ae.entregado_en && (
                          <button className="btn-secondary" onClick={() => marcarEntregada(ae)}>
                            Marcar entregada
                          </button>
                        )}
                        <button
                          className="btn-secondary"
                          onClick={() => calificar(ae)}
                          disabled={!ae.entregado_en}
                          title={!ae.entregado_en ? 'Primero marca como entregada' : 'Calificar'}
                        >
                          Calificar
                        </button>
                      </td>
                    </tr>
                  ))}
                  {(entregas || []).length === 0 && (
                    <tr>
                      <td colSpan={4}>No hay entregas para este filtro.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default Activities;
