"""Oil-well productivity-index calculations.

All public functions use explicit field units and return a structured result so the
future recommendation layer can display both the value and its engineering assumptions.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

_DARCY_FIELD_COEFFICIENT = 0.00708
_PRODUCTIVITY_INDEX_UNIT = "STB/day/psi"


class FlowRegime(str, Enum):
    """Supported radial-flow boundary assumptions."""

    STEADY_STATE = "steady_state"
    PSEUDO_STEADY_STATE = "pseudo_steady_state"


@dataclass(frozen=True, slots=True)
class ProductivityIndexResult:
    """A calculated productivity index with traceable context."""

    value: float
    unit: str
    method: str
    assumptions: tuple[str, ...]


def _require_finite(name: str, value: float) -> None:
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite.")


def _require_positive(name: str, value: float) -> None:
    _require_finite(name, value)
    if value <= 0:
        raise ValueError(f"{name} must be greater than zero.")


def productivity_index_from_well_test(
    *,
    oil_rate_stb_day: float,
    reservoir_pressure_psi: float,
    flowing_bottomhole_pressure_psi: float,
) -> ProductivityIndexResult:
    """Calculate ``J = q_o / (p_r - p_wf)`` from a stabilized well test.

    Args:
        oil_rate_stb_day: Stabilized surface oil rate in stock-tank barrels per day.
        reservoir_pressure_psi: Average reservoir pressure in psi.
        flowing_bottomhole_pressure_psi: Stabilized flowing bottom-hole pressure in psi.
    """
    _require_finite("oil_rate_stb_day", oil_rate_stb_day)
    if oil_rate_stb_day < 0:
        raise ValueError("oil_rate_stb_day must be greater than or equal to zero.")
    _require_positive("reservoir_pressure_psi", reservoir_pressure_psi)
    _require_positive("flowing_bottomhole_pressure_psi", flowing_bottomhole_pressure_psi)

    pressure_drawdown_psi = reservoir_pressure_psi - flowing_bottomhole_pressure_psi
    if pressure_drawdown_psi <= 0:
        raise ValueError(
            "reservoir_pressure_psi must be greater than "
            "flowing_bottomhole_pressure_psi."
        )

    return ProductivityIndexResult(
        value=oil_rate_stb_day / pressure_drawdown_psi,
        unit=_PRODUCTIVITY_INDEX_UNIT,
        method="well_test",
        assumptions=(
            "Stabilized single-phase oil flow",
            "Consistent surface-rate and pressure measurements",
        ),
    )


def productivity_index_radial_flow(
    *,
    permeability_md: float,
    net_pay_ft: float,
    oil_viscosity_cp: float,
    oil_fvf_rb_stb: float,
    drainage_radius_ft: float,
    wellbore_radius_ft: float,
    skin_factor: float = 0.0,
    regime: FlowRegime | str = FlowRegime.PSEUDO_STEADY_STATE,
) -> ProductivityIndexResult:
    """Estimate oil productivity index with the radial Darcy-flow equation.

    The field-units relationship is::

        J = 0.00708 * k * h / (mu_o * B_o * (ln(r_e / r_w) + correction + s))

    ``correction`` is ``0`` for steady state and ``-0.75`` for pseudo-steady state.
    The equation assumes homogeneous, isotropic, single-phase radial oil flow.
    """
    for name, value in (
        ("permeability_md", permeability_md),
        ("net_pay_ft", net_pay_ft),
        ("oil_viscosity_cp", oil_viscosity_cp),
        ("oil_fvf_rb_stb", oil_fvf_rb_stb),
        ("drainage_radius_ft", drainage_radius_ft),
        ("wellbore_radius_ft", wellbore_radius_ft),
    ):
        _require_positive(name, value)

    _require_finite("skin_factor", skin_factor)
    if drainage_radius_ft <= wellbore_radius_ft:
        raise ValueError("drainage_radius_ft must be greater than wellbore_radius_ft.")

    try:
        flow_regime = FlowRegime(regime)
    except ValueError as error:
        allowed_regimes = ", ".join(item.value for item in FlowRegime)
        raise ValueError(f"regime must be one of: {allowed_regimes}.") from error

    correction = -0.75 if flow_regime is FlowRegime.PSEUDO_STEADY_STATE else 0.0
    dimensionless_pressure_drop = (
        math.log(drainage_radius_ft / wellbore_radius_ft) + correction + skin_factor
    )
    if dimensionless_pressure_drop <= 0:
        raise ValueError(
            "The radial-flow denominator must be greater than zero; check radii and skin_factor."
        )

    value = (
        _DARCY_FIELD_COEFFICIENT
        * permeability_md
        * net_pay_ft
        / (oil_viscosity_cp * oil_fvf_rb_stb * dimensionless_pressure_drop)
    )
    boundary_assumption = (
        "Constant-pressure outer boundary"
        if flow_regime is FlowRegime.STEADY_STATE
        else "No-flow outer boundary after pressure stabilization"
    )

    return ProductivityIndexResult(
        value=value,
        unit=_PRODUCTIVITY_INDEX_UNIT,
        method=f"radial_flow:{flow_regime.value}",
        assumptions=(
            "Homogeneous and isotropic reservoir",
            "Single-phase, stabilized radial oil flow",
            boundary_assumption,
        ),
    )
