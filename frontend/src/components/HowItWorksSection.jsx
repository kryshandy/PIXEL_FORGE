const STEPS = [
  { n: '01', title: 'Saisie des paramètres', desc: 'Type de roche, porosité, perméabilité, pression, profondeur du réservoir.' },
  { n: '02', title: 'Calcul d\'ingénierie', desc: 'Application des formules pertinentes : indice de productivité, pression de fracturation.' },
  { n: '03', title: 'Recherche documentaire', desc: 'Le système RAG récupère les passages techniques les plus pertinents pour ces paramètres.' },
  { n: '04', title: 'Recommandation argumentée', desc: 'Le LLM combine contexte documentaire et résultats de calcul pour formuler une réponse sourcée.' },
];

import { useReveal } from '../hooks/useReveal';
// ...
export default function FeaturesSection() {
  const ref = useReveal();
  return (
    <section className="how-section reveal" ref={ref} id="comment-ca-marche">
      <span className="section-eyebrow">Comment ça marche</span>
      <h2>Du réservoir à la recommandation</h2>
      <div className="how-steps">
        {STEPS.map((s) => (
          <div key={s.n} className="how-step">
            <span className="how-step__n">{s.n}</span>
            <h3>{s.title}</h3>
            <p>{s.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}