const FEATURES = [
  {
    title: 'Recherche documentaire fiable',
    desc: 'Les recommandations s\'appuient sur une base de connaissance technique indexée (publications SPE, manuels de pétrophysique), pas sur la seule mémoire du modèle de langage.',
  },
  {
    title: 'Calculs d\'ingénierie vérifiables',
    desc: 'Indice de productivité, pression de fracturation estimée : chaque recommandation est ancrée dans des formules reconnues, pas seulement générée en langage naturel.',
  },
  {
    title: 'Sources citées',
    desc: 'Chaque réponse indique les documents dont elle s\'inspire — comme un collègue senior qui justifie son avis plutôt que de l\'affirmer.',
  },
  {
    title: 'Ciblé et crédible',
    desc: 'Volontairement restreint aux puits pétroliers conventionnels : littérature abondante, formules bien établies, moins de variables parasites qu\'un système générique.',
  },
];

import { useReveal } from '../hooks/useReveal';
// ...
export default function FeaturesSection() {
  const ref = useReveal();
  return (
    <section className="features-section reveal" ref={ref} id="fonctionnalites">
      <span className="section-eyebrow">Fonctionnalités</span>
      <h2>Un copilote, pas une boîte noire</h2>
      <div className="features-grid">
        {FEATURES.map((f) => (
          <div key={f.title} className="feature-card">
            <h3>{f.title}</h3>
            <p>{f.desc}</p>
          </div>
        ))}
      </div>
    </section>
  );
}