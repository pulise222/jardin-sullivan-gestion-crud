import React from 'react';
import { useDispatch } from 'react-redux';
import { filterByNameStudents } from '../../../features/students/studentSlice';
import { filterByNamePerson } from '../../../features/people/personSlice';
import './StudentToolbar.css';


const PersonToolBar = ( {onAddClick} ) => {
  const dispatch = useDispatch()
  
  const onSearchChangePerson = (e) => {
    dispatch(filterByNamePerson(e.target.value));
  }
  return(
    <div className="toolbar-row">
      <div className="search-section">
        <input
          type="text"
          className="search-input"
          placeholder="Buscar persona..."
          onChange={onSearchChangePerson}
          />
        <button className="search-button" type="button">
          <i className="fas fa-search"></i>
        </button>
      </div>
      <button type="button" className="add-button" onClick={onAddClick}>
        <i className="fas fa-plus-circle"></i> Agregar Persona
      </button>
    </div>
    )
  }
  
  const StudentToolbar = ({ onAddClick }) => {
    const dispatch = useDispatch()
    
    const onSearchChangeStudent = (e) => {
    dispatch(filterByNameStudents(e.target.value));
  }
  return (
    <div className="toolbar-row">
      <div className="search-section">
        <input
          type="text"
          className="search-input"
          placeholder="Buscar estudiante..."
          onChange={onSearchChangeStudent}
        />
        <button className="search-button" type="button">
          <i className="fas fa-search"></i>
        </button>
      </div>
      <button type="button" className="add-button" onClick={onAddClick}>
        <i className="fas fa-plus-circle"></i> Agregar Estudiante
      </button>
    </div>
  );
};

export { StudentToolbar, PersonToolBar};
