import { useState } from 'react';
import ReservoirForm from './components/ReservoirForm';
import ResultPanel from './components/ResultPanel';
import HeroScene from './components/HeroScene';
import FeaturesSection from './components/FeaturesSection';
import HowItWorksSection from './components/HowItWorksSection';
import TeamSection from './components/TeamSection';
import './App.css';

function App() {
  const [result, setResult] = useState(null);

  return (
    <div className="page">
      <header className="site-header">
        <span className="site-header__logo">PetroSage</span>
        <nav className="site-header__nav">
          <a href="#fonctionnalites">Fonctionnalités</a>
          <a href="#comment-ca-marche">Fonctionnement</a>
          <a href="#equipe">Équipe</a>
        </nav>
        <span className="site-header__tag">Pixel Forge AI Hackathon 2026</span>
      </header>

      <section className="hero">
        <div className="hero__scene">
          <HeroScene />
          <div className="hero__copy">
            <span className="section-eyebrow">Copilote ingénierie réservoir</span>
            <h1>Une recommandation d'ingénieur, sourcée et calculée.</h1>
            <p>
              PetroSage combine calculs pétrophysiques vérifiables et recherche
              documentaire pour assister la complétion de puits pétroliers conventionnels.
            </p>
          </div>
        </div>
        <div className="hero__form">
          <ReservoirForm onSubmit={setResult} />
          <ResultPanel result={result} />
        </div>
      </section>

      <FeaturesSection />
      <HowItWorksSection />
      <TeamSection />

      <footer className="site-footer">
        <p>PetroSage — Copilote IA pour la complétion & production de puits pétroliers conventionnels.</p>
      </footer>
    </div>
  );
}

export default App;