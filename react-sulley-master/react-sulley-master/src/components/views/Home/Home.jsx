//src/components/views/Home/Home.jsx
import { useEffect, useState, useRef, useMemo } from "react";
// Link navega entre páginas de React SIN recargar el navegador (a diferencia de <a href>)
import { Link } from "react-router-dom";
import "./Home.css";
import logo from "../../../assets/logo.png";
import pelados from "../../../assets/pelados.png";
import pelados2 from "../../../assets/pelados2.png";
import jugando from "../../../assets/niños-jugando.png";
import evento1 from '../../../assets/evento01.jpeg'

/*
  ENLACES DEL MENÚ: una sola lista que usamos para dibujar el menú Y para
  saber en qué sección estás. `id` debe coincidir con el id de cada <section>.
*/
const NAV_LINKS = [
  { id: "inicio", label: "Inicio" },
  { id: "eventos", label: "Eventos" },
  { id: "Nosotros", label: "Nosotros" },
  { id: "programas", label: "Programas" },
  { id: "contacto", label: "Contacto" },
];

/*
  HERO CONTENT: aquí editas fácilmente los textos, enlaces e imagen del
  'hero' (la primera pantalla). El JSX de más abajo solo "lee" estos datos,
  así cambias el contenido sin tocar la estructura.
*/
const HERO = {
  badgeText: 'Jardín Infantil • Desde 1 año',
  titlePrefix: 'Bienvenidos al',
  titleHighlight: 'Jardín Sullivan',
  lead:
    'Un espacio donde la educación y el corazón se unen. Acompañamos a cada niño en su desarrollo único a través del juego, la exploración y el respeto.',
  ctaPrimary: { href: '#contacto', text: 'Conocer más' },
  ctaSecondary: { href: '#programas', text: 'Ver programas' },
  image: pelados,
  // Etiquetas flotantes sobre la imagen
  chips: [
    { icon: '🌱', title: 'Aprendizaje activo', subtitle: 'Modelo pedagógico lúdico' },
    { icon: '💛', title: 'Atención personalizada', subtitle: 'Cada niño, a su ritmo' },
  ],
}

/*
  EVENTOS: datos de ejemplo. Más adelante estos datos vendrán de la API del
  backend (la app `eventos` de Django); por ahora viven aquí para diseñar.
  `color` es el color de la fecha y del botón de cada tarjeta (paleta de la marca).
*/
const EVENTS = [
  {
    title: "Feria de la ciencia",
    day: "12", month: "Oct", time: "9:00 a.m.",
    place: "Auditorio Principal",
    description: "Muestras de proyectos y experimentos de los niños.",
    image: evento1, link: "#", color: "#FEBF22",
  },
  {
    title: "Día de la familia",
    day: "20", month: "Oct", time: "8:00 a.m.",
    place: "Patio Central",
    description: "Juegos, picnic y actividades colaborativas.",
    image: evento1, link: "#", color: "#28A8E3",
  },
  {
    title: "Muestra artística",
    day: "28", month: "Oct", time: "10:00 a.m.",
    place: "Sala Multiusos",
    description: "Exposición de arte y música.",
    image: evento1, link: "#", color: "#93C524",
  },
  {
    title: "Charla de nutrición",
    day: "05", month: "Nov", time: "4:00 p.m.",
    place: "Aula 3",
    description: "Hábitos saludables en la primera infancia.",
    image: evento1, link: "#", color: "#F25141",
  },
  {
    title: "Festival de lectura",
    day: "15", month: "Nov", time: "9:30 a.m.",
    place: "Biblioteca",
    description: "Cuentacuentos y trueque de libros.",
    image: evento1, link: "#", color: "#FF8A00",
  },
];

/*
  NOSOTROS: los cuatro pilares del jardín (antes eran cuatro párrafos largos).
  `color` tiñe el círculo del ícono de cada tarjeta (colores de la paleta).
*/
const PILLARS = [
  {
    icon: "🏡",
    title: "Ambiente cálido y seguro",
    text: "Un espacio acogedor y afectivo donde los niños desarrollan habilidades sociales, emocionales y cognitivas de forma natural y divertida.",
    color: "#FEBF22",
  },
  {
    icon: "💛",
    title: "Atención personalizada",
    text: "Un equipo de profesionales capacitados acompaña a cada niño para asegurar su desarrollo integral y un crecimiento saludable.",
    color: "#F25141",
  },
  {
    icon: "🌈",
    title: "Entorno inclusivo",
    text: "Cada niño se siente valorado y respetado. Promovemos la diversidad y valores como la empatía, el respeto y la colaboración.",
    color: "#28A8E3",
  },
  {
    icon: "🎨",
    title: "Programas especializados",
    text: "Actividades artísticas, musicales y deportivas que estimulan el desarrollo físico y mental de los niños.",
    color: "#93C524",
  },
];
const Home = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [canPrev, setCanPrev] = useState(false);
  const [canNext, setCanNext] = useState(false);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(0);
  const scrollerRef = useRef(null);
  const [activeId, setActiveId] = useState("inicio");
  const heroRef = useRef(null);

  

  // ---- Carrusel de eventos ----
  // Un "paso" = el ancho de una tarjeta + el espacio entre tarjetas
  const getStep = () => {
    const el = scrollerRef.current;
    const slide = el?.querySelector(".ev-slide");
    if (!el || !slide) return 0;
    const gap = parseFloat(getComputedStyle(el.firstElementChild).columnGap) || 0;
    return slide.offsetWidth + gap;
  };

  // Las flechas avanzan o retroceden una tarjeta
  const scrollByStep = (dir = 1) => {
    const el = scrollerRef.current;
    if (!el) return;
    el.scrollBy({ left: getStep() * dir, behavior: "smooth" });
  };

  // Recalcula qué flechas se pueden usar y cuántos indicadores mostrar
  const updateArrows = () => {
    const el = scrollerRef.current;
    const step = getStep();
    if (!el || !step) return;

    const maxScroll = el.scrollWidth - el.clientWidth;
    setCanPrev(el.scrollLeft > 2);
    setCanNext(el.scrollLeft < maxScroll - 2);

    // un indicador por cada posición a la que se puede llegar
    const stops = Math.max(1, Math.round(maxScroll / step) + 1);
    setTotalPages(stops);
    setCurrentPage(Math.min(stops - 1, Math.round(el.scrollLeft / step)));
  };

  useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;
    updateArrows(); // estado inicial
    const onScroll = () => updateArrows();
    el.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", updateArrows);
    return () => {
      el.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", updateArrows);
    };
  }, []);

  // IntersectionObserver para animar las tarjetas del carrusel cuando entran al viewport
  useEffect(() => {
    const cards = document.querySelectorAll('.ev-card');
    if (!cards || cards.length === 0) return;

    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
        }
      });
    }, { root: null, rootMargin: '0px', threshold: 0.12 });

    cards.forEach((c) => io.observe(c));
    return () => io.disconnect();
  }, []);

  // Aparecer al hacer scroll (reutilizable): cualquier elemento con el atributo
  // data-reveal empieza invisible y, cuando entra en pantalla, recibe la clase
  // "is-visible". El CSS se encarga de la animación (ver "REVEAL" en Home.css).
  useEffect(() => {
    const items = document.querySelectorAll("[data-reveal]");
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            io.unobserve(entry.target); // ya apareció: dejamos de vigilarlo
          }
        });
      },
      { threshold: 0.15, rootMargin: "0px 0px -8% 0px" }
    );
    items.forEach((item) => io.observe(item));
    return () => io.disconnect();
  }, []);

  useEffect(() => {
    const root = document.getElementById("root");
    if (!root) return;
    const prevOverflow = root.style.overflow;
    root.style.overflow = "auto";
    root.classList.add("root-scroll-enabled");
    return () => {
      root.style.overflow = prevOverflow;
      root.classList.remove("root-scroll-enabled");
    };
  }, []);

  // Cerrar el menú móvil: al ensanchar la pantalla o al pulsar Escape (accesibilidad)
  useEffect(() => {
    const onResize = () => {
      if (window.innerWidth >= 900) setMenuOpen(false);
    };
    const onKey = (e) => {
      if (e.key === "Escape") setMenuOpen(false);
    };
    window.addEventListener("resize", onResize);
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("resize", onResize);
      window.removeEventListener("keydown", onKey);
    };
  }, []);

  // Scroll: (1) cambia el estilo del nav y (2) mueve el fondo/imagen del hero (parallax).
  // Usamos requestAnimationFrame para actualizar como máximo 1 vez por fotograma.
  useEffect(() => {
    let ticking = false;
    const update = () => {
      const y = window.scrollY;
      setScrolled(y > 24);
      // Guardamos el scroll en una variable CSS (--py); el CSS decide cuánto mover cada capa
      heroRef.current?.style.setProperty("--py", Math.min(y, 900));
      ticking = false;
    };
    const onScroll = () => {
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(update);
      }
    };
    update();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // "Scrollspy": marca en el menú la sección que está cruzando el centro de la pantalla
  useEffect(() => {
    const sections = NAV_LINKS
      .map((l) => document.getElementById(l.id))
      .filter(Boolean);
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) setActiveId(entry.target.id);
        });
      },
      { rootMargin: "-45% 0px -50% 0px" }
    );
    sections.forEach((s) => io.observe(s));
    return () => io.disconnect();
  }, []);

  return (
    <div className="home">
      {/* ============ NAV: barra flotante tipo "píldora" ============ */}
      <header className={`nav ${scrolled ? "scrolled" : ""}`}>
        <div className="nav-shell">
          <a className="brand" href="#inicio" aria-label="Jardín Sullivan, ir al inicio">
            <img src={logo} alt="Jardín Sullivan" />
          </a>

          {/* Botón hamburguesa (solo móvil): muestra ≡ o × según el estado del menú */}
          <button
            className="hamburger"
            type="button"
            aria-label={menuOpen ? 'Cerrar menú' : 'Abrir menú'}
            aria-controls="mainmenu"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen((o) => !o)}
          >
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
              {menuOpen ? (
                <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" />
              ) : (
                <path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              )}
            </svg>
          </button>

          {/* Enlaces: se generan desde NAV_LINKS. `--i` sirve para escalonar la animación */}
          <nav
            id="mainmenu"
            aria-label="Principal"
            className={`nav-links ${menuOpen ? "open" : ""}`}
            onClick={(e) => {
              // Si el clic fue sobre un enlace, cerramos el menú móvil
              if (e.target instanceof Element && e.target.closest("a")) {
                setMenuOpen(false);
              }
            }}
          >
            {NAV_LINKS.map((link, i) => (
              <a
                key={link.id}
                href={`#${link.id}`}
                style={{ "--i": i }}
                className={activeId === link.id ? "is-active" : undefined}
                aria-current={activeId === link.id ? "location" : undefined}
              >
                {link.label}
              </a>
            ))}
            <Link className="btn-login" to="/login" style={{ "--i": NAV_LINKS.length }}>
              <span>Inicia Sesión</span>
              <span className="btn-login-icon" aria-hidden="true">
                <i className="fas fa-arrow-right"></i>
              </span>
            </Link>
          </nav>
        </div>
      </header>

      {/* ============ HERO: primera pantalla ============ */}
      <section id="inicio" className="hero-section" ref={heroRef}>
        <div className="wrap hero-inner">

          {/* Columna de texto: cada bloque entra con un pequeño retraso (--d) */}
          <div className="hero-text">
            <div className="hero-badge reveal" style={{ "--d": ".05s" }}>
              <span className="hero-badge-dot" aria-hidden="true"></span>
              <span>{HERO.badgeText}</span>
            </div>

            <h1 className="hero-title reveal" style={{ "--d": ".15s" }}>
              {HERO.titlePrefix}{" "}
              <span className="hero-title-highlight">{HERO.titleHighlight}</span>
            </h1>

            <p className="hero-lead reveal" style={{ "--d": ".28s" }}>{HERO.lead}</p>

            <div className="hero-actions reveal" style={{ "--d": ".4s" }}>
              <a href={HERO.ctaPrimary.href} className="hero-cta-primary">
                {HERO.ctaPrimary.text}
                <i className="fas fa-arrow-right" aria-hidden="true"></i>
              </a>
              <a href={HERO.ctaSecondary.href} className="hero-cta-secondary">
                {HERO.ctaSecondary.text}
              </a>
            </div>
          </div>

          {/* Columna de imagen con etiquetas flotantes */}
          <div className="hero-media">
            <div className="hero-media-inner reveal" style={{ "--d": ".2s" }}>
              <div className="hero-img-frame">
                <img src={HERO.image} alt="Niños jugando en el Jardín Sullivan" />
              </div>

              {HERO.chips.map((chip, i) => (
                <div key={chip.title} className={`hero-chip hero-chip-${i + 1}`}>
                  <span className="hero-chip-icon" aria-hidden="true">{chip.icon}</span>
                  <div>
                    <strong>{chip.title}</strong>
                    <span>{chip.subtitle}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Indicador para bajar (solo escritorio) */}
        <a href="#eventos" className="hero-scroll" aria-label="Bajar a la sección Eventos">
          <span></span>
        </a>
      </section>

      {/* ==========================================================
          EVENTOS: sección oscura con un carrusel de tarjetas.
          Estructura:
            section.events-section
              ├─ encabezado (etiqueta + título + frase)
              ├─ .ev-scroller  → la "ventana" que se desliza horizontalmente
              │    └─ ul.ev-track → fila de tarjetas (una <li> por evento)
              └─ .ev-footer   → flecha ‹ + indicadores + flecha ›
          ========================================================== */}
      <section id="eventos" className="events-section">
        <div className="wrap">

          {/* --- Encabezado de la sección --- */}
          <div className="events-header">
            {/* "Eyebrow": textito pequeño sobre el título que da contexto */}
            <span className="events-eyebrow">Agenda</span>
            <h2 className="events-title">Eventos</h2>
            <p className="events-sub">
              Momentos para aprender, jugar y compartir en familia.
            </p>
          </div>

          {/* --- Carrusel ---
              ref={scrollerRef}: nos deja controlar este elemento desde JavaScript
              (para mover el scroll con las flechas y saber en qué tarjeta estamos).
              tabIndex={0}: permite enfocarlo con el teclado y moverlo con ← →. */}
          <div className="ev-scroller" ref={scrollerRef} tabIndex={0} aria-label="Carrusel de eventos">
            <ul className="ev-track">
              {/* .map() recorre la lista EVENTS y dibuja una tarjeta por cada evento.
                  `ev` es el evento actual e `i` su posición (0, 1, 2...). */}
              {EVENTS.map((ev, i) => (
                <li className="ev-slide" key={ev.title}>
                  {/* Pasamos datos a CSS con variables:
                      --accent → color propio de esta tarjeta
                      --i      → posición, para que las tarjetas entren una tras otra */}
                  <article className="ev-card" style={{ "--accent": ev.color, "--i": i }}>
                    <div className="ev-card-inner">
                      {/* Foto de fondo. alt="" porque es decorativa (el texto ya dice todo) */}
                      <img className="ev-card-img" src={ev.image} alt="" loading="lazy" />

                      {/* Fecha tipo calendario. aria-hidden: los lectores de pantalla
                          la saltan, porque la fecha completa ya está en .ev-meta */}
                      <div className="ev-date-chip" aria-hidden="true">
                        <strong>{ev.day}</strong>
                        <span>{ev.month}</span>
                      </div>

                      {/* Datos del evento: fecha · hora · lugar */}
                      <p className="ev-meta">{ev.day} {ev.month} · {ev.time} · {ev.place}</p>
                      <h3 className="ev-title">{ev.title}</h3>

                      {/* La descripción va dentro de un contenedor para poder
                          animar su apertura al pasar el mouse (ver CSS) */}
                      <div className="ev-desc-wrap">
                        <p className="ev-desc">{ev.description}</p>
                      </div>

                      {/* `ev.link && (...)` = "si hay enlace, dibuja el botón" */}
                      {ev.link && (
                        <a className="ev-link" href={ev.link}>
                          Ver detalle
                          <span className="ev-link-icon" aria-hidden="true">
                            <i className="fas fa-arrow-right"></i>
                          </span>
                        </a>
                      )}
                    </div>
                  </article>
                </li>
              ))}
            </ul>
          </div>

          {/* --- Controles: ‹ flecha · indicadores · flecha › ---
              Van DEBAJO del carrusel para que el menú flotante nunca los tape. */}
          <div className="ev-footer">
            {/* Flecha anterior. `disabled` la apaga cuando ya estamos en la primera tarjeta */}
            <button
              type="button"
              className="ev-btn"
              aria-label="Evento anterior"
              onClick={() => scrollByStep(-1)}
              disabled={!canPrev}
            >
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M15 5l-7 7 7 7" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>

            {/* Indicadores: un punto por cada posición del carrusel.
                Array.from({ length: n }) crea una lista de n elementos para recorrer.
                El punto activo (currentPage) se alarga y se pinta de amarillo. */}
            <div className="ev-indicators" role="group" aria-label="Posición en el carrusel">
              {Array.from({ length: totalPages }).map((_, i) => (
                <button
                  key={i}
                  type="button"
                  className={`ev-indicator ${currentPage === i ? "is-active" : ""}`}
                  aria-label={`Ir al evento ${i + 1}`}
                  aria-current={currentPage === i ? "true" : undefined}
                  onClick={() => {
                    // Al pulsar un punto, desliza el carrusel hasta esa tarjeta
                    const el = scrollerRef.current;
                    if (!el) return;
                    el.scrollTo({ left: getStep() * i, behavior: "smooth" });
                  }}
                />
              ))}
            </div>

            {/* Flecha siguiente. Se apaga al llegar a la última tarjeta */}
            <button
              type="button"
              className="ev-btn"
              aria-label="Siguiente evento"
              onClick={() => scrollByStep(1)}
              disabled={!canNext}
            >
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
                <path d="M9 5l7 7-7 7" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </button>
          </div>
        </div>
      </section>

      {/* ==========================================================
          NOSOTROS: presentación del jardín.
          Estructura:
            .nos-intro    → mosaico de fotos + texto principal
            .nos-pillars  → 4 tarjetas con lo que nos define
            .nos-quote    → frase destacada de cierre
          Los elementos con `data-reveal` aparecen animados al hacer scroll
          (el retraso de cada uno se controla con la variable --d).
          ========================================================== */}
      <section className="nos-section" id="Nosotros">
        <div className="wrap">

          {/* --- Fotos + texto --- */}
          <div className="nos-intro">
            {/* Mosaico: una foto grande y otra pequeña que se superpone */}
            <div className="nos-media" data-reveal="left">
              <div className="nos-photo nos-photo-main">
                <img src={pelados2} alt="Profesora y niños disfrazados posando en el jardín" loading="lazy" />
              </div>
              <div className="nos-photo nos-photo-small">
                <img src={jugando} alt="Niños jugando al aire libre" loading="lazy" />
              </div>
            </div>

            <div className="nos-text">
              <span className="nos-eyebrow" data-reveal>Nosotros</span>
              <h2 className="nos-title" data-reveal style={{ "--d": ".08s" }}>
                Creemos en aprender{" "}
                <span className="nos-title-highlight">jugando</span>
              </h2>
              <p className="nos-lead" data-reveal style={{ "--d": ".16s" }}>
                En Jardín Sullivan creemos en el aprendizaje activo, el juego y
                la atención personalizada. Nuestro equipo trabaja en equipo para
                crear experiencias que fomenten la curiosidad, la creatividad y
                el respeto por los demás.
              </p>
              <p className="nos-body" data-reveal style={{ "--d": ".24s" }}>
                Nuestro proyecto educativo integra actividades artísticas,
                experimentos y salidas presenciales que enriquecen el desarrollo
                integral de los niños.
              </p>
            </div>
          </div>

          {/* --- Pilares: PILLARS.map() dibuja una tarjeta por cada elemento ---
              --tone le pasa al CSS el color de esa tarjeta */}
          <ul className="nos-pillars">
            {PILLARS.map((pillar, i) => (
              <li
                key={pillar.title}
                className="nos-pillar"
                data-reveal
                style={{ "--tone": pillar.color, "--d": `${i * 0.08}s` }}
              >
                <span className="nos-pillar-icon" aria-hidden="true">{pillar.icon}</span>
                <h3>{pillar.title}</h3>
                <p>{pillar.text}</p>
              </li>
            ))}
          </ul>

          {/* --- Frase de cierre --- */}
          <blockquote className="nos-quote" data-reveal>
            <p className="nos-quote-text">
              Prepararlos no solo para la escuela,{" "}
              <span className="nos-title-highlight">sino para la vida</span>.
            </p>
            <p className="nos-quote-sub">
              Ayudándoles a construir una base sólida de confianza y autoestima.
            </p>
          </blockquote>
        </div>
      </section>

      {/* GRUPOS */}
      <section className="grupos-section" id="programas">
        <div className="wrap">
          <h2 className="title-center">Nuestros Grupos</h2>
          <div className="grupos-grid">
            <article className="grupo-card">
              <h3>Organiza</h3>
              <p className="edad">Edad 1 a 3 años</p>
              <p className="descripcion">
                Pequeños exploradores que describen el mundo a través de los
                sentidos.
              </p>
              <ul className="actividades">
                <li>Juegos sensoriales</li>
                <li>Rondas infantiles</li>
                <li>Manipulación de materiales</li>
                <li>Desarrollo de autonomía</li>
              </ul>
            </article>

            <article className="grupo-card">
              <h3>Capullitos</h3>
              <p className="edad">Edad 3 a 4 años</p>
              <p className="descripcion">
                Potentes comunicadores que expanden su mundo a través del
                lenguaje.
              </p>
              <ul className="actividades">
                <li>Dramatizaciones</li>
                <li>Actividades artísticas</li>
                <li>Juegos colaborativos</li>
                <li>Desarrollo de independencia</li>
              </ul>
            </article>

            <article className="grupo-card">
              <h3>Hormiguitas</h3>
              <p className="edad">Edad 4 a 5 años</p>
              <p className="descripcion">
                Jóvenes científicos naturales que exploran mediante proyectos.
              </p>
              <ul className="actividades">
                <li>Trabajo en equipo</li>
                <li>Resolución de desafíos</li>
                <li>Cultivo de huertas</li>
                <li>Pensamiento crítico</li>
              </ul>
            </article>

            <article className="grupo-card">
              <h3>Colonizadores</h3>
              <p className="edad">Edad 5 a 6 años</p>
              <p className="descripcion">
                Futuros líderes preparados para conquistar nuevos retos.
              </p>
              <ul className="actividades">
                <li>Conceptos académicos</li>
                <li>Proyectos innovadores</li>
                <li>Tecnología responsable</li>
                <li>Desarrollo de resiliencia</li>
              </ul>
            </article>
          </div>
        </div>
      </section>

      {/* BENEFICIOS */}
      <section className="beneficios-section">
        <div className="wrap beneficios-grid">
          <div className="beneficio-item">
            <div
              className="beneficio-circulo"
              style={{ backgroundColor: "#F25141" }}
            >
              🎓
            </div>
            <h3>Excelentes docentes</h3>
            <p>
              Todos nuestros educadores son profesionales en pedagogía infantil
              con amplia experiencia en primera infancia.
            </p>
          </div>

          <div className="beneficio-item">
            <div
              className="beneficio-circulo"
              style={{ backgroundColor: "#93C524" }}
            >
              🍎
            </div>
            <h3>Alimentación Saludable</h3>
            <p>
              Cada día servimos menús balanceados preparados con ingredientes
              frescos y seguimos estrictos protocolos de higiene.
            </p>
          </div>

          <div className="beneficio-item">
            <div
              className="beneficio-circulo"
              style={{ backgroundColor: "#28A8E3" }}
            >
              🎮
            </div>
            <h3>Aprendizaje Jugando</h3>
            <p>
              Usamos juegos y actividades creativas para que los niños aprendan
              naturalmente y con alegría.
            </p>
          </div>
        </div>
      </section>

      {/* BANNER MATRICULACIÓN */}
      <section className="matricula-banner-horizontal">
        <div className="wrap banner-inner">
          <h2>¿DESEAS MATRICULAR EN NUESTRO JARDÍN?</h2>
          <a href="#contacto" className="matricula-btn-horizontal">
            MÁS INFORMACIÓN
          </a>
        </div>
      </section>

      {/* METODOLOGÍA */}
      <section className="metodologia-section">
        <div className="wrap metodo-grid">
          <div className="metodo-text">
            <h2 className="titulo-metodologia">Nuestra Metodología</h2>
            <p className="texto-metodologia">
              Nuestro enfoque educativo está basado en el método de aprendizaje
              activo, donde los niños son los protagonistas de su propio
              desarrollo. Creemos en la importancia del juego como herramienta
              fundamental para el aprendizaje, ya que permite desarrollar
              habilidades sociales, emocionales y cognitivas de manera natural.
            </p>
          </div>
          <div className="metodo-img">
            <img src={pelados2} alt="Profesora con niños" />
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="footer-section" id="contacto">
        <div className="wrap footer-grid">
          <div className="footer-left">
            <h3>Contacto</h3>
            <div className="mb">
              <p>
                <strong>Jardín Infantil Sullivan</strong>
              </p>
              <p>© 2024. | Políticas de privacidad</p>
              <p>Dirección: Calle 45 #12-34, Bogotá</p>
            </div>

            <div className="mb">
              <h3>Horarios de Atención</h3>
              <p>Lunes a viernes: 7:30 a.m. - 5:00 p.m.</p>
              <p>Sábados: 8:00 a.m. - 12:00 m.</p>
            </div>

            <div>
              <h3>Línea Administrativa</h3>
              <p>Teléfono: (601) 555 1324</p>
              <p>Celular: 300 455 7890</p>
              <p>Correos:</p>
              <br />
              <ul className="dotless">
                <li>Coordinación: coordinacion@sullivan.edu.co</li>
                <li>Psicología: psicologia@sullivan.edu.co</li>
                <li>Secretaría: secretaria@sullivan.edu.co</li>
              </ul>
            </div>
          </div>

          <div className="footer-right">
            <div className="footer-right">
              <div
                className="map-embed"
                role="region"
                aria-label="Mapa de ubicación Jardín Sullivan"
              >
                <iframe
                  title="Ubicación Jardín Sullivan"
                  loading="lazy"
                  allowFullScreen
                  referrerPolicy="no-referrer-when-downgrade"
                  src="https://www.google.com/maps?q=Sullivan+Kinder%2C+Carrera+87%2C+Cl.+53+Sur+%2349A%2C+Bogot%C3%A1%2C+Cundinamarca%2C+Colombia&output=embed">
                  </iframe>
              </div>
            </div>
          </div>
        </div>

        <div className="center mt">
          <a href="#inicio" className="btn-to-top">
            ↑ Inicio
          </a>
        </div>
      </footer>
    </div>
  );
};

export default Home;
