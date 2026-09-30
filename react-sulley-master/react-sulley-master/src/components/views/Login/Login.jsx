// src/components/Login.jsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { useLoginUserMutation } from '../../../features/user/userApi';
import { setCredentials, setPersona  } from '../../../features/user/userSlice';
import { useLazyGetMyPersonaQuery } from '../../../features/people/personApi';
import './login.css';

const Login = () => {
  const [form, setForm] = useState({ username: '', password: '' });
  const [login, { isLoading }] = useLoginUserMutation();
  const [fetchMyPersona] = useLazyGetMyPersonaQuery(); // <- lazy para controlarlo
  
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const handleChange = (e) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const { username, password } = form;
    if (!username || !password) {
      return alert('Completa usuario y contraseña');
    }

    try {
       const { access, refresh, usuario } = await login(form).unwrap()
       
      // guardamos tokens y user
      localStorage.setItem('access', access)
      localStorage.setItem('refresh', refresh)
      sessionStorage.setItem('user', JSON.stringify(usuario))
      dispatch(setCredentials({ user: usuario, access, refresh }))
    
      // Traer la Persona asociada al usuario autenticado
      try {
        const persona = await fetchMyPersona().unwrap();
        sessionStorage.setItem('persona', JSON.stringify(persona));
        dispatch(setPersona(persona));
      } catch (e) {
        // Puede no existir Persona (por rol distinto); no es bloqueo
        console.log('Login: ', e);
        sessionStorage.removeItem('persona');
        dispatch(setPersona(null));
      }


      // Redirigir segun rol
      switch (usuario.rol) {
        case 'Administrador': navigate('/admin/'); break;
        case 'Profesor':      navigate('/profesor/'); break;
        case 'Acudiente':     navigate('/acudiente/'); break;
        default:              navigate('/');
      }
    } catch (err) {
      alert('Credenciales incorrectas');
      console.error(err);
    }
  };

  return (
    <div className="login-wrapper">
      <button className="inicio" onClick={() => navigate('/')}>Inicio</button>
      <div className="logo">
        <img src="/src/assets/logo.png" alt="logo-jardin" />
      </div>
      <div className="login-container">
        <h2>Iniciar Sesion</h2>
        <form onSubmit={handleSubmit}>
          <label htmlFor="username">Usuario:</label>
          <input
            type="text"
            id="username"
            name="username"
            value={form.username}
            onChange={handleChange}
            autoComplete="username"
          />

          <label >Contraseña:</label>
          <input
            type="password"
            id="password"
            name="password"
            value={form.password}
            onChange={handleChange}
            autoComplete="current-password"
          />

          <button type="submit" className="boton-login" disabled={isLoading}>
            {isLoading ? 'Cargando...' : 'Iniciar Sesion'}
          </button>
        </form>
        <p> ¿No te acuerdas de tu contraseña? <a href="/cambiar-contraseña">Recuperar Contraseña</a></p>
      </div>
    </div>
  );
};

export default Login;
