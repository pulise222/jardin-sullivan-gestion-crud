// src/components/forms/create/CreateStudentForm/CreateStudentForm.jsx
import { useFormik } from "formik";
import * as Yup from "yup";
import { useCreateStudentMutation } from '../../../../features/students/studentApi';
import '../../GeneralForm.css';

const CreateStudentForm = ({ onClose }) => {
  const [createStudent, { isLoading }] = useCreateStudentMutation();

  const initialValues = {
    nombre: '',
    apellido: '',
    fecha_nacimiento: '',
    direccion: '',
    telefono: '',
    correo_electronico: '',
    tipo_documento: 'RC',     // por defecto RC
    numero_documento: '',
    curso_id: '',
  };

  const required = "* Este campo es obligatorio";

  const validationSchema = Yup.object({
    nombre: Yup.string().trim().required(required),
    apellido: Yup.string().trim().required(required),
    fecha_nacimiento: Yup.string().required(required),
    direccion: Yup.string().trim().required(required),
    telefono: Yup.string()
      .matches(/^\d{7,15}$/, 'Solo dígitos (7-15)')
      .required(required),
    correo_electronico: Yup.string().email('Email inválido').required(required),

    // NUEVOS:
    tipo_documento: Yup.string().oneOf(['RC','TI','PAS','CE']).required(required),
    numero_documento: Yup.string()
      .matches(/^[A-Za-z0-9\-\.]{4,30}$/, '4-30 caracteres alfanuméricos')
      .required(required),

    curso_id: Yup.number().typeError('Debe ser un número').required(required),
  });

  const onSubmit = async (values, { resetForm }) => {
    try {
      const payload = {
        ...values,
        curso: Number(values.curso_id)
      };
      delete payload.curso_id;

      await createStudent(payload).unwrap();
      resetForm();
      onClose?.();
    } catch (error) {
      console.error(error);
      alert('Error al crear estudiante');
    }
  };

  const formik = useFormik({ initialValues, validationSchema, onSubmit });
  const { handleSubmit, handleChange, errors, touched, handleBlur, values, setFieldValue } = formik;

  return (
    <div className="create-form">
      <form className="form" onSubmit={handleSubmit}>
        <span className="form--title">Crear Estudiante</span>

        {/* Nombre */}
        <div className="container_box">
          <div className="container--input">
            <input
              type="text" name="nombre" value={values.nombre}
              onChange={handleChange} onBlur={handleBlur} required
            />
            <span>Nombre*</span><i></i>
          </div>
          {errors.nombre && touched.nombre && <div className="error">{errors.nombre}</div>}
        </div>

        {/* Apellido */}
        <div className="container_box">
          <div className="container--input">
            <input
              type="text" name="apellido" value={values.apellido}
              onChange={handleChange} onBlur={handleBlur} required
            />
            <span>Apellido*</span><i></i>
          </div>
          {errors.apellido && touched.apellido && <div className="error">{errors.apellido}</div>}
        </div>

        {/* Fecha nacimiento */}
        <div className="container_box">
          <div className="container--input focused">
            <input
              type="date" name="fecha_nacimiento" value={values.fecha_nacimiento}
              onChange={handleChange} onBlur={handleBlur} required
            />
            <span>Fecha de Nacimiento*</span><i></i>
          </div>
          {errors.fecha_nacimiento && touched.fecha_nacimiento && <div className="error">{errors.fecha_nacimiento}</div>}
        </div>

        {/* Dirección */}
        <div className="container_box">
          <div className="container--input">
            <input
              type="text" name="direccion" value={values.direccion}
              onChange={handleChange} onBlur={handleBlur} required
            />
            <span>Dirección*</span><i></i>
          </div>
          {errors.direccion && touched.direccion && <div className="error">{errors.direccion}</div>}
        </div>

        {/* Teléfono */}
        <div className="container_box">
          <div className="container--input">
            <input
              type="text" name="telefono" value={values.telefono}
              onChange={handleChange} onBlur={handleBlur} required
            />
            <span>Teléfono*</span><i></i>
          </div>
          {errors.telefono && touched.telefono && <div className="error">{errors.telefono}</div>}
        </div>

        {/* Correo */}
        <div className="container_box">
          <div className={values.correo_electronico ? "container--input focused" : "container--input"}>
            <input
              type="email" name="correo_electronico" value={values.correo_electronico}
              onChange={handleChange} onBlur={handleBlur} required
            />
            <span>Correo Electrónico*</span><i></i>
          </div>
          {errors.correo_electronico && touched.correo_electronico && <div className="error">{errors.correo_electronico}</div>}
        </div>

        {/* Tipo Documento */}
        <div className="container_box">
          <label style={{fontSize:12, marginBottom:4}}>Tipo de Documento*</label>
          <select
            name="tipo_documento"
            value={values.tipo_documento}
            onChange={(e)=>setFieldValue('tipo_documento', e.target.value)}
            onBlur={handleBlur}
            className="select-control"
            required
          >
            <option value="RC">Registro Civil</option>
            <option value="TI">Tarjeta de Identidad</option>
            <option value="PAS">Pasaporte</option>
            <option value="CE">Cédula de Extranjería</option>
          </select>
          {errors.tipo_documento && touched.tipo_documento && <div className="error">{errors.tipo_documento}</div>}
        </div>

        {/* Documento */}
        <div className="container_box">
          <div className="container--input">
            <input
              type="text" name="numero_documento" value={values.numero_documento}
              onChange={handleChange} onBlur={handleBlur} required
            />
            <span>Número de Documento*</span><i></i>
          </div>
          {errors.numero_documento && touched.numero_documento && <div className="error">{errors.numero_documento}</div>}
        </div>

        {/* Curso */}
        <div className="container_box">
          <div className="container--input">
            <input
              type="number" name="curso_id" value={values.curso_id}
              onChange={handleChange} onBlur={handleBlur} required
            />
            <span>Curso/Grupo (ID)*</span><i></i>
          </div>
          {errors.curso_id && touched.curso_id && <div className="error">{errors.curso_id}</div>}
        </div>

        <button type="submit" className="button" disabled={isLoading}>
          {isLoading ? "Creando..." : "Crear Estudiante"}
        </button>
      </form>
    </div>
  );
};

export default CreateStudentForm;