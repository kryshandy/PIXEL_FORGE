export default function ResultPanel({ result }) {
  if (!result || result.status === 'idle') {
    return (
      <div className="result-panel result-panel--empty">
        <span className="result-panel__icon">◌</span>
        <p>La recommandation apparaîtra ici une fois vos paramètres soumis.</p>
      </div>
    );
  }

  if (result.status === 'loading') {
    return (
      <div className="result-panel result-panel--pending">
        <span className="section-eyebrow">Analyse en cours</span>
        <p>Calcul d'ingénierie et recherche documentaire en cours…</p>
      </div>
    );
  }

  if (result.status === 'error') {
    return (
      <div className="result-panel result-panel--error">
        <span className="section-eyebrow">Erreur</span>
        <p>{result.message}</p>
      </div>
    );
    {result.requestId && (
      <p className="result-panel__request-id">ID de requête : <code>{result.requestId}</code></p>
    )}
  }

  const data = result.data ?? {};

  return (
    <div className="result-panel result-panel--success">
      <span className="section-eyebrow">Recommandation</span>

      {data.recommendation && <p className="result-panel__main">{data.recommendation}</p>}

      {Array.isArray(data.sources) && data.sources.length > 0 && (
        <div className="result-panel__sources">
          <span className="result-panel__sources-title">Sources</span>
          <ul>
            {data.sources.map((s, i) => (
              <li key={i}>{s.title || s.url || `Source ${i + 1}`}</li>
            ))}
          </ul>
        </div>
      )}

      {data.disclaimer && <p className="result-panel__disclaimer">{data.disclaimer}</p>}

      {data.status && (
        <span className={`result-panel__status result-panel__status--${data.status}`}>
          {data.status}
        </span>
      )}
    </div>
  );
}