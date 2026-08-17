import math

import pytest

from app.engineering.fracture_pressure import estimate_fracture_pressure_from_gradient


class TestEstimateFracturePressureFromGradient:
    def test_returns_fracture_pressure_and_screening_limit(self) -> None:
        result = estimate_fracture_pressure_from_gradient(
            true_vertical_depth_ft=10_000.0,
            fracture_gradient_psi_per_ft=0.75,
            safety_margin_psi=500.0,
        )

        assert result.fracture_pressure_psi == pytest.approx(7_500.0)
        assert result.recommended_maximum_treating_pressure_psi == pytest.approx(7_000.0)
        assert result.method == "gradient_depth_estimate"
        assert result.unit == "psi"

    @pytest.mark.parametrize(
        ("depth", "gradient", "margin"),
        [
            (0.0, 0.75, 0.0),
            (10_000.0, 0.0, 0.0),
            (math.nan, 0.75, 0.0),
            (10_000.0, math.inf, 0.0),
            (10_000.0, 0.75, -1.0),
            (10_000.0, 0.75, 7_500.0),
        ],
    )
    def test_rejects_invalid_or_unsafe_inputs(
        self,
        depth: float,
        gradient: float,
        margin: float,
    ) -> None:
        with pytest.raises(ValueError):
            estimate_fracture_pressure_from_gradient(
                true_vertical_depth_ft=depth,
                fracture_gradient_psi_per_ft=gradient,
                safety_margin_psi=margin,
            )
