// src/views/components/Profesor/CoursesList.jsx
import React from 'react';
import './css/CoursesList.css'

const CoursesList = ({ courses = [], onSelect }) => {
  if (!courses.length) {
    return <p>No hay cursos asignados.</p>;
  }

  return (
    <div className="courses-section">
      {courses.map((course) => (
        <div key={course.id} className="course-card">
          <div className="course-icon">
            <img
              src="https://img.icons8.com/ios/452/classroom.png"
                // alt={course.curso.nombre_curso}
            />
          </div>
          <div className="course-info">
            <h3>{course.curso.nombre_curso}</h3>
            <p>{course.curso.descripcion}</p>
            <p>{course.materia.nombre}</p>
          </div>
          <button
            className="view-course"
            onClick={() => onSelect(course)}
          >
            Ver Curso
          </button>
        </div>
      ))}
    </div>
  );
};

export default CoursesList;
