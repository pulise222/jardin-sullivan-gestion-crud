import React from 'react'
import "./MenuProfe.css"
import { useSelector, useDispatch } from 'react-redux'
import { useNavigate } from 'react-router-dom';
import { logoutUser } from '../../../../features/user/userSlice'

const MenuProfe = ({setView}) => {
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const claseActiva = useSelector(s => s.clase?.current?.status === 'running');
  const usuario = useSelector(state => state.user.user);
  const persona = useSelector(state => state.user.persona);
  
  const showUserProfile = () => {
    setView("perfil");
    // console.log("Usuario actual:", usuario);
  }

    const logout = () => {
    // Limpiar las credenciales
    dispatch(logoutUser());

    // Redirigir al login
    navigate('/login', { replace: true });
  };
  
  return (
    <aside className="sidebar">
      <div className="profile">
          <img src={persona? persona?.foto_url : "https://randomuser.me/api/portraits/men/1.jpg"} alt="Foto de perfil" className="profile-img"/>
          <span>Profe Juan</span>
      </div>
      <div className="navigation">

        <ul className='menu-profe'>
            
            <li onClick={()=>setView("inicio")}>
              <span className="icon"><ion-icon name="grid-outline"></ion-icon></span>  
              <span className="text">Inicio</span>
            </li>
            
            <li onClick={() => {
                                if (claseActiva) return; 
                                setView("cursos");
                              }} className={claseActiva ? 'disabled' : ''} >
              <span className="icon"><ion-icon name="people-outline"></ion-icon></span>
              <span className="text">Cursos</span>
            </li>
            
            {/* <li onClick={()=>setView("asistencia")}>
              <span className='icon'><ion-icon name="hand-left-outline"></ion-icon></span>
              <span className="text">Asistencia</span>
            </li>
             */}
            <li onClick={()=>setView("eventos")}>
              <span className="icon"><ion-icon name="book-outline"></ion-icon></span>
              <span className="text">Eventos</span>
            </li>

            <li onClick={showUserProfile}>
            {/* <li onClick={()=>setView("perfil")}>Perfil</li> */}
              <span className="icon"><ion-icon name="person-outline"></ion-icon></span>
              <span className="text">Perfil</span>
            </li>

            <li onClick={logout}>
              <span className="icon"><ion-icon name="book-outline"></ion-icon></span>
              <span className="text">Cerrar Sesion</span>
            </li>
        </ul>
      </div>
    </aside>
  )
}

export default MenuProfe