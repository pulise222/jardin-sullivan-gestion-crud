import React from 'react'
import { Route, Routes} from 'react-router-dom'
import TablaEstudiantes from '../components/container/TablaEstudiantes/TablaEstudiantes'
import Admin from '../components/views/Admin/Admin'
import MenuAdmin from '../components/container/Menu/MenuAdmin/MenuAdmin'
import Login from '../components/views/Login/Login'
import RequireAuth from '../hooks/RequireAuth'
import Home from "../components/views/Home/Home"

import Profe  from '../components/views/Profe/Profe'
import ResetPasswordConfirm from '../components/views/Auth/ResetPasswordConfirm'
import ResetPasswordRequest from '../components/views/Auth/ResetPasswordRequest'
import ImportEstudiantes from '../components/views/Admin/ImportEstudiantes'
import Acudiente from '../components/views/Acudiente/Acudiente'
import EstudianteDetalle from '../components/views/Acudiente/EstudianteDetalle'

const index = () => {
  return (
    <>
      <Routes>
          
        <Route path="/" element={<Home />} />
        
        <Route path='/login' element={<Login></Login>}></Route>
        
        <Route path='/estudiantes' element={<TablaEstudiantes/>} />
        
        <Route path='/admin' element={
          <RequireAuth>
            <Admin/>
          </RequireAuth>
        } />
        <Route path="/admin/importar-estudiantes" element={<ImportEstudiantes/>} />

        <Route
          path="/acudiente/*" element={
            <RequireAuth>
              <Acudiente/>
            </RequireAuth>
          }
        />
        <Route path="/acudiente/estudiante/:id" element={
          <RequireAuth>
            <EstudianteDetalle/> 
          </RequireAuth>
        }/> 
        
        <Route path='/profesor' element={
          <RequireAuth>
            <Profe/>
          </RequireAuth>
        }/>


        <Route path='/cambiar-contraseña' element={
            <ResetPasswordRequest/>
        }/>
        <Route path='/reset-password/:uid/:token' element={
            <ResetPasswordConfirm/>
        }/>
      </Routes>
    </>  
      
  )
}

export default index