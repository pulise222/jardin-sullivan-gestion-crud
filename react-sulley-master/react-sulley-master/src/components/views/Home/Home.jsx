//src/components/views/Home/Home.jsx
import { useEffect, useState, useRef, useMemo } from "react";
// Link navega entre páginas de React SIN recargar el navegador (a diferencia de <a href>)
import { Link } from "react-router-dom";
import "./Home.css";
import logo from "../../../assets/logo.png";
import pelados from "../../../assets/pelados.png";
import pelados2 from "../../../assets/pelados2.png";
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

  

  const scrollByStep = (dir = 1) => {
    const el = scrollerRef.current;
    if (!el) return;
    const step = el.clientWidth; // desplaza un “viewport” del carrusel
    el.scrollBy({ left: step * dir, behavior: "smooth" });
  };

  const updateArrows = () => {
  const el = scrollerRef.current;
  if (!el) return;

  const atStart = el.scrollLeft <= 2;
  const atEnd = el.scrollLeft + el.clientWidth >= el.scrollWidth - 2;
  setCanPrev(!atStart);
  setCanNext(!atEnd);

  // indicadores (páginas = ancho total / ancho visible)
  const step = el.clientWidth;
  const pages = Math.max(1, Math.ceil(el.scrollWidth / step));
  setTotalPages(pages);
  const page = Math.round(el.scrollLeft / step);
  setCurrentPage(Math.min(pages - 1, page));
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
 }, [/* si cargas desde API: */ /* eventos.length */]);

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

  // Efecto tilt leve por mouse: rota la tarjeta interior según posición del cursor
  useEffect(() => {
    const inners = document.querySelectorAll('.ev-card-inner');
    if (!inners || inners.length === 0) return;

    function handleMove(e) {
      const card = e.currentTarget;
      const rect = card.getBoundingClientRect();
      const px = (e.clientX - rect.left) / rect.width; // 0..1
      const py = (e.clientY - rect.top) / rect.height; // 0..1
      const rx = (py - 0.5) * 6; // rot X
      const ry = (px - 0.5) * -8; // rot Y
      card.style.transform = `rotateX(${rx}deg) rotateY(${ry}deg) translateZ(0)`;
    }

    function handleLeave(e) {
      e.currentTarget.style.transform = '';
    }

    inners.forEach((el) => {
      const parent = el.closest('.ev-card');
      if (!parent) return;
      parent.addEventListener('mousemove', handleMove.bind(el));
      parent.addEventListener('mouseleave', handleLeave.bind(el));
      parent.addEventListener('blur', handleLeave.bind(el));
    });

    return () => {
      inners.forEach((el) => {
        const parent = el.closest('.ev-card');
        if (!parent) return;
        parent.removeEventListener('mousemove', handleMove.bind(el));
        parent.removeEventListener('mouseleave', handleLeave.bind(el));
        parent.removeEventListener('blur', handleLeave.bind(el));
      });
    };
  }, []);

  // Reveal para la sección Nosotros
  useEffect(() => {
    const nosSection = document.querySelector('.nos-section');
    if (!nosSection) return;
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) nosSection.classList.add('is-visible');
      });
    }, { threshold: 0.12 });
    io.observe(nosSection);
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

      {/*Eventos*/}
<section id="eventos" className="events-section">
  <div className="wrap events-header">
    <h2 className="events-title">Eventos</h2>
  </div>

  <div className="wrap">
    <div className="ev-wrap">
      {/* Flecha izquierda superpuesta */}
      <button
        type="button"
        className={`ev-btn ev-prev ev-overlay ${!canPrev ? "is-disabled" : ""}`}
        aria-label="Evento anterior"
        onClick={() => scrollByStep(-1)}
        disabled={!canPrev}
        aria-disabled={!canPrev}
      >
        ‹
      </button>

      <div className="ev-scroller" ref={scrollerRef} tabIndex={0} aria-label="Carrusel de eventos">
        <ul className="ev-track">
          {[
            {
              title: "Feria de la ciencia",
              date: "12 Oct 2025, 9:00 a.m.",
              place: "Auditorio Principal",
              description: "Muestras de proyectos y experimentos de los niños.",
              image: "/Imagen/evento1.jpg",
              link: "#",
            },
            {
              title: "Día de la familia",
              date: "20 Oct 2025, 8:00 a.m.",
              place: "Patio Central",
              description: "Juegos, picnic y actividades colaborativas.",
              image: "/Imagen/evento2.jpg",
              link: "#",
            },
            {
              title: "Muestra artística",
              date: "28 Oct 2025, 10:00 a.m.",
              place: "Sala Multiusos",
              description: "Exposición de arte y música.",
              image: "/Imagen/evento3.jpg",
              link: "#",
            },
            {
              title: "Charla de nutrición",
              date: "05 Nov 2025, 4:00 p.m.",
              place: "Aula 3",
              description: "Hábitos saludables en la primera infancia.",
              image: "/Imagen/evento4.jpg",
              link: "#",
            },
            {
              title: "Festival de lectura",
              date: "15 Nov 2025, 9:30 a.m.",
              place: "Biblioteca",
              description: "Cuentacuentos y trueque de libros.",
              image: "/Imagen/evento5.jpg",
              link: "#",
            },
          ].map((ev, i) => (
            <li className="ev-slide" key={i}>
              <article className="ev-card" tabIndex={0} aria-label={`Evento ${ev.title}`}>
                <div className="ev-card-inner">
                  <div className="ev-card-media">
                    {ev.image ? <img src={evento1} alt="" aria-hidden="true" /> : <div className="ev-card-fallback" />}
                  </div>
                  <div className="ev-card-body">
                    <h3 className="ev-title">{ev.title}</h3>
                    <p className="ev-date">{ev.date} · {ev.place}</p>
                    <p className="ev-desc">{ev.description}</p>
                    {ev.link && <a className="ev-link" href={ev.link}>Ver detalle</a>}
                  </div>
                </div>

                {/* Overlay interactivo que aparece al hover/focus */}
                <div className="ev-card-overlay" aria-hidden="true">
                  <strong>{ev.title}</strong>
                  <span style={{marginLeft:'.6rem', color:'rgba(27,49,88,.7)'}}>{ev.date}</span>
                </div>
              </article>
            </li>
          ))}
        </ul>
      </div>

      {/* Indicadores tipo “líneas” (fuera del <ul>) */}
      <div className="ev-indicators" role="tablist" aria-label="Páginas del carrusel">
        {Array.from({ length: totalPages }).map((_, i) => (
          <button
            key={i}
            type="button"
            className={`ev-indicator ${currentPage === i ? "is-active" : ""}`}
            aria-label={`Ir a página ${i + 1}`}
            aria-current={currentPage === i ? "true" : undefined}
            onClick={() => {
              const el = scrollerRef.current;
              if (!el) return;
              el.scrollTo({ left: el.clientWidth * i, behavior: "smooth" });
            }}
          />
        ))}
      </div>

      {/* Flecha derecha superpuesta */}
      <button
        type="button"
        className={`ev-btn ev-next ev-overlay ${!canNext ? "is-disabled" : ""}`}
        aria-label="Siguiente evento"
        onClick={() => scrollByStep(1)}
        disabled={!canNext}
        aria-disabled={!canNext}
      >
        ›
      </button>
    </div>
  </div>
</section>

      {/* NOSOTROS */}
      <section className="nos-section" id="Nosotros">
        <div className="wrap nos-inner">
          <div className="nos-text">
            <h2>Nosotros</h2>
            <p>
              En Jardín Sullivan creemos en el aprendizaje activo, el juego y
              la atención personalizada. Nuestro equipo trabaja en equipo para
              crear experiencias que fomenten la curiosidad, la creatividad y
              el respeto por los demás.
            </p>
            <p>
              Nuestro proyecto educativo integra actividades artísticas,
              experimentos y salidas presenciales que enriquecen el desarrollo
              integral de los niños.
            </p>
          </div>

          <div className="nos-media">
            <img src={pelados2} alt="Profesora con niños" />
          </div>
        </div>
      </section>

      {/* TEXTO 2 COLUMNAS */}
      <section className="wrap two-cols">
        <div className="col">
          <p>
            En nuestro Jardín Infantil, ofrecemos un ambiente cálido y acogedor
            donde los niños pueden desarrollar sus habilidades sociales,
            emocionales y cognitivas de manera natural y divertida. Nuestro
            enfoque educativo está basado en la curiosidad y la exploración,
            fomentando la creatividad y el aprendizaje a través del juego.
          </p>
          <p>
            Contamos con un equipo de profesionales capacitados que se esfuerzan
            por brindar atención personalizada a cada niño, asegurando su
            desarrollo integral y un crecimiento saludable en un ambiente seguro
            y afectivo.
          </p>
        </div>

        <div className="col">
          <p>
            Además, en nuestro Jardín Infantil nos enfocamos en crear un entorno
            inclusivo donde cada niño se sienta valorado y respetado. Promovemos
            la diversidad y enseñamos a los pequeños a apreciar las diferencias,
            fomentando valores como la empatía, el respeto y la colaboración.
          </p>
          <p>
            También contamos con programas especializados que incluyen
            actividades artísticas, musicales y deportivas, diseñadas para
            estimular el desarrollo físico y mental de los niños. Nuestro
            objetivo es prepararlos no solo para la escuela, sino para la vida,
            ayudándoles a construir una base sólida de confianza y autoestima.
          </p>
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
