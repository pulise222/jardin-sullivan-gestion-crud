// src/components/forms/create/CreatePerson/CreatePersonForm.jsx
import React from 'react';
import { useSearchParams } from 'react-router-dom';
import { useFormik } from "formik";
import * as Yup from "yup";
import { useCreatePersonMutation } from '../../../../features/people/personApi';
import '../../GeneralForm.css';

const CreatePersonForm = ({onClose}) => {
  const [params] = useSearchParams();
  const preRol = params.get('new') === 'acudiente' ? 'Acudiente' : '';

  const [createPerson, { isLoading }] = useCreatePersonMutation();

  const initialValues = {
    nombre: '',
    apellido: '',
    telefono: '',
    tipo_documento: '',
    numero_documento: '',
    direccion: '',
    fecha_nacimiento: '',
    email: '',
    rol: preRol
  };

  const required = "* Este campo es obligatorio";

  const validationSchema = Yup.object().shape({
    nombre:                     Yup.string().required(required),
    apellido:                     Yup.string().required(required),
    telefono:                    Yup.string().required(required),
    tipo_documento:        Yup.string().required(required),
    numero_documento:  Yup.string().required(required),
    direccion:                    Yup.string().required(required),
    fecha_nacimiento:      Yup.date().required(required),
    email:                         Yup.string().email("Email inválido").required(required),
    rol:                             Yup.string().required(required),
  });



  const onSubmit = async (values) => {
    try {
      // Preparamos el payload para que el backend reciba
      // tanto la persona como los datos de usuario anidados

      const payload = {
        nombre:           values.nombre,
        apellido:         values.apellido,
        telefono:         values.telefono,
        tipo_documento:   values.tipo_documento,
        numero_documento: values.numero_documento,
        direccion:        values.direccion,
        fecha_nacimiento: values.fecha_nacimiento,
        usuario: {
          username: values.email,  // Usamos el mismo email como username
          email:    values.email,
          rol:      values.rol
        }
      };

      console.log(payload);
      
      await createPerson(payload).unwrap();
      alert('Persona creada con éxito');
      onClose()
    } catch (error) {
      console.error(error);
      alert('Error al crear persona');
    }
  };

  const formik = useFormik({ initialValues, validationSchema, onSubmit });
  const { handleSubmit, handleChange, handleBlur, values, errors, touched } = formik;

  const campos = [
    { name: "nombre",           type: "text",  label: "Nombre*" },
    { name: "apellido",         type: "text",  label: "Apellido*" },
    { name: "telefono",         type: "text",  label: "Teléfono*" },
    { name: "tipo_documento",   type: "text",  label: "Tipo de Documento*" },
    { name: "numero_documento", type: "text",  label: "Número de Documento*" },
    { name: "direccion",        type: "text",  label: "Dirección*" },
    { name: "fecha_nacimiento", type: "date",  label: "Fecha de Nacimiento*" },
    { name: "email",            type: "email", label: "Email*" },
  ];

  return (
    <div className="create-form">
      <form className="form" onSubmit={handleSubmit}>
        <span className="form--title">Crear Persona</span>

        {campos.map(({ name, type, label }) => (
          <div className="container_box" key={name}>
            <div
              className={
                values[name] || name === "fecha_nacimiento"
                  ? "container--input focused"
                  : "container--input"
              }
            >
              <input
                type={type}
                name={name}
                id={name}
                value={values[name]}
                onChange={handleChange}
                onBlur={handleBlur}
                required
              />
              <span>{label}</span>
              <i></i>
            </div>
            {errors[name] && touched[name] && (
              <div className="error">{errors[name]}</div>
            )}
          </div>
        ))}

      <div className="container_box" key="rol">
        <div
          className={
            values.rol || touched.rol
              ? "container--input focused"
              : "container--input"
          }
        >
              <select
                name="rol"
                id="rol"
                value={values.rol}
                onChange={handleChange}
                onBlur={handleBlur}
                required
              >
                <option value="" disabled>
                  Seleccione un rol*
                </option>
                <option value="Acudiente">Acudiente</option>
                <option value="Profesor">Profesor</option>
                <option value="Administrador">Administrador</option>
              </select>
              <span>Rol de Usuario*</span>
            </div>
            {errors.rol && touched.rol && <div className="error">{errors.rol}</div>}
          </div>



        <button type="submit" className="button" disabled={isLoading}>
          {isLoading ? "Creando..." : "Crear Persona"}
        </button>
      </form>
    </div>
  );
};

export default CreatePersonForm;
