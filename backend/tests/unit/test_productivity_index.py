import math

import pytest

from app.engineering.productivity_index import (
    FlowRegime,
    productivity_index_from_well_test,
    productivity_index_radial_flow,
)


class TestProductivityIndexFromWellTest:
    def test_returns_rate_divided_by_pressure_drawdown(self) -> None:
        result = productivity_index_from_well_test(
            oil_rate_stb_day=1_000.0,
            reservoir_pressure_psi=3_000.0,
            flowing_bottomhole_pressure_psi=2_500.0,
        )

        assert result.value == pytest.approx(2.0)
        assert result.unit == "STB/day/psi"
        assert result.method == "well_test"

    def test_allows_zero_rate_for_a_non_productive_well(self) -> None:
        result = productivity_index_from_well_test(
            oil_rate_stb_day=0.0,
            reservoir_pressure_psi=3_000.0,
            flowing_bottomhole_pressure_psi=2_500.0,
        )

        assert result.value == 0.0

    @pytest.mark.parametrize(
        ("oil_rate", "reservoir_pressure", "flowing_pressure"),
        [
            (-1.0, 3_000.0, 2_500.0),
            (1_000.0, 2_500.0, 2_500.0),
            (1_000.0, 2_400.0, 2_500.0),
            (math.inf, 3_000.0, 2_500.0),
        ],
    )
    def test_rejects_invalid_measurements(
        self,
        oil_rate: float,
        reservoir_pressure: float,
        flowing_pressure: float,
    ) -> None:
        with pytest.raises(ValueError):
            productivity_index_from_well_test(
                oil_rate_stb_day=oil_rate,
                reservoir_pressure_psi=reservoir_pressure,
                flowing_bottomhole_pressure_psi=flowing_pressure,
            )


class TestProductivityIndexRadialFlow:
    def test_calculates_pseudo_steady_state_field_units_result(self) -> None:
        result = productivity_index_radial_flow(
            permeability_md=50.0,
            net_pay_ft=40.0,
            oil_viscosity_cp=2.0,
            oil_fvf_rb_stb=1.2,
            drainage_radius_ft=1_000.0,
            wellbore_radius_ft=0.33,
        )

        assert result.value == pytest.approx(0.8119544, rel=1e-6)
        assert result.unit == "STB/day/psi"
        assert result.method == "radial_flow:pseudo_steady_state"

    def test_positive_skin_reduces_productivity(self) -> None:
        base_inputs = {
            "permeability_md": 50.0,
            "net_pay_ft": 40.0,
            "oil_viscosity_cp": 2.0,
            "oil_fvf_rb_stb": 1.2,
            "drainage_radius_ft": 1_000.0,
            "wellbore_radius_ft": 0.33,
        }

        undamaged = productivity_index_radial_flow(**base_inputs, skin_factor=0.0)
        damaged = productivity_index_radial_flow(**base_inputs, skin_factor=8.0)

        assert damaged.value < undamaged.value

    def test_supports_steady_state_boundary_assumption(self) -> None:
        result = productivity_index_radial_flow(
            permeability_md=50.0,
            net_pay_ft=40.0,
            oil_viscosity_cp=2.0,
            oil_fvf_rb_stb=1.2,
            drainage_radius_ft=1_000.0,
            wellbore_radius_ft=0.33,
            regime=FlowRegime.STEADY_STATE,
        )

        assert result.method == "radial_flow:steady_state"
        assert "Constant-pressure outer boundary" in result.assumptions

    @pytest.mark.parametrize(
        ("field", "invalid_value"),
        [
            ("permeability_md", 0.0),
            ("net_pay_ft", -1.0),
            ("oil_viscosity_cp", math.nan),
            ("oil_fvf_rb_stb", 0.0),
            ("drainage_radius_ft", -100.0),
            ("wellbore_radius_ft", 0.0),
        ],
    )
    def test_rejects_non_positive_or_non_finite_physical_inputs(
        self,
        field: str,
        invalid_value: float,
    ) -> None:
        inputs = {
            "permeability_md": 50.0,
            "net_pay_ft": 40.0,
            "oil_viscosity_cp": 2.0,
            "oil_fvf_rb_stb": 1.2,
            "drainage_radius_ft": 1_000.0,
            "wellbore_radius_ft": 0.33,
        }
        inputs[field] = invalid_value

        with pytest.raises(ValueError):
            productivity_index_radial_flow(**inputs)

    def test_rejects_drainage_radius_not_greater_than_wellbore_radius(self) -> None:
        with pytest.raises(ValueError, match="drainage_radius_ft"):
            productivity_index_radial_flow(
                permeability_md=50.0,
                net_pay_ft=40.0,
                oil_viscosity_cp=2.0,
                oil_fvf_rb_stb=1.2,
                drainage_radius_ft=0.33,
                wellbore_radius_ft=0.33,
            )

    def test_rejects_a_non_positive_radial_flow_denominator(self) -> None:
        with pytest.raises(ValueError, match="denominator"):
            productivity_index_radial_flow(
                permeability_md=50.0,
                net_pay_ft=40.0,
                oil_viscosity_cp=2.0,
                oil_fvf_rb_stb=1.2,
                drainage_radius_ft=1_000.0,
                wellbore_radius_ft=0.33,
                skin_factor=-20.0,
            )

    def test_rejects_an_unknown_flow_regime(self) -> None:
        with pytest.raises(ValueError, match="regime must be one of"):
            productivity_index_radial_flow(
                permeability_md=50.0,
                net_pay_ft=40.0,
                oil_viscosity_cp=2.0,
                oil_fvf_rb_stb=1.2,
                drainage_radius_ft=1_000.0,
                wellbore_radius_ft=0.33,
                regime="transient",
            )
