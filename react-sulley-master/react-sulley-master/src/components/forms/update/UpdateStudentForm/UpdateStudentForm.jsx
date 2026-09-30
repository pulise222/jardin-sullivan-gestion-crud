// src/components/forms/update/UpdateStudentForm/UpdateStudentForm.jsx
import { useFormik } from "formik";
import * as Yup from "yup";
import { useUpdateStudentMutation } from '../../../../features/students/studentApi'; 
import '../../GeneralForm.css';

const UpdateStudentForm = ({ student, onClose }) => {
  const [updateStudent, { isLoading }] = useUpdateStudentMutation();

  const initialValues = {
    nombre: student?.nombre || '',
    apellido: student?.apellido || '',
    fecha_nacimiento: student?.fecha_nacimiento || '',
    direccion: student?.direccion || '',
    telefono: student?.telefono || '',
    correo_electronico: student?.correo_electronico || '',
    tipo_documento: student?.tipo_documento || 'RC',
    numero_documento: student?.numero_documento || '',
    curso: student?.curso || ''
  };

  const required = "* Este campo es obligatorio";

  const validationSchema = Yup.object().shape({
    nombre: Yup.string().strict().required(required),
    apellido: Yup.string().required(required),
    fecha_nacimiento: Yup.string().required(required),
    direccion: Yup.string().required(required),
    telefono: Yup.string().required(required),
    correo_electronico: Yup.string().email('Email inválido').required(required),
    tipo_documento: Yup.string().oneOf(['RC','TI','PAS','CE']).required(required),
    numero_documento: Yup.string().matches(/^[A-Za-z0-9\-\.]{4,30}$/, '4-30 caracteres alfanuméricos').required(required),
    curso: Yup.number().required(required),
  });

  const onSubmit = async(values) => {
    try {
      await updateStudent({ id: student.id, ...values }).unwrap();
      alert("Estudiante actualizado con éxito");
      onClose?.();
    } catch (error) {
      console.error("Error al actualizar estudiante:", error);
      alert("Error al actualizar estudiante");
    }
  };

  const formik = useFormik({ initialValues, validationSchema, onSubmit });
  const { handleSubmit, handleChange, errors, touched, handleBlur, values, setFieldValue } = formik;

  return (
    <div className="create-form">
      <form className="form" onSubmit={handleSubmit}>
        <span className="form--title">Actualizar Estudiante</span>

        {[
          { name: "nombre", type: "text", label: "Nombre*" },
          { name: "apellido", type: "text", label: "Apellido*" },
          { name: "fecha_nacimiento", type: "date", label: "Fecha de Nacimiento*" },
          { name: "direccion", type: "text", label: "Dirección*" },
          { name: "telefono", type: "text", label: "Teléfono*" },
          { name: "correo_electronico", type: "email", label: "Correo Electrónico*" },
        ].map(({ name, type, label }) => (
          <div key={name} className="container_box">
            <div className={name === "fecha_nacimiento" || name === "correo_electronico" ? "container--input focused" : "container--input"}>
              <input
                type={type}
                name={name}
                value={values[name]}
                onChange={handleChange}
                onBlur={handleBlur}
                required
              />
              <span>{label}</span>
              <i></i>
            </div>
            {errors[name] && touched[name] && <div className="error">{errors[name]}</div>}
          </div>
        ))}

        {/* Tipo de Documento */}
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
            {/* <option value="PAS">Pasaporte</option> 
            <option value="CE">Cédula de Extranjería</option> */}
          </select>
          {errors.tipo_documento && touched.tipo_documento && <div className="error">{errors.tipo_documento}</div>}
        </div>

        {/* Número Documento */}
        <div className="container_box">
          <div className="container--input">
            <input
              type="text"
              name="numero_documento"
              value={values.numero_documento}
              onChange={handleChange}
              onBlur={handleBlur}
              required
            />
            <span>Número de Documento*</span>
            <i></i>
          </div>
          {errors.numero_documento && touched.numero_documento && <div className="error">{errors.numero_documento}</div>}
        </div>

        {/* Curso */}
        <div className="container_box">
          <div className="container--input">
            <input
              type="number"
              name="curso"
              value={values.curso}
              onChange={handleChange}
              onBlur={handleBlur}
              required
            />
            <span>Curso/Grupo (ID)*</span>
            <i></i>
          </div>
          {errors.curso && touched.curso && <div className="error">{errors.curso}</div>}
        </div>

        <button type="submit" className="button" disabled={isLoading}>
          {isLoading ? 'Actualizando...' : 'Actualizar Estudiante'}
        </button>
      </form>
    </div>
  );
};

export default UpdateStudentForm;