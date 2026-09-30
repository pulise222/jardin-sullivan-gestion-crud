// src/components/views/Admin/EventsAdmin.jsx

import React, { useMemo, useState } from 'react';
import {
  useGetEventosQuery,
  useCreateEventoMutation,
  useUpdateEventoMutation,
  useDeleteEventoMutation
} from '../../../features/eventos/eventosApi';
import './css/EventsAdmin.css';

function toLocalInputValue(iso) {
  if (!iso) return '';
  const d = new Date(iso);
  const pad = (n) => String(n).padStart(2, '0');
  // datetime-local → YYYY-MM-DDTHH:mm (sin zona)
  return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}
function fromLocalToISO(localValue) {
  // Toma el valor de <input type="datetime-local"> (naive) y lo convierte a ISO UTC
  if (!localValue) return null;
  const d = new Date(localValue);
  return d.toISOString(); // DRF recibe UTC ISO 8601
}

const EMPTY = { titulo: '', descripcion: '', fecha_inicio_local: '', file: null };

const EventsAdmin = () => {
  const { data = [], isLoading, isError } = useGetEventosQuery();
  const eventos = useMemo(() => data || [], [data]);

  const [createEvento, { isLoading: creating }] = useCreateEventoMutation();
  const [updateEvento, { isLoading: updating }] = useUpdateEventoMutation();
  const [deleteEvento, { isLoading: deleting }] = useDeleteEventoMutation();

  const [form, setForm] = useState(EMPTY);
  const [preview, setPreview] = useState(null);
  const [editing, setEditing] = useState(null); // objeto evento en edición o null

  const onPickFile = (file) => {
    setForm((f) => ({ ...f, file }));
    if (file) {
      const url = URL.createObjectURL(file);
      setPreview(url);
    } else {
      setPreview(null);
    }
  };

  const startCreate = () => {
    setEditing(null);
    setForm(EMPTY);
    setPreview(null);
  };

  const startEdit = (ev) => {
    setEditing(ev);
    setForm({
      titulo: ev.titulo ?? '',
      descripcion: ev.descripcion ?? '',
      fecha_inicio_local: toLocalInputValue(ev.fecha_inicio),
      file: null, // sólo si el admin sube uno nuevo
    });
    setPreview(ev.imagen_url || null);
  };

  const submit = async (e) => {
    e.preventDefault();
    const fecha_inicio_iso = fromLocalToISO(form.fecha_inicio_local);

    try {
      if (editing) {
        await updateEvento({
          id_evento: editing.id_evento ?? editing.id,
          titulo: form.titulo,
          descripcion: form.descripcion,
          fecha_inicio_iso,
          file: form.file || undefined,
        }).unwrap();
        alert('Evento actualizado');
      } else {
        await createEvento({
          titulo: form.titulo,
          descripcion: form.descripcion,
          fecha_inicio_iso,
          file: form.file || undefined,
        }).unwrap();
        alert('Evento creado');
      }
      startCreate(); // limpia el formulario
    } catch (err) {
      console.error(err);
      alert('No se pudo guardar el evento');
    }
  };

  const remove = async (ev) => {
    if (!confirm(`¿Eliminar evento "${ev.titulo}"?`)) return;
    try {
      await deleteEvento(ev.id_evento ?? ev.id).unwrap();
      if (editing && (editing.id_evento ?? editing.id) === (ev.id_evento ?? ev.id)) {
        startCreate();
      }
    } catch (err) {
      console.error(err);
      alert('No se pudo eliminar');
    }
  };

  return (
    <div className="events-admin">
      <div className="ea-grid">
        <div className="ea-left">
          <div className="ea-head">
            <h2>Eventos</h2>
            <button className="btn" onClick={startCreate}>Nuevo</button>
          </div>

          {isLoading ? (
            <p>Cargando…</p>
          ) : isError ? (
            <p>Error al cargar eventos</p>
          ) : (
            <table className="ea-table">
              <thead>
                <tr>
                  <th>Imagen</th>
                  <th>Título</th>
                  <th>Fecha Inicio</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {eventos.map((ev) => (
                  <tr key={ev.id_evento ?? ev.id}>
                    <td>
                      {ev.imagen_url ? (
                        <img className="ea-thumb" src={ev.imagen_url} alt={ev.titulo} />
                      ) : (
                        <div className="ea-noimg">—</div>
                      )}
                    </td>
                    <td>{ev.titulo}</td>
                    <td>{ev.fecha_inicio}</td>
                    <td className="ea-actions">
                      <button className="btn" onClick={() => startEdit(ev)}>Editar</button>
                      <button className="btn danger" onClick={() => remove(ev)} disabled={deleting}>Eliminar</button>
                    </td>
                  </tr>
                ))}
                {eventos.length === 0 && (
                  <tr><td colSpan={4}>No hay eventos.</td></tr>
                )}
              </tbody>
            </table>
          )}
        </div>

        <div className="ea-right">
          <h3>{editing ? 'Editar evento' : 'Nuevo evento'}</h3>
          <form onSubmit={submit} className="ea-form">
            <label>
              Título*
              <input
                type="text"
                value={form.titulo}
                onChange={(e) => setForm((f) => ({ ...f, titulo: e.target.value }))}
                required
              />
            </label>

            <label>
              Descripción
              <textarea
                rows={4}
                value={form.descripcion}
                onChange={(e) => setForm((f) => ({ ...f, descripcion: e.target.value }))}
              />
            </label>

            <label>
              Fecha de inicio*
              <input
                type="datetime-local"
                value={form.fecha_inicio_local}
                onChange={(e) => setForm((f) => ({ ...f, fecha_inicio_local: e.target.value }))}
                required
              />
            </label>

            <label>
              Imagen (JPG/PNG)
              <input
                type="file"
                accept="image/*"
                onChange={(e) => onPickFile(e.target.files?.[0] || null)}
              />
            </label>

            {preview && (
              <div className="ea-preview">
                <img src={preview} alt="Vista previa" />
              </div>
            )}

            <div className="ea-form-actions">
              <button className="btn primary" type="submit" disabled={creating || updating}>
                {editing ? (updating ? 'Guardando…' : 'Guardar cambios') : (creating ? 'Creando…' : 'Crear evento')}
              </button>
              {editing && (
                <button type="button" className="btn" onClick={startCreate}>
                  Cancelar edición
                </button>
              )}
            </div>
          </form>
          {/* <p className="ea-tip">Tip: la hora se guarda en UTC (DRF). Verifica tu zona horaria en el backend.</p> */}
        </div>
      </div>
    </div>
  );
};

export default EventsAdmin;