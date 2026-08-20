const BASE_URL = import.meta.env.VITE_API_BASE_URL;

export class ApiError extends Error {
  constructor(message, status, details, requestId) {
    super(message);
    this.status = status;
    this.details = details;
    this.requestId = requestId;
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
    const body = await response.json().catch(() => null);
    const fieldErrors = body?.error?.details ?? [];
    const requestId = body?.error?.requestId ?? response.headers.get('X-Request-ID');
    const summary = fieldErrors.length > 0
      ? fieldErrors.map((d) => `${d.field} : ${d.message}`).join(' · ')
      : body?.error?.message ?? 'Certains champs sont invalides.';
    throw new ApiError(summary, 422, fieldErrors, requestId);
  }

  if (!response.ok) {
    throw new ApiError(`Erreur serveur (${response.status}).`, response.status);
  }

  return response.json();
}