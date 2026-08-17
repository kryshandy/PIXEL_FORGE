export default function ResultPanel({ result }) {
  if (!result) {
    return (
      <div className="result-panel result-panel--empty">
        <span className="result-panel__icon">◌</span>
        <p>La recommandation apparaîtra ici une fois vos paramètres soumis.</p>
      </div>
    );
  }

  return (
    <div className="result-panel result-panel--pending">
      <span className="section-eyebrow">Analyse en cours</span>
      <p>
        Paramètres reçus pour un réservoir de type <strong>{result.rockType}</strong>.
        L'intégration au moteur de calcul et RAG est en cours côté équipe (Jour 4).
      </p>
    </div>
  );
}