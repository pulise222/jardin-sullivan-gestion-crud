// src/components/admin/ImportEstudiantes.jsx
import React, { useState } from 'react';
import { useImportarEstudiantesMutation } from '../../../features/people/personApi';
import './css/ImportEstudiantes.css';

const ImportEstudiantes = () => {
  const [file, setFile] = useState(null);
  const [importar, { data, isLoading, isError, error }] = useImportarEstudiantesMutation();

  const onSubmit = async (e) => {
    e.preventDefault();
    if (!file) return alert('Selecciona un archivo .xlsx o .csv');

    try {
      await importar(file).unwrap();
      // opcional: mostrar toast
    } catch (err) {
      console.error(err);
    }
  };

  const descargarPlantillaCSV = () => {
    const headers = [
      'curso_id',
      'curso_nombre',
      'estudiante_nombre',
      'estudiante_apellido',
      'estudiante_fecha_nacimiento',
      'estudiante_direccion',
      'estudiante_telefono',
      'estudiante_correo',
      'acudiente_tipo_documento',
      'acudiente_numero_documento',
      'acudiente_nombre',
      'acudiente_apellido',
      'acudiente_telefono',
      'acudiente_direccion',
      'acudiente_email',
      'parentesco',
    ];
    const csv = headers.join(',') + '\n';
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'plantilla_estudiantes_acudiente.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="import-wrapper">
      <div className="import-card">
        <h2>Importar estudiantes + acudiente</h2>

        <p className="hint">
          Sube un archivo <strong>.xlsx</strong> o <strong>.csv</strong> con los encabezados
          recomendados. Puedes usar <em>curso_id</em> o <em>curso_nombre</em> (si envías ambos, se usa <em>curso_id</em>).
        </p>

        <div className="actions-row">
          <button type="button" className="secondary" onClick={descargarPlantillaCSV}>
            Descargar plantilla CSV
          </button>
        </div>

        <form onSubmit={onSubmit} className="import-form">
          <label className="file-label">
            Archivo
            <input
              type="file"
              accept=".xlsx,.csv"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
          </label>

          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Importando…' : 'Subir archivo'}
          </button>
        </form>

        {/* Resultados */}
        {isError && (
          <div className="error-box">
            <h4>Error</h4>
            <pre>{JSON.stringify(error?.data || error, null, 2)}</pre>
          </div>
        )}

        {data && (
          <div className="result-box">
            <h3>Resultado</h3>
            <ul className="resume">
              <li><strong>Filas procesadas:</strong> {data.procesadas}</li>
              <li><strong>Estudiantes creados:</strong> {data.estudiantes_creados}</li>
              <li><strong>Acudientes creados:</strong> {data.acudientes_creados}</li>
              <li><strong>Relaciones creadas:</strong> {data.links_creados}</li>
            </ul>

            {Array.isArray(data.errores) && data.errores.length > 0 && (
              <>
                <h4>Errores</h4>
                <table className="errors-table">
                  <thead>
                    <tr>
                      <th>Fila</th>
                      <th>Detalle</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.errores.map((e, i) => (
                      <tr key={i}>
                        <td>{e.fila}</td>
                        <td>{e.error}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </>
            )}
          </div>
        )}
      </div>

      <div className="format-help">
        <h3>Encabezados requeridos</h3>
        <p>
          Debes incluir <code>curso_id</code> <em>o</em> <code>curso_nombre</code>.
          Además:
        </p>
        <ul>
          <li>estudiante_nombre, estudiante_apellido, estudiante_fecha_nacimiento</li>
          <li>estudiante_direccion, estudiante_telefono, estudiante_correo</li>
          <li>acudiente_tipo_documento, acudiente_numero_documento</li>
          <li>acudiente_nombre, acudiente_apellido, acudiente_telefono</li>
          <li>acudiente_direccion, acudiente_email, parentesco</li>
        </ul>
      </div>
    </div>
  );
};

export default ImportEstudiantes;
