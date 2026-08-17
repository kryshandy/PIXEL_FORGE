"""Public request and response contracts for the versioned REST API."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, model_validator

from app.engineering.productivity_index import FlowRegime


def to_camel(value: str) -> str:
    """Convert Python snake_case field names to the JSON camelCase contract."""
    first, *rest = value.split("_")
    return first + "".join(part.capitalize() for part in rest)


class ApiModel(BaseModel):
    """Base model that keeps Python internals and JSON contracts idiomatic."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, extra="forbid")


class ApiErrorDetail(ApiModel):
    field: str | None = None
    message: str
    code: str


class ApiError(ApiModel):
    code: str
    message: str
    details: list[ApiErrorDetail] = Field(default_factory=list)
    request_id: str


class ErrorEnvelope(ApiModel):
    error: ApiError


class ProductivityIndexRequest(ApiModel):
    """One request model for the two supported productivity-index methods."""

    calculation_type: Literal["well_test", "radial_flow"]
    oil_rate_stb_day: float | None = Field(default=None, ge=0)
    reservoir_pressure_psi: float | None = Field(default=None, gt=0)
    flowing_bottomhole_pressure_psi: float | None = Field(default=None, gt=0)
    permeability_md: float | None = Field(default=None, gt=0)
    net_pay_ft: float | None = Field(default=None, gt=0)
    oil_viscosity_cp: float | None = Field(default=None, gt=0)
    oil_fvf_rb_stb: float | None = Field(default=None, gt=0)
    drainage_radius_ft: float | None = Field(default=None, gt=0)
    wellbore_radius_ft: float | None = Field(default=None, gt=0)
    skin_factor: float = 0.0
    flow_regime: FlowRegime = FlowRegime.PSEUDO_STEADY_STATE

    @model_validator(mode="after")
    def validate_required_fields(self) -> ProductivityIndexRequest:
        fields_by_method = {
            "well_test": (
                "oil_rate_stb_day",
                "reservoir_pressure_psi",
                "flowing_bottomhole_pressure_psi",
            ),
            "radial_flow": (
                "permeability_md",
                "net_pay_ft",
                "oil_viscosity_cp",
                "oil_fvf_rb_stb",
                "drainage_radius_ft",
                "wellbore_radius_ft",
            ),
        }
        missing_fields = [
            field_name
            for field_name in fields_by_method[self.calculation_type]
            if getattr(self, field_name) is None
        ]
        if missing_fields:
            missing = ", ".join(to_camel(field_name) for field_name in missing_fields)
            raise ValueError(f"Missing required fields for {self.calculation_type}: {missing}.")
        return self


class CalculationResponse(ApiModel):
    calculation_type: str
    value: float
    unit: str
    method: str
    assumptions: list[str]


class FracturePressureRequest(ApiModel):
    true_vertical_depth_ft: float = Field(gt=0)
    fracture_gradient_psi_per_ft: float = Field(gt=0)
    safety_margin_psi: float = Field(default=0.0, ge=0)


class FracturePressureResponse(ApiModel):
    fracture_pressure_psi: float
    recommended_maximum_treating_pressure_psi: float
    fracture_gradient_psi_per_ft: float
    unit: str
    method: str
    assumptions: list[str]


class SourceCitation(ApiModel):
    source_type: Literal["rag", "calculation", "reference"]
    title: str = Field(min_length=1, max_length=180)
    excerpt: str = Field(min_length=1, max_length=1_000)
    url: HttpUrl | None = None


class RecommendationRequest(ApiModel):
    well_name: str = Field(min_length=1, max_length=100)
    rock_type: str = Field(min_length=1, max_length=80)
    porosity_fraction: float = Field(ge=0, le=1)
    permeability_md: float = Field(gt=0)
    reservoir_pressure_psi: float = Field(gt=0)
    true_vertical_depth_ft: float = Field(gt=0)
    productivity_index_stb_day_psi: float | None = Field(default=None, ge=0)
    fracture_pressure_psi: float | None = Field(default=None, gt=0)
    sources: list[SourceCitation] = Field(default_factory=list, max_length=10)


class RecommendationResponse(ApiModel):
    status: Literal["preliminary"]
    recommendation: str
    sources: list[SourceCitation]
    disclaimer: str
