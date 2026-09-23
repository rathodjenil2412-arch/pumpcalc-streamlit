"""Regression tests for the manual example used in the project report."""

import unittest

from pump_calculations import PumpInputs, calculate_pump, recommend_motor, system_curve


class PumpCalculationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.example = PumpInputs(
            flow_lps=10.0,
            suction_head_m=3.0,
            delivery_head_m=17.0,
            suction_length_m=6.0,
            suction_diameter_mm=100.0,
            delivery_length_m=30.0,
            delivery_diameter_mm=80.0,
            darcy_friction_factor=0.02,
            efficiency_percent=70.0,
            service_factor=1.15,
        )

    def test_manual_example(self) -> None:
        result = calculate_pump(self.example)
        self.assertAlmostEqual(result.suction_velocity_m_s, 1.27324, places=5)
        self.assertAlmostEqual(result.delivery_velocity_m_s, 1.98944, places=5)
        self.assertAlmostEqual(result.suction_friction_head_m, 0.09915, places=5)
        self.assertAlmostEqual(result.delivery_friction_head_m, 1.51294, places=5)
        self.assertAlmostEqual(result.total_manometric_head_m, 21.61210, places=5)
        self.assertAlmostEqual(result.water_power_kw, 2.12015, places=5)
        self.assertAlmostEqual(result.shaft_power_kw, 3.02878, places=5)
        self.assertEqual(result.recommended_motor_kw, 4.0)

    def test_motor_selection_uses_next_rating(self) -> None:
        self.assertEqual(recommend_motor(3.01), 4.0)
        self.assertEqual(recommend_motor(4.0), 4.0)
        self.assertIsNone(recommend_motor(100.0))

    def test_invalid_diameter_is_rejected(self) -> None:
        invalid = PumpInputs(**{**self.example.__dict__, "delivery_diameter_mm": 0.0})
        with self.assertRaises(ValueError):
            calculate_pump(invalid)

    def test_system_curve_passes_through_design_point(self) -> None:
        result = calculate_pump(self.example)
        flows, heads = system_curve(result, points=4)
        self.assertAlmostEqual(flows[2], result.flow_m3_h, places=10)
        self.assertAlmostEqual(heads[2], result.total_manometric_head_m, places=10)


if __name__ == "__main__":
    unittest.main()
