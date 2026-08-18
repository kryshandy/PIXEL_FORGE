const TEAM = [
  { name: 'Florent', github: 'https://github.com/floflowilwil-cpu' },
  { name: 'Krys', github: 'https://github.com/kryshandy' },
  { name: 'Michel', github: 'https://github.com/Henri-Michel-Essomba-Djomeni' },
  { name: 'Azra', github: 'https://github.com/Azra1808' },
];

import { useReveal } from '../hooks/useReveal';
// ...
export default function FeaturesSection() {
  const ref = useReveal();
  return (
    <section className="team-section reveal" ref={ref} id="equipe">
      <span className="section-eyebrow">L'équipe</span>
      <h2>Pixel Forge</h2>
      <p className="team-section__intro">
        Quatre étudiants, une semaine, un copilote pour l'ingénierie de réservoir —
        projet soumis au Pixel Forge AI Hackathon (15 → 22 août 2026).
      </p>

      <div className="team-grid">
        {TEAM.map((member) => (
          <a key={member.name} href={member.github} target="_blank" rel="noreferrer" className="team-card">
            <div className="team-card__avatar">{member.name.charAt(0)}</div>
            <h3>{member.name}</h3>
            <span className="team-card__badge">Informatique · Tronc Commun · Bachelor 2</span>
            <span className="team-card__link">GitHub ↗</span>
          </a>
        ))}
      </div>

      <div className="team-section__repo">
        <span>Dépôt du projet</span>
        <a href="https://github.com/kryshandy/PIXEL_FORGE" target="_blank" rel="noreferrer">
          github.com/kryshandy/PIXEL_FORGE ↗
        </a>
      </div>
    </section>
  );
}