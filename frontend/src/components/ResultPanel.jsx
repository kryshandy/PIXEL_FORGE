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
        {result.details && (
          <pre className="result-panel__details">{JSON.stringify(result.details, null, 2)}</pre>
        )}
      </div>
    );
  }

  const data = result.data ?? {};

  return (
    <div className="result-panel result-panel--success">
      <span className="section-eyebrow">Recommandation</span>

      {data.recommendation && <p className="result-panel__main">{data.recommendation}</p>}

      {(data.productivityIndex || data.fracturePressure) && (
        <dl className="result-panel__metrics">
          {data.productivityIndex && (
            <>
              <dt>Indice de productivité</dt>
              <dd>{data.productivityIndex.value} {data.productivityIndex.unit}
                {data.productivityIndex.method && ` — méthode : ${data.productivityIndex.method}`}
              </dd>
            </>
          )}
          {data.fracturePressure && (
            <>
              <dt>Pression de fracturation</dt>
              <dd>{data.fracturePressure.value} {data.fracturePressure.unit}
                {data.fracturePressure.warning && (
                  <span className="result-panel__warning"> ⚠ {data.fracturePressure.warning}</span>
                )}
              </dd>
            </>
          )}
        </dl>
      )}

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

      {data.status && (
        <span className={`result-panel__status result-panel__status--${data.status}`}>
          {data.status}
        </span>
      )}
    </div>
  );
}