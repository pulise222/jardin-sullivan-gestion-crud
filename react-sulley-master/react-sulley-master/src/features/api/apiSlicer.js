import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';
import { setCredentials, logoutUser } from '../user/userSlice';

const isValidToken = (t) => t && t !== 'undefined' && t !== 'null';

const rawBaseQuery = fetchBaseQuery({
  baseUrl: 'http://127.0.0.1:8000/',
  prepareHeaders: (headers) => {
    const token = localStorage.getItem('access');
    if (isValidToken(token)) {
      headers.set('Authorization', `Bearer ${token}`);
    }
    return headers;
  },
});

// evita múltiples refresh simultáneos
let refreshRun = null;

const doRefresh = async (api, extraOptions) => {
  const currentRefresh = localStorage.getItem('refresh');
  if (!isValidToken(currentRefresh)) {
    throw new Error('no-refresh-token');
  }

  const res = await rawBaseQuery(
    {
      url: 'api/token/refresh/',
      method: 'POST',
      body: { refresh: currentRefresh },
    },
    api,
    extraOptions
  );

  if (res.error) throw new Error('refresh-failed');

  const newAccess = res.data?.access;
  // SimpleJWT por defecto NO rota el refresh; si no viene, conserva el actual
  const newRefresh = res.data?.refresh ?? currentRefresh;

  if (!isValidToken(newAccess)) throw new Error('no-access-in-refresh');

  localStorage.setItem('access', newAccess);
  localStorage.setItem('refresh', newRefresh);

  const state = api.getState();
  const user = state?.user?.user || null;

  // Actualiza el slice manteniendo el user actual
  api.dispatch(setCredentials({ user, access: newAccess, refresh: newRefresh }));
};

const baseQueryWithReauth = async (args, api, extraOptions) => {
  let result = await rawBaseQuery(args, api, extraOptions);

  // ¿401? intentamos refresh
  if (result.error?.status === 401) {
    const url = typeof args === 'string' ? args : args?.url || '';

    // Evita bucles si la 401 viene del propio login o del refresh
    if (url.startsWith('api/token')) {
      api.dispatch(logoutUser());
      return result;
    }

    // Corre un refresh compartido si no está corriendo
    if (!refreshRun) {
      refreshRun = doRefresh(api, extraOptions).finally(() => {
        refreshRun = null;
      });
    }

    try {
      await refreshRun; // espera al refresh (o que falle)
      // Reintenta la petición original con el nuevo access
      result = await rawBaseQuery(args, api, extraOptions);
    } catch (e) {
      // Refresh falló: cerrar sesión limpia
      console.log(e);
      api.dispatch(logoutUser());
    }
  }

  return result;
};

export const api = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithReauth,
  tagTypes: ['User', 'Courses', 'Students', 'Entregas','People','Materias','Eventos'],
  endpoints: () => ({}),
});

export const { useLoginUserMutation } = api;
