// src/components/MenuAdmin.jsx
import React from 'react';
import { NavLink } from 'react-router-dom';
import './MenuAdmin.css'; // Importa el CSS
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { logoutUser } from '../../../../features/user/userSlice'

const MenuAdmin = ({ setView, currentView }) => {
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const persona = useSelector(state => state.user.persona) || {};
  console.log(persona);
  
  const logout = () => {
    // Limpiar las credenciales
    dispatch(logoutUser());

    // Redirigir al login
    navigate('/login', { replace: true });
  };

  return (
    <aside className="admin-menu">
      <h3>Admin: {persona.nombre || 'Administrador'}</h3>
      <ul>

        <li onClick={() => setView('estudiantes')} className={currentView === 'estudiantes' ? 'active' : ''}>
          <span className="text">Estudiantes</span>
        </li>

        <li onClick={() => setView('personas')} className={currentView === 'personas' ? 'active' : ''}>
          <span className="text">Personas</span>
        </li>

        <li onClick={() => setView('materias')} className={currentView === 'materias' ? 'active' : ''}>
          <span className="text">Materias</span>
        </li>
        <li onClick={() => setView('asignaciones')} className={currentView === 'asignaciones' ? 'active' : ''}>
          <span className="text">Asignaciones</span>
        </li>
        <li onClick={() => setView('eventos')} className={currentView === 'eventos' ? 'active' : ''}>
          <span className="text">Eventos</span>
        </li>
        <li onClick={logout}>
          <span className="text">Cerrar Sesion</span>
        </li>
      </ul>
    </aside>
  );
};


export default MenuAdmin;
