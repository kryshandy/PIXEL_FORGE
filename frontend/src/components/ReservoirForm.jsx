import { useState } from 'react';
import { apiPost, ApiError } from '../api/client';
import { porosityPercentToFraction, metersToFeet } from '../utils/conversions';
import './ReservoirForm.css';

const ROCK_TYPES = [
  { value: 'gres', label: 'Grès' },
  { value: 'calcaire', label: 'Calcaire' },
  { value: 'dolomie', label: 'Dolomie' },
];

const initialForm = {
  wellName: '',
  rockType: '',
  porosity: '',
  permeability: '',
  pressure: '',
  depth: '',
};

function validate(form) {
  const errors = {};
  if (!form.wellName.trim()) errors.wellName = 'Donnez un nom au puits.';
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

const ROCK_TYPE_API_LABELS = {
  gres: 'Sandstone',
  calcaire: 'Limestone',
  dolomie: 'Dolomite',
};

function buildPayload(form) {
  return {
    wellName: form.wellName.trim(),
    rockType: ROCK_TYPE_API_LABELS[form.rockType] ?? form.rockType,
    porosityFraction: porosityPercentToFraction(form.porosity),
    permeabilityMd: Number(form.permeability),
    reservoirPressurePsi: Number(form.pressure),
    trueVerticalDepthFt: metersToFeet(form.depth),
  };
}

export default function ReservoirForm({ onResult }) {
  const [form, setForm] = useState(initialForm);
  const [errors, setErrors] = useState({});
  const [status, setStatus] = useState('idle'); // idle | loading | error
  const [lastPayload, setLastPayload] = useState(null);

  function handleChange(e) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function submitPayload(payload) {
  setStatus('loading');
  onResult({ status: 'loading' });
  try {
    const data = await apiPost('/recommendations', payload);
    setStatus('idle');
    onResult({ status: 'success', data });
  } catch (err) {
    setStatus('error');
    const message =
      err instanceof ApiError
        ? err.message
        : 'Une erreur inattendue est survenue.';
    const requestId = err instanceof ApiError ? err.requestId : null;
    onResult({ status: 'error', message, requestId });
  }
}

  function handleSubmit(e) {
    e.preventDefault();
    const validationErrors = validate(form);
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length === 0) {
      const payload = buildPayload(form);
      setLastPayload(payload);
      submitPayload(payload);
    }
  }

  function handleRetry() {
    if (lastPayload) submitPayload(lastPayload);
  }

  return (
    <form className="reservoir-form" onSubmit={handleSubmit} noValidate>
      <header className="reservoir-form__header">
        <span className="reservoir-form__eyebrow">Paramètres du réservoir</span>
        <h2>Décrivez votre puits</h2>
      </header>

      <div className="reservoir-form__field">
        <label htmlFor="wellName">Nom du puits</label>
        <input id="wellName" name="wellName" type="text" placeholder="Ex. Puits-A1"
          value={form.wellName} onChange={handleChange} />
        {errors.wellName && <span className="reservoir-form__error">{errors.wellName}</span>}
      </div>

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

      <button type="submit" className="reservoir-form__submit" disabled={status === 'loading'}>
        {status === 'loading' ? 'Analyse en cours…' : 'Générer la recommandation'}
      </button>

      {status === 'error' && (
        <button type="button" className="reservoir-form__retry" onClick={handleRetry}>
          Réessayer
        </button>
      )}
    </form>
  );
}