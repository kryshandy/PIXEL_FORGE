"""Engineering-calculation endpoints consumed by the frontend."""

from fastapi import APIRouter, status

from app.api.errors import ApiException
from app.api.schemas import (
    CalculationResponse,
    ErrorEnvelope,
    FracturePressureRequest,
    FracturePressureResponse,
    ProductivityIndexRequest,
)
from app.engineering.fracture_pressure import estimate_fracture_pressure_from_gradient
from app.engineering.productivity_index import (
    productivity_index_from_well_test,
    productivity_index_radial_flow,
)

router = APIRouter(prefix="/engineering-calculations", tags=["engineering-calculations"])


def _engineering_input_error(message: str) -> ApiException:
    return ApiException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        code="ENGINEERING_INPUT_INVALID",
        message=message,
    )


@router.post(
    "/productivity-index",
    response_model=CalculationResponse,
    responses={422: {"model": ErrorEnvelope, "description": "Invalid engineering inputs"}},
    summary="Calculer l'indice de productivité",
)
def calculate_productivity_index(request: ProductivityIndexRequest) -> CalculationResponse:
    """Calculate productivity index from either a well test or radial-flow inputs."""
    try:
        if request.calculation_type == "well_test":
            result = productivity_index_from_well_test(
                oil_rate_stb_day=request.oil_rate_stb_day or 0.0,
                reservoir_pressure_psi=request.reservoir_pressure_psi or 0.0,
                flowing_bottomhole_pressure_psi=request.flowing_bottomhole_pressure_psi or 0.0,
            )
        else:
            result = productivity_index_radial_flow(
                permeability_md=request.permeability_md or 0.0,
                net_pay_ft=request.net_pay_ft or 0.0,
                oil_viscosity_cp=request.oil_viscosity_cp or 0.0,
                oil_fvf_rb_stb=request.oil_fvf_rb_stb or 0.0,
                drainage_radius_ft=request.drainage_radius_ft or 0.0,
                wellbore_radius_ft=request.wellbore_radius_ft or 0.0,
                skin_factor=request.skin_factor,
                regime=request.flow_regime,
            )
    except ValueError as error:
        raise _engineering_input_error(str(error)) from error

    return CalculationResponse(
        calculation_type=request.calculation_type,
        value=result.value,
        unit=result.unit,
        method=result.method,
        assumptions=list(result.assumptions),
    )


@router.post(
    "/fracture-pressure",
    response_model=FracturePressureResponse,
    responses={422: {"model": ErrorEnvelope, "description": "Invalid engineering inputs"}},
    summary="Estimer la pression de fracturation",
)
def calculate_fracture_pressure(request: FracturePressureRequest) -> FracturePressureResponse:
    """Return a depth-gradient fracture-pressure screening estimate."""
    try:
        result = estimate_fracture_pressure_from_gradient(
            true_vertical_depth_ft=request.true_vertical_depth_ft,
            fracture_gradient_psi_per_ft=request.fracture_gradient_psi_per_ft,
            safety_margin_psi=request.safety_margin_psi,
        )
    except ValueError as error:
        raise _engineering_input_error(str(error)) from error

    return FracturePressureResponse(
        fracture_pressure_psi=result.fracture_pressure_psi,
        recommended_maximum_treating_pressure_psi=result.recommended_maximum_treating_pressure_psi,
        fracture_gradient_psi_per_ft=result.fracture_gradient_psi_per_ft,
        unit=result.unit,
        method=result.method,
        assumptions=list(result.assumptions),
    )
