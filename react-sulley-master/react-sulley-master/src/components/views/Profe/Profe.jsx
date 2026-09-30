// src/components/views/Profe/Profe.jsx
import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import MenuProfe from '../../container/Menu/MenuProfe/MenuProfe';
import './css/Profe.css';


import DashboardProfesor from './DashboardProfesor';
import CoursesList from './CoursesList';
import CourseDetail from './CourseDetail';
import Attendance from './Attendance';
import Activities from './Activities';
import Profile from './Profile';

import {
  useGetCourseByTeacherQuery,
  useGetCourseWithStudentsQuery,
} from '../../../features/cursos/cursosApi';
import {
  coursesByTeacher,
  setSelectedCourse,
  setCursoProfesorMateria
} from '../../../features/cursos/cursosSlice';
import EventCarousel from '../../widgets/EventCarousel';

const Profe = () => {
  const dispatch = useDispatch()
  // Estado local pa ra controlar la "vista" actual
  const [view, setView] = useState('inicio');
  
    // Estado local para almacenar el id del curso seleccionado
    const [selectedCPM, setSelectedCPM] = useState(null);
    // console.log("selectedCPM", selectedCPM);
    
  // Tomamos el usuario actual (profesor) del store de Redux
  const profe = useSelector((s) => s.user.persona);
  // Llamada al endpoint para obtener los cursos del profesor
  // Usamos profe.id si está definido, o 2 como fallback durante el desarrollo
  const { data: cursosData } = useGetCourseByTeacherQuery(
    profe ? profe.id : 2
  );

  

  // Cuando selectedId cambia, disparamos la query para traer
  // el detalle del curso (incluyendo estudiantes)
  const { data: detalleCurso } = useGetCourseWithStudentsQuery(
    selectedCPM?.curso?.id,
    { skip: !selectedCPM?.curso?.id } // skip evita la llamada hasta que selectedId sea truthy
  );

  // Cada vez que llegan los cursos del profesor, los guardamos en Redux
  useEffect(() => {
    if (cursosData) {
      dispatch(coursesByTeacher(cursosData));
    }
  }, [dispatch, cursosData]);

  // Cuando llega el detalle de un curso, lo seteamos en Redux
  // y cambiamos la vista a "curso-seleccionado"
  useEffect(() => {
    if (detalleCurso) {
      dispatch(setSelectedCourse(detalleCurso));
      // console.log('Detalle de curso cargado:', detalleCurso);
      setView('curso-seleccionado');
    }
  }, [dispatch, detalleCurso]);

  // Manejador que se pasa al componente CoursesList para cuando
  // el usuario haga clic en "Ver Curso"
  const handleSelectCourse = (curso) => {
    setView('curso-seleccionado');
    setSelectedCPM(curso);
    dispatch(setCursoProfesorMateria(curso))
    // console.log("curso seleccionado", curso);
  };

  // Renderizado condicional de cada sección según el valor de `view`
  const renderContent = () => {
    switch (view) {
      case 'inicio':
        return <DashboardProfesor />;
      case 'cursos':
        return (
          <CoursesList
            courses={cursosData || []}
            onSelect={handleSelectCourse}
          />
        );
      case 'curso-seleccionado':
        return <CourseDetail />;
      case 'asistencia':
        return <Attendance />;
      case 'eventos':
        return <EventCarousel/>;
      case 'perfil':
        return <Profile />;
      default:
        return null;
    }
  };

  return (
    <div className="profe-container">
      {/* Sidebar de navegación */}
      <MenuProfe setView={setView} currentView={view} />

      {/* Contenedor principal donde se va mostrando la sección correspondiente */}
      <main className="main-content-profe">
        {renderContent()}
      </main>
    </div>
  );
};

export default Profe;
