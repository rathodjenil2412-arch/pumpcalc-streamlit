"""Engineering calculations for the PumpCalc Streamlit application.

The equations assume water is transferred between two open reservoirs. Static
head and Darcy-Weisbach pipe-friction losses are included. Minor losses,
pressure-vessel terms and velocity at the reservoir free surfaces are omitted.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import pi
from typing import Optional


STANDARD_MOTOR_RATINGS_KW = (
    0.37,
    0.55,
    0.75,
    1.10,
    1.50,
    2.20,
    3.00,
    4.00,
    5.50,
    7.50,
    11.00,
    15.00,
    18.50,
    22.00,
    30.00,
    37.00,
    45.00,
    55.00,
    75.00,
    90.00,
)


@dataclass(frozen=True)
class PumpInputs:
    """User inputs in the units displayed by the app."""

    flow_lps: float
    suction_head_m: float
    delivery_head_m: float
    suction_length_m: float
    suction_diameter_mm: float
    delivery_length_m: float
    delivery_diameter_mm: float
    darcy_friction_factor: float
    efficiency_percent: float
    service_factor: float
    density_kg_m3: float = 1000.0
    gravity_m_s2: float = 9.81


@dataclass(frozen=True)
class PumpResults:
    """Calculated pump and pipe quantities in SI units."""

    flow_m3_s: float
    flow_m3_h: float
    suction_diameter_m: float
    delivery_diameter_m: float
    suction_area_m2: float
    delivery_area_m2: float
    suction_velocity_m_s: float
    delivery_velocity_m_s: float
    suction_friction_head_m: float
    delivery_friction_head_m: float
    total_friction_head_m: float
    static_head_m: float
    total_manometric_head_m: float
    water_power_kw: float
    shaft_power_kw: float
    shaft_power_hp: float
    design_motor_power_kw: float
    recommended_motor_kw: Optional[float]


def validate_inputs(data: PumpInputs) -> list[str]:
    """Return clear messages for values that make the calculation invalid."""

    errors: list[str] = []
    if data.flow_lps <= 0:
        errors.append("Flow rate must be greater than zero.")
    if data.suction_head_m < 0 or data.delivery_head_m < 0:
        errors.append("Static suction and delivery heads cannot be negative.")
    if data.suction_length_m < 0 or data.delivery_length_m < 0:
        errors.append("Pipe lengths cannot be negative.")
    if data.suction_diameter_mm <= 0 or data.delivery_diameter_mm <= 0:
        errors.append("Both pipe diameters must be greater than zero.")
    if data.darcy_friction_factor <= 0:
        errors.append("Darcy friction factor must be greater than zero.")
    if not 0 < data.efficiency_percent <= 100:
        errors.append("Pump efficiency must be between 0 and 100 percent.")
    if data.service_factor < 1:
        errors.append("Motor service factor must be at least 1.00.")
    if data.density_kg_m3 <= 0 or data.gravity_m_s2 <= 0:
        errors.append("Density and gravitational acceleration must be positive.")
    return errors


def recommend_motor(design_power_kw: float) -> Optional[float]:
    """Return the next common motor rating at or above the design power."""

    for rating in STANDARD_MOTOR_RATINGS_KW:
        if rating >= design_power_kw:
            return rating
    return None


def calculate_pump(data: PumpInputs) -> PumpResults:
    """Calculate head losses, pump power and the recommended motor rating."""

    errors = validate_inputs(data)
    if errors:
        raise ValueError(" ".join(errors))

    flow_m3_s = data.flow_lps / 1000.0
    flow_m3_h = flow_m3_s * 3600.0
    suction_diameter_m = data.suction_diameter_mm / 1000.0
    delivery_diameter_m = data.delivery_diameter_mm / 1000.0

    suction_area_m2 = pi * suction_diameter_m**2 / 4.0
    delivery_area_m2 = pi * delivery_diameter_m**2 / 4.0
    suction_velocity_m_s = flow_m3_s / suction_area_m2
    delivery_velocity_m_s = flow_m3_s / delivery_area_m2

    suction_friction_head_m = (
        data.darcy_friction_factor
        * (data.suction_length_m / suction_diameter_m)
        * (suction_velocity_m_s**2 / (2.0 * data.gravity_m_s2))
    )
    delivery_friction_head_m = (
        data.darcy_friction_factor
        * (data.delivery_length_m / delivery_diameter_m)
        * (delivery_velocity_m_s**2 / (2.0 * data.gravity_m_s2))
    )

    total_friction_head_m = suction_friction_head_m + delivery_friction_head_m
    static_head_m = data.suction_head_m + data.delivery_head_m
    total_manometric_head_m = static_head_m + total_friction_head_m

    water_power_kw = (
        data.density_kg_m3
        * data.gravity_m_s2
        * flow_m3_s
        * total_manometric_head_m
        / 1000.0
    )
    shaft_power_kw = water_power_kw / (data.efficiency_percent / 100.0)
    shaft_power_hp = shaft_power_kw * 1.34102209
    design_motor_power_kw = shaft_power_kw * data.service_factor

    return PumpResults(
        flow_m3_s=flow_m3_s,
        flow_m3_h=flow_m3_h,
        suction_diameter_m=suction_diameter_m,
        delivery_diameter_m=delivery_diameter_m,
        suction_area_m2=suction_area_m2,
        delivery_area_m2=delivery_area_m2,
        suction_velocity_m_s=suction_velocity_m_s,
        delivery_velocity_m_s=delivery_velocity_m_s,
        suction_friction_head_m=suction_friction_head_m,
        delivery_friction_head_m=delivery_friction_head_m,
        total_friction_head_m=total_friction_head_m,
        static_head_m=static_head_m,
        total_manometric_head_m=total_manometric_head_m,
        water_power_kw=water_power_kw,
        shaft_power_kw=shaft_power_kw,
        shaft_power_hp=shaft_power_hp,
        design_motor_power_kw=design_motor_power_kw,
        recommended_motor_kw=recommend_motor(design_motor_power_kw),
    )


def system_curve(results: PumpResults, points: int = 80) -> tuple[list[float], list[float]]:
    """Return flow (m3/h) and system head (m) points from zero to 150% flow."""

    if points < 2:
        raise ValueError("At least two curve points are required.")

    maximum_flow = results.flow_m3_h * 1.5
    flow_values = [maximum_flow * index / (points - 1) for index in range(points)]
    head_values = [
        results.static_head_m
        + results.total_friction_head_m * (flow / results.flow_m3_h) ** 2
        for flow in flow_values
    ]
    return flow_values, head_values
