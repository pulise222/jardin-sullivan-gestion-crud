// src/views/components/Profesor/DashboardHome.jsx
import React from 'react';

const DashboardHome = () => (
  <div className="main-content">
    <div className="navbar">
      <div className="greeting">
        <h1>Hola, Profe Juan</h1>
        <div className="notification">
          <img
            src="https://img.icons8.com/ios/452/bell.png"
            alt="Notificaciones"
          />
        </div>
      </div>
    </div>

    <div className="dashboard-cards">
      <div className="card">
        <h3>Total estudiantes</h3>
        <p>25</p>
      </div>
      <div className="card">
        <h3>Clases hoy</h3>
        <p>3</p>
      </div>
      <div className="card">
        <h3>Actividades pendientes</h3>
        <p>4</p>
      </div>
    </div>

    <div className="attendance-section">
      <h2>Asistencia semanal</h2>
      <div className="attendance-circle">
        <p>90%</p>
      </div>
    </div>

    <div className="recent-activities">
      <h2>Actividades Recientes</h2>
      <ul>
        <li>Dibujo de animales</li>
        <li>Juego con bloques</li>
        <li>Collage creativo</li>
        <li>Cuento infantil</li>
      </ul>
    </div>
  </div>
);

export default DashboardHome;
