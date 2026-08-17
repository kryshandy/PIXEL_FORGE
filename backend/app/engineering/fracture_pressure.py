"""Screening-level fracture-pressure calculations for conventional wells."""

from __future__ import annotations

import math
from dataclasses import dataclass

_PRESSURE_UNIT = "psi"


@dataclass(frozen=True, slots=True)
class FracturePressureResult:
    """Fracture-pressure estimate with its operational screening limit."""

    fracture_pressure_psi: float
    recommended_maximum_treating_pressure_psi: float
    fracture_gradient_psi_per_ft: float
    unit: str
    method: str
    assumptions: tuple[str, ...]


def _require_finite_positive(name: str, value: float) -> None:
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be finite and greater than zero.")


def estimate_fracture_pressure_from_gradient(
    *,
    true_vertical_depth_ft: float,
    fracture_gradient_psi_per_ft: float,
    safety_margin_psi: float = 0.0,
) -> FracturePressureResult:
    """Estimate fracture pressure from a local fracture gradient and TVD.

    The relationship is ``P_frac = TVD * fracture_gradient``. The returned
    recommended maximum treating pressure subtracts the requested safety margin.
    This is a screening calculation, not a hydraulic-fracture treatment design.
    """
    _require_finite_positive("true_vertical_depth_ft", true_vertical_depth_ft)
    _require_finite_positive("fracture_gradient_psi_per_ft", fracture_gradient_psi_per_ft)

    if not math.isfinite(safety_margin_psi) or safety_margin_psi < 0:
        raise ValueError("safety_margin_psi must be finite and greater than or equal to zero.")

    fracture_pressure_psi = true_vertical_depth_ft * fracture_gradient_psi_per_ft
    if safety_margin_psi >= fracture_pressure_psi:
        raise ValueError("safety_margin_psi must be lower than the estimated fracture pressure.")

    return FracturePressureResult(
        fracture_pressure_psi=fracture_pressure_psi,
        recommended_maximum_treating_pressure_psi=fracture_pressure_psi - safety_margin_psi,
        fracture_gradient_psi_per_ft=fracture_gradient_psi_per_ft,
        unit=_PRESSURE_UNIT,
        method="gradient_depth_estimate",
        assumptions=(
            "True vertical depth is used as the depth reference",
            "The supplied fracture gradient is representative of the target interval",
            "Result is a screening estimate and requires geomechanics validation before operations",
        ),
    )
