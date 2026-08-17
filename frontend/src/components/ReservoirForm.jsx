import { useState } from 'react';
import './ReservoirForm.css';

const ROCK_TYPES = [
  { value: 'gres', label: 'Grès' },
  { value: 'calcaire', label: 'Calcaire' },
  { value: 'dolomie', label: 'Dolomie' },
];

const initialForm = {
  rockType: '',
  porosity: '',
  permeability: '',
  pressure: '',
  depth: '',
};

function validate(form) {
  const errors = {};
  if (!form.rockType) errors.rockType = 'Sélectionnez un type de roche.';
  if (!form.porosity || form.porosity <= 0 || form.porosity > 40)
    errors.porosity = 'Porosité attendue entre 0 et 40 %.';
  if (!form.permeability || form.permeability <= 0)
    errors.permeability = 'Perméabilité requise (mD), valeur positive.';
  if (!form.pressure || form.pressure <= 0)
    errors.pressure = 'Pression de réservoir requise (psi), valeur positive.';
  if (!form.depth || form.depth <= 0)
    errors.depth = 'Profondeur requise (m), valeur positive.';
  return errors;
}

export default function ReservoirForm({ onSubmit }) {
  const [form, setForm] = useState(initialForm);
  const [errors, setErrors] = useState({});

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

const [submitting, setSubmitting] = useState(false);

function handleSubmit(e) {
  e.preventDefault();
  const validationErrors = validate(form);
  setErrors(validationErrors);
  if (Object.keys(validationErrors).length === 0) {
    setSubmitting(true);
    setTimeout(() => {
      setSubmitting(false);
      onSubmit?.(form);
    }, 900);
  }
}

  return (
    <form className="reservoir-form" onSubmit={handleSubmit} noValidate>
      <header className="reservoir-form__header">
        <span className="reservoir-form__eyebrow">Paramètres du réservoir</span>
        <h2>Décrivez votre puits</h2>
      </header>

      <div className="reservoir-form__field">
        <label htmlFor="rockType">Type de roche</label>
        <select id="rockType" name="rockType" value={form.rockType} onChange={handleChange}>
          <option value="">Sélectionner…</option>
          {ROCK_TYPES.map((r) => (
            <option key={r.value} value={r.value}>{r.label}</option>
          ))}
        </select>
        {errors.rockType && <span className="reservoir-form__error">{errors.rockType}</span>}
      </div>

      <div className="reservoir-form__grid">
        <div className="reservoir-form__field">
          <label htmlFor="porosity">Porosité (%)</label>
          <input id="porosity" name="porosity" type="number" step="0.1" inputMode="decimal"
            value={form.porosity} onChange={handleChange} />
          {errors.porosity && <span className="reservoir-form__error">{errors.porosity}</span>}
        </div>

        <div className="reservoir-form__field">
          <label htmlFor="permeability">Perméabilité (mD)</label>
          <input id="permeability" name="permeability" type="number" step="0.01" inputMode="decimal"
            value={form.permeability} onChange={handleChange} />
          {errors.permeability && <span className="reservoir-form__error">{errors.permeability}</span>}
        </div>

        <div className="reservoir-form__field">
          <label htmlFor="pressure">Pression (psi)</label>
          <input id="pressure" name="pressure" type="number" step="1" inputMode="numeric"
            value={form.pressure} onChange={handleChange} />
          {errors.pressure && <span className="reservoir-form__error">{errors.pressure}</span>}
        </div>

        <div className="reservoir-form__field">
          <label htmlFor="depth">Profondeur (m)</label>
          <input id="depth" name="depth" type="number" step="1" inputMode="numeric"
            value={form.depth} onChange={handleChange} />
          {errors.depth && <span className="reservoir-form__error">{errors.depth}</span>}
        </div>
      </div>

      <button type="submit" className="reservoir-form__submit">
        Générer la recommandation
      </button>
    </form>
  );
}