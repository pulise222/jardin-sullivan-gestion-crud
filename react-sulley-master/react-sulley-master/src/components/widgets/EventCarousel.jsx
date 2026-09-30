import React, { useMemo, useRef, useState } from 'react';
import { useGetEventosProximosQuery } from '../../features/eventos/eventosApi';
import './css/EventCarousel.css';

const EventCarousel = ({ limit = 10 }) => {
  const { data = [], isLoading, isError } = useGetEventosProximosQuery({ limit });
  const list = useMemo(() => data || [], [data]);
  const scrollerRef = useRef(null);
  const [openIdx, setOpenIdx] = useState(null);

  const scrollBy = (dir = 1) => {
    const el = scrollerRef.current;
    if (!el) return;
    const amount = Math.min(400, el.clientWidth * 0.9);
    el.scrollBy({ left: dir * amount, behavior: 'smooth' });
  };

  if (isLoading) return <p>Cargando eventos…</p>;
  if (isError) return <p>Error al cargar eventos</p>;
  if (list.length === 0) return <p>No hay eventos próximos.</p>;

  return (
    <div className="event-carousel">
      <div className="ec-header">
        <h3>Próximos eventos</h3>
        <div className="ec-controls">
          <button className="ec-btn" onClick={() => scrollBy(-1)} aria-label="Anterior">‹</button>
          <button className="ec-btn" onClick={() => scrollBy(1)} aria-label="Siguiente">›</button>
        </div>
      </div>

      <div className="ec-strip" ref={scrollerRef}>
        {list.map((ev, idx) => (
          <div className="ec-card" key={ev.id_evento ?? ev.id ?? idx} onClick={() => setOpenIdx(idx)}>
            <div className="ec-thumb">
              {ev.imagen_url ? (
                <img src={ev.imagen_url} alt={ev.titulo} />
              ) : (
                <div className="ec-placeholder">Sin imagen</div>
              )}
            </div>
            <div className="ec-meta">
              <div className="ec-title">{ev.titulo}</div>
              <div className="ec-date">{ev.fecha_inicio}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Panel de detalle simple */}
      {openIdx !== null && list[openIdx] && (
        <div className="ec-detail" role="dialog" aria-modal="true">
          <div className="ecd-header">
            <h4>{list[openIdx].titulo}</h4>
            <button className="ec-close" onClick={() => setOpenIdx(null)}>✕</button>
          </div>
          <div className="ecd-body">
            <p><strong>Fecha:</strong> {list[openIdx].fecha_inicio}</p>
            <p className="ecd-desc">{list[openIdx].descripcion || 'Sin descripción'}</p>
            {list[openIdx].imagen_url && (
              <img className="ecd-img" src={list[openIdx].imagen_url} alt={list[openIdx].titulo} />
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default EventCarousel;
