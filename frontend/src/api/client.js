const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export class ApiError extends Error {
  constructor(message, status, details) {
    super(message);
    this.status = status;
    this.details = details;
  }
}

export async function apiPost(path, body) {
  let response;
  try {
    response = await fetch(`${BASE_URL}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
  } catch (networkErr) {
    throw new ApiError('Impossible de joindre le serveur. Vérifiez votre connexion.', 0, networkErr);
  }

  if (response.status === 422) {
    const details = await response.json().catch(() => null);
    throw new ApiError('Certains champs sont invalides.', 422, details);
  }

  if (!response.ok) {
    throw new ApiError(`Erreur serveur (${response.status}).`, response.status);
  }

  return response.json();
}