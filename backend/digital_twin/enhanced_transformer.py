"""
Enhanced Digital Twin Transformer Simulation Model for Aegis
Incorporates advanced electrical engineering principles for power transformers
Includes: Harmonics, losses breakdown, temperature effects on impedance,
dielectric considerations, and electromagnetic transient modeling
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List
import logging
import math

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedTransformerSimulator:
    """
    Enhanced Digital Twin simulator for power transformers
    Models comprehensive electrical, thermal, and aging behavior
    Incorporates IEEE C57.12.00, IEC 60076 standards
    """

    def __init__(self, transformer_rating_mva: float = 10.0,
                 voltage_rating_kv: float = 23.0,
                 temp_rise_limit_c: float = 65.0,
                 frequency_hz: float = 60.0,
                 impedance_percent: float = 8.0,
                 x_over_r_ratio: float = 20.0):
        """
        Initialize the enhanced transformer simulator

        Args:
            transformer_rating_mva: Transformer rating in MVA
            voltage_rating_kv: Voltage rating in kV (line-to-line)
            temp_rise_limit_c: Maximum allowable temperature rise above ambient (°C)
            frequency_hz: System frequency (Hz)
            impedance_percent: Percent impedance (%Z)
            x_over_r_ratio: Reactance to resistance ratio (X/R)
        """
        self.rating_mva = transformer_rating_mva
        self.voltage_rating_kv = voltage_rating_kv
        self.temp_rise_limit_c = temp_rise_limit_c
        self.frequency_hz = frequency_hz
        self.impedance_percent = impedance_percent
        self.x_over_r_ratio = x_over_r_ratio

        # Transformer characteristics (detailed losses breakdown)
        self._initialize_loss_characteristics()
        self._initialize_thermal_characteristics()
        self._initialize_electrical_parameters()
        self._initialize_aging_characteristics()
        self._initialize_dielectric_properties()

        self.logger = logger

    def _initialize_loss_characteristics(self):
        """Initialize detailed loss components per IEEE standards"""
        # No-load losses (core losses)
        self.no_load_losses_kw = self.rating_mva * 0.012  # Base: 1.2% of rating
        self.no_load_loss_components = {
            'hysteresis': self.no_load_losses_kw * 0.6,   # ~60% of no-load losses
            'eddy_current': self.no_load_losses_kw * 0.3, # ~30% of no-load losses
            'stray': self.no_load_losses_kw * 0.1         # ~10% of no-load losses
        }

        # Load losses (winding losses) - more detailed breakdown
        self.load_losses_kw_at_rated = self.rating_mva * 0.009  # Base: 0.9% of rating
        self.load_loss_components = {
            'i2r_dc': self.load_losses_kw_at_rated * 0.7,     # DC resistance losses
            'eddy_winding': self.load_losses_kw_at_rated * 0.15, # Eddy losses in windings
            'stray_load': self.load_losses_kw_at_rated * 0.1   # Stray load losses
        }

        # Harmonic loss factors (increase with frequency)
        self.harmonic_loss_factors = {
            3: 1.5,   # 3rd harmonic
            5: 1.8,   # 5th harmonic
            7: 2.2,   # 7th harmonic
            11: 2.5,  # 11th harmonic
            13: 2.8   # 13th harmonic
        }

    def _initialize_thermal_characteristics(self):
        """Initialize thermal modeling parameters"""
        # Thermal time constants (different for oil and windings)
        self.thermal_time_const_oil_hours = 2.5   # Oil thermal time constant
        self.thermal_time_const_winding_hours = 1.0  # Winding thermal time constant
        self.thermal_time_const_hotspot_hours = 0.5  # Hot spot thermal time constant

        # Thermal resistances (simplified lumped model)
        self.thermal_resistance_oil_to_ambient = 0.12  # °C/W
        self.thermal_resistance_winding_to_oil = 0.08  # °C/W
        self.thermal_resistance_hotspot_to_winding = 0.05  # °C/W

        # Reference conditions
        self.reference_ambient_temp_c = 20.0
        self.reference_winding_temp_c = self.reference_ambient_temp_c + self.temp_rise_limit_c
        self.reference_hotspot_temp_c = self.reference_winding_temp_c + 15.0  # Hot spot gradient

    def _initialize_electrical_parameters(self):
        """Initialize electrical parameters based on ratings"""
        # Calculate impedance values
        self.base_impedance_ohm = (self.voltage_rating_kv ** 2) * 1000 / self.rating_mva
        self.impedance_ohm = self.base_impedance_ohm * (self.impedance_percent / 100.0)

        # Split impedance into R and X components
        # Using: Z² = R² + X² and X/R = ratio
        x_over_r = self.x_over_r_ratio
        self.resistance_ohm = self.impedance_ohm / math.sqrt(1 + x_over_r ** 2)
        self.reactance_ohm = self.resistance_ohm * x_over_r

        # Calculate currents
        self.rated_current_a = (self.rating_mva * 1000) / (math.sqrt(3) * self.voltage_rating_kv)
        self.short_circuit_current_a = self.rated_current_a * (100 / self.impedance_percent)

        # Magnetizing current (typically 0.5-2% of rated current)
        self.magnetizing_current_a = self.rated_current_a * 0.01

        # Core loss conductance and susceptance
        self.core_loss_conductance_s = self.no_load_losses_kw * 1000 / (self.voltage_rating_kv * 1000 / math.sqrt(3)) ** 2
        self.magnetizing_susceptance_s = self.magnetizing_current_a / (self.voltage_rating_kv * 1000 / math.sqrt(3))

    def _initialize_aging_characteristics(self):
        """Initialize aging and life consumption models"""
        # Thermal aging (Arrhenius-based) per IEEE guides
        self.aging_acceleration_ea = 15000  # Activation energy (J/mol) for cellulose
        self.aging_acceleration_r = 8.314   # Gas constant (J/mol·K)
        self.aging_reference_temp_k = 373.0 + 273.15  # 100°C reference in Kelvin

        # Thermal aging exponent (more accurate model)
        self.thermal_aging_exponent = {
            (80, 90): 6.0,
            (90, 95): 8.0,
            (95, 100): 10.0,
            (100, 110): 12.0,
            (110, 120): 15.0,
            (120, 130): 18.0
        }

        # Mechanical aging factors
        self.vibration_aging_factor = 0.0  # Will be calculated based on operating conditions
        self.mechanical_stress_exponent = 3.0  # For short-circuit forces

        # Dielectric aging (simplified)
        self.dielectric_aging_rate = 0.0001  # Base rate per hour at reference conditions

    def _initialize_dielectric_properties(self):
        """Initialize dielectric and insulation properties"""
        # Insulation levels (kV)
        self.bil_level_kv = self.voltage_rating_kv * 3.0  # Basic Impulse Level
        # Typical BIL: 150kV for 23kV class, 200kV for 34.5kV class, etc.
        if self.voltage_rating_kv <= 23.0:
            self.bil_level_kv = 150.0
        elif self.voltage_rating_kv <= 34.5:
            self.bil_level_kv = 200.0
        elif self.voltage_rating_kv <= 46.0:
            self.bil_level_kv = 250.0
        else:
            self.bil_level_kv = self.voltage_rating_kv * 3.5

        # Dielectric stress factors
        self.dielectric_stress_factor = 1.0  # Will be modified by harmonics, surges, etc.
        self.partial_discharge_inception_kv = self.voltage_rating_kv * 1.8  # Approximate

    def _calculate_detailed_losses(self, load_percent: float,
                                 harmonic_distortion_thd: float = 0.05) -> Dict[str, float]:
        """
        Calculate detailed transformer losses including harmonic effects

        Args:
            load_percent: Load as percentage of rated capacity
            harmonic_distortion_thd: Total Harmonic Distortion (as decimal)

        Returns:
            Dictionary of loss components in kW
        """
        load_factor = load_percent / 100.0

        # No-load losses (core losses) - affected by voltage harmonics
        # Harmonic voltages increase hysteresis and eddy current losses
        voltage_thd = harmonic_distortion_thd * 0.8  # Assume voltage THD is 80% of current THD
        harmonic_loss_factor_no_load = 1.0 + (voltage_thd ** 2) * 2.0  # Approximate

        no_load_losses = {}
        total_no_load = 0.0
        for component, base_loss in self.no_load_loss_components.items():
            if component == 'hysteresis':
                # Hysteresis loss proportional to frequency and flux density
                loss = base_loss * harmonic_loss_factor_no_load
            elif component == 'eddy_current':
                # Eddy current loss proportional to frequency² and flux density²
                loss = base_loss * (harmonic_loss_factor_no_load ** 2)
            else:  # stray
                loss = base_loss * harmonic_loss_factor_no_load
            no_load_losses[component] = loss
            total_no_load += loss

        # Load losses (winding losses) - affected by current harmonics and skin/proximity effects
        harmonic_loss_factor_load = 1.0 + (harmonic_distortion_thd ** 2) * 3.0  # More pronounced for load losses

        # DC resistance losses (I²R)
        dc_loss_base = self.load_loss_components['i2r_dc'] * (load_factor ** 2)
        dc_loss = dc_loss_base * harmonic_loss_factor_load

        # Eddy losses in windings (increase with frequency² and harmonic content)
        eddy_loss_base = self.load_loss_components['eddy_winding'] * (load_factor ** 2)
        # Harmonic eddy losses increase significantly with harmonic order
        harmonic_eddy_multiplier = 1.0
        for h_order, h_factor in self.harmonic_loss_factors.items():
            harmonic_content = harmonic_distortion_thd / h_order  # Simplified harmonic distribution
            harmonic_eddy_multiplier += (harmonic_content ** 2) * (h_factor - 1.0)
        eddy_loss = eddy_loss_base * harmonic_eddy_multiplier * harmonic_loss_factor_load

        # Stray load losses (leakage flux effects)
        stray_loss_base = self.load_loss_components['stray_load'] * (load_factor ** 2)
        stray_loss = stray_loss_base * harmonic_loss_factor_load

        load_losses = {
            'i2r_dc': dc_loss,
            'eddy_winding': eddy_loss,
            'stray_load': stray_loss
        }
        total_load = dc_loss + eddy_loss + stray_loss

        # Total losses
        total_losses = total_no_load + total_load

        return {
            'no_load_losses': no_load_losses,
            'total_no_load_losses': total_no_load,
            'load_losses': load_losses,
            'total_load_losses': total_load,
            'total_losses': total_losses,
            'harmonic_loss_factor_no_load': harmonic_loss_factor_no_load,
            'harmonic_loss_factor_load': harmonic_loss_factor_load
        }

    def _calculate_advanced_temperatures(self, load_percent: float,
                                       ambient_temp_c: float,
                                       cooling_mode: str = "normal",
                                       harmonic_distortion_thd: float = 0.05,
                                       hours_at_conditions: float = 1.0) -> Dict[str, float]:
        """
        Calculate detailed temperatures using thermal network model

        Args:
            load_percent: Load as percentage of rated capacity
            ambient_temp_c: Ambient temperature in °C
            cooling_mode: Cooling effectiveness mode
            harmonic_distortion_thd: Current harmonic distortion
            hours_at_conditions: Hours at these thermal conditions

        Returns:
            Dictionary of temperatures in °C
        """
        # Get detailed losses
        losses = self._calculate_detailed_losses(load_percent, harmonic_distortion_thd)
        total_losses_watts = losses['total_losses'] * 1000  # Convert kW to W

        # Thermal capacitance values (J/°C) - simplified
        thermal_mass_oil_j = self.rating_mva * 10000  # Approximate: 10 kJ/kVA
        thermal_mass_winding_j = self.rating_mva * 3000   # Less mass for windings
        thermal_mass_hotspot_j = self.rating_mva * 1000   # Very localized

        # Calculate steady-state temperature rises
        # Using: ΔT = Losses × Thermal Resistance

        # Losses distribution (approximate)
        losses_to_oil_watts = total_losses_watts * 0.85   # 85% of losses go to oil first
        losses_to_winding_watts = total_losses_watts * 0.95  # 95% affect windings directly
        losses_to_hotspot_watts = losses_to_winding_watts * 0.3  # 30% of winding losses create hot spot

        # Calculate thermal resistances with corrections
        base_r_oa = self.thermal_resistance_oil_to_ambient  # Oil to ambient
        base_r_wo = self.thermal_resistance_winding_to_oil  # Winding to oil
        base_r_hw = self.thermal_resistance_hotspot_to_winding  # Hot spot to winding

        # Apply corrections for conditions
        # Oil viscosity changes with temperature (affects convection)
        oil_temp_estimate = ambient_temp_c + 40.0  # Rough estimate for correction
        viscosity_factor = max(0.7, min(1.5, 2.0 - oil_temp_estimate * 0.01))  # Simplified
        r_oa_corrected = base_r_oa / viscosity_factor

        # Winding to oil resistance slightly temp dependent
        r_wo_corrected = base_r_wo * (1.0 + (oil_temp_estimate - 40.0) * 0.002)

        # Hot spot factors
        hw_corrected = base_r_hw * (1.0 + harmonic_distortion_thd * 0.5)  # Harmonics increase hot spot

        # Cooling mode adjustments
        cooling_multipliers = {
            "off": 0.3,
            "reduced": 0.6,
            "normal": 1.0,
            "forced": 1.8,
            "directed_forced": 2.5
        }
        cooling_factor = cooling_multipliers.get(cooling_mode.lower(), 1.0)

        # Apply cooling correction to all thermal resistances
        r_oa_final = r_oa_corrected / cooling_factor
        r_wo_final = r_wo_corrected / cooling_factor
        r_hw_final = hw_corrected / cooling_factor

        # Calculate temperature rises (steady state)
        delta_t_oil = losses_to_oil_watts * r_oa_final
        delta_t_winding = losses_to_winding_watts * r_wo_final + delta_t_oil  # Winding hotter than oil
        delta_t_hotspot = losses_to_hotspot_watts * r_hw_final + delta_t_winding  # Hot spot hottest

        # Apply ambient correction (hotter ambient reduces cooling capacity)
        ambient_correction_factor = max(0.5, 1.0 - (ambient_temp_c - 25.0) * 0.015)
        delta_t_oil *= ambient_correction_factor
        delta_t_winding *= ambient_correction_factor
        delta_t_hotspot *= ambient_correction_factor

        # Calculate actual temperatures
        oil_temp_c = ambient_temp_c + delta_t_oil
        winding_temp_c = ambient_temp_c + delta_t_winding
        hotspot_temp_c = ambient_temp_c + delta_t_hotspot

        # Thermal time constant effects for transient behavior
        # Simplified first-order response
        if hours_at_conditions < 24:  # Not at steady state yet
            alpha_oil = 1.0 - math.exp(-hours_at_conditions / self.thermal_time_const_oil_hours)
            alpha_winding = 1.0 - math.exp(-hours_at_conditions / self.thermal_time_const_winding_hours)
            alpha_hotspot = 1.0 - math.exp(-hours_at_conditions / self.thermal_time_const_hotspot_hours)

            # Start from previous conditions (simplified - assume starting from ambient)
            oil_temp_c = ambient_temp_c + delta_t_oil * alpha_oil
            winding_temp_c = ambient_temp_c + delta_t_winding * alpha_winding
            hotspot_temp_c = ambient_temp_c + delta_t_hotspot * alpha_hotspot

        return {
            'oil_temp_c': oil_temp_c,
            'winding_temp_c': winding_temp_c,
            'hotspot_temp_c': hotspot_temp_c,
            'delta_t_oil': delta_t_oil,
            'delta_t_winding': delta_t_winding,
            'delta_t_hotspot': delta_t_hotspot,
            'thermal_time_constants': {
                'oil_hours': self.thermal_time_const_oil_hours,
                'winding_hours': self.thermal_time_const_winding_hours,
                'hotspot_hours': self.thermal_time_const_hotspot_hours
            }
        }

    def _calculate_electrical_parameters_at_temp(self, winding_temp_c: float) -> Dict[str, float]:
        """
        Calculate electrical parameters that vary with temperature

        Args:
            winding_temp_c: Winding temperature in °C

        Returns:
            Dictionary of temperature-corrected electrical parameters
        """
        # Resistance varies with temperature (approximately linear for copper)
        # R(T2) = R(T1) * [1 + α(T2 - T1)]
        # Where α = temperature coefficient of resistance (0.00393 for copper)
        temp_coefficient_resistance = 0.00393
        reference_temp_c = 75.0  # Typically referenced to 75°C

        resistance_factor = 1.0 + temp_coefficient_resistance * (winding_temp_c - reference_temp_c)
        resistance_at_temp_ohm = self.resistance_ohm * resistance_factor
        impedance_at_temp_ohm = math.sqrt(resistance_at_temp_ohm ** 2 + self.reactance_ohm ** 2)
        impedance_percent_at_temp = (impedance_at_temp_ohm / self.base_impedance_ohm) * 100.0

        # Reactance changes slightly with temperature due to magnetic permeability changes
        # For simplicity, we'll assume reactance is constant (dominated by geometry)
        reactance_at_temp_ohm = self.reactance_ohm

        # Calculate corrected currents and voltages
        rated_current_at_temp_a = (self.rating_mva * 1000) / (math.sqrt(3) * self.voltage_rating_kv)
        short_circuit_current_at_temp_a = rated_current_at_temp_a * (100 / impedance_percent_at_temp)

        # Voltage regulation changes with impedance
        # Simplified: %VR ≈ %R·cosφ + %X·sinφ
        power_factor = 0.95  # Lagging
        power_factor_angle = math.acos(power_factor)
        cos_phi = power_factor
        sin_phi = math.sin(power_factor_angle)

        percent_r = (resistance_at_temp_ohm / self.base_impedance_ohm) * 100.0
        percent_x = (self.reactance_ohm / self.base_impedance_ohm) * 100.0
        voltage_regulation_percent = percent_r * cos_phi + percent_x * sin_phi

        return {
            'resistance_ohm': resistance_at_temp_ohm,
            'reactance_ohm': reactance_at_temp_ohm,
            'impedance_ohm': impedance_at_temp_ohm,
            'impedance_percent': impedance_percent_at_temp,
            'rated_current_a': rated_current_at_temp_a,
            'short_circuit_current_a': short_circuit_current_at_temp_a,
            'voltage_regulation_percent': voltage_regulation_percent,
            'temperature_coefficient_applied': temp_coefficient_resistance * (winding_temp_c - reference_temp_c)
        }

    def _calculate_advanced_aging_and_health(self, temperatures: Dict[str, float],
                                           load_percent: float,
                                           harmonic_distortion_thd: float = 0.05,
                                           hours_at_condition: float = 1.0,
                                           vibration_rms_mm_s: float = 2.0,
                                           dielectric_stress_factor: float = 1.0) -> Dict[str, float]:
        """
        Calculate comprehensive aging and health metrics

        Args:
            temperatures: Dictionary from _calculate_advanced_temperatures
            load_percent: Load percentage
            harmonic_distortion_thd: THD as decimal
            hours_at_condition: Hours at these conditions
            vibration_rms_mm_s: RMS vibration velocity
            dielectric_stress_factor: Multiplier for dielectric stress

        Returns:
            Dictionary of health and aging metrics
        """
        winding_temp_c = temperatures['winding_temp_c']
        hotspot_temp_c = temperatures['hotspot_temp_c']
        oil_temp_c = temperatures['oil_temp_c']

        # 1. THERMAL AGING (Arrhenius-based, IEEE Guide)
        # More accurate piecewise exponential model
        thermal_aging_factor = self._calculate_thermal_aging_factor(winding_temp_c, hours_at_condition)

        # 2. HARMONIC INDUCED AGING
        # Harmonics increase eddy currents and localized heating
        harmonic_aging_factor = 1.0 + (harmonic_distortion_thd ** 2) * 0.5 * hours_at_condition

        # 3. VIBRATION INDUCED MECHANICAL AGING
        # Vibration causes mechanical wear on windings and clamping structures
        # Simplified model based on RMS velocity
        vibration_aging_factor = 1.0 + (vibration_rms_mm_s / 10.0) ** 2 * 0.1 * hours_at_condition

        # 4. DIELECTRIC AGING
        # Combined thermal, electrical, and environmental stress
        electric_stress_factor = load_percent / 100.0  # Normalized electrical loading
        dielectric_aging_factor = 1.0 + (
            (oil_temp_c / 100.0) ** 2 * 0.05 +  # Thermal component
            electric_stress_factor * 0.03 +       # Electrical component
            (dielectric_stress_factor - 1.0) * 0.1 # Environmental stress
        ) * hours_at_condition

        # 5. MECHANICAL STRESS FROM SHORT CIRCUIT FORCES (if applicable)
        # Electromagnetic forces proportional to current²
        load_factor = load_percent / 100.0
        em_force_factor = load_factor ** 2
        mechanical_stress_aging = 1.0 + (em_force_factor - 1.0) * 0.05 * hours_at_condition

        # Combined aging factors (multiplicative for independent mechanisms)
        combined_aging_factor = (
            thermal_aging_factor *
            harmonic_aging_factor *
            vibration_aging_factor *
            dielectric_aging_factor *
            mechanical_stress_aging
        )

        # Health impact (degradation per hour, normalized 0-1 scale)
        # Based on combination of factors exceeding design limits
        thermal_health_impact = max(0, (winding_temp_c - 90.0) / 20.0) * 0.4  # Significant above 90°C
        hotspot_health_impact = max(0, (hotspot_temp_c - 110.0) / 15.0) * 0.4  # Critical above 110°C
        overload_health_impact = max(0, (load_percent - 100.0) / 50.0) * 0.2   # Overload contribution

        health_impact_per_hour = min(
            thermal_health_impact + hotspot_health_impact + overload_health_impact,
            0.8  # Cap maximum degradation rate
        )

        # Remaining useful life estimation
        # Simplified: RUL hours = Design life hours / aging_factor
        design_life_hours = 180000  # ~20 years at 40°C ambient, average loading
        aging_rate_per_hour = (combined_aging_factor - 1.0) / hours_at_condition if hours_at_condition > 0 else 0.0
        if aging_rate_per_hour > 0:
            estimated_remaining_hours = design_life_hours / (1.0 + aging_rate_per_hour * 8760)  # Annualized
        else:
            estimated_remaining_hours = design_life_hours * 2  # Well under design conditions

        return {
            'thermal_aging_factor': thermal_aging_factor,
            'harmonic_aging_factor': harmonic_aging_factor,
            'vibration_aging_factor': vibration_aging_factor,
            'dielectric_aging_factor': dielectric_aging_factor,
            'mechanical_stress_aging': mechanical_stress_aging,
            'combined_aging_factor': combined_aging_factor,
            'health_impact_per_hour': health_impact_per_hour,
            'estimated_remaining_hours': estimated_remaining_hours,
            'design_life_hours': design_life_hours,
            'aging_rate_per_hour': aging_rate_per_hour,
            'hotspot_gradient_c': hotspot_temp_c - winding_temp_c,
            'oil_to_winding_gradient_c': winding_temp_c - oil_temp_c
        }

    def _calculate_thermal_aging_factor(self, winding_temp_c: float, hours: float) -> float:
        """
        Calculate thermal aging factor using piecewise exponential model
        Based on IEEE guides for transformer life expectancy
        """
        # Find appropriate aging curve segment
        aging_factor = 1.0  # Default: no aging

        # Piecewise definition: different acceleration factors per temperature range
        if winding_temp_c <= 80:
            # Below 80°C: minimal aging
            aging_factor = 1.0 + (winding_temp_c - 20.0) * 0.0001 * hours
        elif winding_temp_c <= 90:
            # 80-90°C: moderate aging
            base_factor = 6.0  # 6x faster than reference at 85°C avg
            aging_factor = 1.0 + (base_factor - 1.0) * ((winding_temp_c - 80) / 10.0) * hours * 0.001
        elif winding_temp_c <= 95:
            # 90-95°C: increasing aging
            base_factor = 8.0 + (winding_temp_c - 90) * 0.4  # 8-10x
            aging_factor = 1.0 + (base_factor - 1.0) * hours * 0.001
        elif winding_temp_c <= 100:
            # 95-100°C: significant aging
            base_factor = 10.0 + (winding_temp_c - 95) * 0.4  # 10-12x
            aging_factor = 1.0 + (base_factor - 1.0) * hours * 0.001
        elif winding_temp_c <= 110:
            # 100-110°C:高 aging
            base_factor = 12.0 + (winding_temp_c - 100) * 0.3  # 12-15x
            aging_factor = 1.0 + (base_factor - 1.0) * hours * 0.001
        elif winding_temp_c <= 120:
            # 110-120°C: very高 aging
            base_factor = 15.0 + (winding_temp_c - 110) * 0.2  # 15-17x
            aging_factor = 1.0 + (base_factor - 1.0) * hours * 0.001
        else:
            # Above 120°C:极快 aging
            base_factor = 18.0 + (winding_temp_c - 120) * 0.1  # 18-20x+
            aging_factor = 1.0 + (base_factor - 1.0) * hours * 0.001

        return max(1.0, aging_factor)

    def _calculate_advanced_risk_assessment(self, temperatures: Dict[str, float],
                                          electrical_params: Dict[str, float],
                                          aging_health: Dict[str, float],
                                          load_percent: float,
                                          harmonic_distortion_thd: float = 0.05,
                                          symmetry_imbalance_percent: float = 0.0,
                                          partial_discharge_detected: bool = False) -> Dict[str, Any]:
        """
        Calculate comprehensive risk assessment with multiple factors

        Args:
            temperatures: Temperature dictionary
            electrical_params: Electrical parameters dictionary
            aging_health: Aging and health dictionary
            load_percent: Load percentage
            harmonic_distortion_thd: THD as decimal
            symmetry_imbalance_percent: Phase current imbalance
            partial_discharge_detected: PD detection flag

        Returns:
            Dictionary of risk levels and contributing factors
        """
        winding_temp_c = temperatures['winding_temp_c']
        hotspot_temp_c = temperatures['hotspot_temp_c']
        aging_factor = aging_health['combined_aging_factor']
        health_impact = aging_health['health_impact_per_hour']

        # Initialize risk scores (0-5 scale, where 5 is critical)
        risk_scores = {
            'thermal_winding': 0,
            'thermal_hotspot': 0,
            'insulation_aging': 0,
            'overload': 0,
            'harmonics': 0,
            'dielectric_stress': 0,
            'mechanical_vibration': 0,
            'electrical_symmetry': 0,
            'partial_discharge': 0,
            'short_circuit_withstand': 0
        }

        # 1. THERMAL RISK - WINDING TEMPERATURE
        if winding_temp_c >= 110:
            risk_scores['thermal_winding'] = 5
        elif winding_temp_c >= 100:
            risk_scores['thermal_winding'] = 4
        elif winding_temp_c >= 90:
            risk_scores['thermal_winding'] = 3
        elif winding_temp_c >= 80:
            risk_scores['thermal_winding'] = 2
        elif winding_temp_c >= 70:
            risk_scores['thermal_winding'] = 1

        # 2. THERMAL RISK - HOT SPOT TEMPERATURE (most critical)
        if hotspot_temp_c >= 140:
            risk_scores['thermal_hotspot'] = 5
        elif hotspot_temp_c >= 130:
            risk_scores['thermal_hotspot'] = 4
        elif hotspot_temp_c >= 120:
            risk_scores['thermal_hotspot'] = 3
        elif hotspot_temp_c >= 110:
            risk_scores['thermal_hotspot'] = 2
        elif hotspot_temp_c >= 100:
            risk_scores['thermal_hotspot'] = 1

        # 3. INSULATION AGING RISK
        if aging_factor >= 3.0:
            risk_scores['insulation_aging'] = 5
        elif aging_factor >= 2.0:
            risk_scores['insulation_aging'] = 4
        elif aging_factor >= 1.5:
            risk_scores['insulation_aging'] = 3
        elif aging_factor >= 1.2:
            risk_scores['insulation_aging'] = 2
        elif aging_factor >= 1.05:
            risk_scores['insulation_aging'] = 1

        # 4. OVERLOAD RISK
        if load_percent >= 140:
            risk_scores['overload'] = 5
        elif load_percent >= 120:
            risk_scores['overload'] = 4
        elif load_percent >= 110:
            risk_scores['overload'] = 3
        elif load_percent >= 105:
            risk_scores['overload'] = 2
        elif load_percent >= 100:
            risk_scores['overload'] = 1

        # 5. HARMONIC RISK
        thd_risk = min(5.0, harmonic_distortion_thd * 20)  # 25% THD = level 5 risk
        risk_scores['harmonics'] = min(5.0, thd_risk)

        # 6. DIELECTRIC STRESS RISK (based on voltage stress and contamination)
        # Simplified: based on operating voltage vs BIL and contamination factors
        dielectric_stress = min(5.0, (load_percent / 100.0) * 2.0)  # Simplified
        risk_scores['dielectric_stress'] = dielectric_stress

        # 7. MECHANICAL VIBRATION RISK (would need actual vibration input)
        # Placeholder - would use actual vibration monitoring data
        risk_scores['mechanical_vibration'] = 1.0  # Low baseline

        # 8. ELECTRICAL SYMMETRY RISK (phase imbalance)
        imbalance_risk = min(5.0, symmetry_imbalance_percent * 0.1)  # 50% imbalance = level 5
        risk_scores['electrical_symmetry'] = imbalance_risk

        # 9. PARTIAL DISCHARGE RISK
        if partial_discharge_detected:
            risk_scores['partial_discharge'] = 5
        elif aging_factor > 2.0:  # PD likelihood increases with aging
            risk_scores['partial_discharge'] = 3
        else:
            risk_scores['partial_discharge'] = 0

        # 10. SHORT CIRCUIT WITHSTAND RISK (aging reduces withstand capability)
        # Simplified: aged insulation has reduced mechanical strength
        sc_withstand_reduction = min(0.5, (aging_factor - 1.0) * 0.1)  # Up to 50% reduction
        if sc_withstand_reduction >= 0.4:
            risk_scores['short_circuit_withstand'] = 5
        elif sc_withstand_reduction >= 0.3:
            risk_scores['short_circuit_withstand'] = 4
        elif sc_withstand_reduction >= 0.2:
            risk_scores['short_circuit_withstand'] = 3
        elif sc_withstand_reduction >= 0.1:
            risk_scores['short_circuit_withstand'] = 2
        elif sc_withstand_reduction > 0:
            risk_scores['short_circuit_withstand'] = 1

        # Determine overall risk level (take maximum, but consider combinations)
        max_individual_risk = max(risk_scores.values())

        # Apply risk level thresholds
        if max_individual_risk >= 4.5 or risk_scores['thermal_hotspot'] >= 4:
            overall_risk = "CRITICAL"
            risk_level_numeric = 5
        elif max_individual_risk >= 3.5:
            overall_risk = "HIGH"
            risk_level_numeric = 4
        elif max_individual_risk >= 2.5:
            overall_risk = "MEDIUM"
            risk_level_numeric = 3
        elif max_individual_risk >= 1.5:
            overall_risk = "LOW"
            risk_level_numeric = 2
        else:
            overall_risk = "MINIMAL"
            risk_level_numeric = 1

        # Calculate confidence in assessment based on data quality
        # More parameters measured = higher confidence
        measured_parameters = 8  # Base set we always have
        if harmonic_distortion_thd > 0:
            measured_parameters += 1
        if symmetry_imbalance_percent > 0:
            measured_parameters += 1
        if partial_discharge_detected is not None:  # We know the status
            measured_parameters += 1

        confidence_score = min(0.95, 0.6 + (measured_parameters - 6) * 0.05)

        return {
            'risk_scores': risk_scores,
            'max_individual_risk': max_individual_risk,
            'overall_risk_level': overall_risk,
            'risk_level_numeric': risk_level_numeric,
            'confidence_score': confidence_score,
            'contributing_factors': {
                k: v for k, v in risk_scores.items() if v >= 2.0  # Significant contributors
            }
        }

    def simulate_enhanced(self, load_percent: float,
                        ambient_temp_c: float,
                        cooling_mode: str = "normal",
                        harmonic_distortion_thd: float = 0.05,
                        hours_at_conditions: float = 1.0,
                        vibration_rms_mm_s: float = 2.0,
                        dielectric_stress_factor: float = 1.0,
                        symmetry_imbalance_percent: float = 0.0,
                        partial_discharge_detected: bool = False) -> Dict[str, Any]:
        """
        Enhanced transformer simulation with comprehensive electrical, thermal, and aging modeling

        Args:
            load_percent: Load as percentage of rated capacity (0-200)
            ambient_temp_c: Ambient temperature in °C
            cooling_mode: Cooling mode ("normal", "reduced", "off", "forced", "directed_forced")
            harmonic_distortion_thd: Current THD as decimal (0.0-1.0)
            hours_at_conditions: Hours at these operating conditions
            vibration_rms_mm_s: RMS vibration velocity in mm/s
            dielectric_stress_factor: Dielectric stress multiplier
            symmetry_imbalance_percent: Phase current imbalance percentage
            partial_discharge_detected: Boolean indicating PD detection

        Returns:
            Comprehensive dictionary containing all simulation results
        """
        # Validate and clamp inputs
        load_percent = max(0, min(200, load_percent))
        ambient_temp_c = max(-40, min(60, ambient_temp_c))
        cooling_mode = cooling_mode.lower()
        harmonic_distortion_thd = max(0.0, min(0.5, harmonic_distortion_thd))  # Clamp THD
        hours_at_conditions = max(0.0, min(8760.0, hours_at_conditions))  # Max 1 year
        vibration_rms_mm_s = max(0.0, min(50.0, vibration_rms_mm_s))
        dielectric_stress_factor = max(0.5, min(3.0, dielectric_stress_factor))
        symmetry_imbalance_percent = max(0.0, min(50.0, symmetry_imbalance_percent))  # Max 50% imbalance

        # Step 1: Calculate detailed losses (including harmonics)
        losses = self._calculate_detailed_losses(load_percent, harmonic_distortion_thd)

        # Step 2: Calculate detailed temperatures using thermal network
        temperatures = self._calculate_advanced_temperatures(
            load_percent, ambient_temp_c, cooling_mode,
            harmonic_distortion_thd, hours_at_conditions
        )

        # Step 3: Calculate temperature-dependent electrical parameters
        electrical_params = self._calculate_electrical_parameters_at_temp(
            temperatures['winding_temp_c']
        )

        # Step 4: Calculate comprehensive aging and health metrics
        aging_health = self._calculate_advanced_aging_and_health(
            temperatures, load_percent, harmonic_distortion_thd,
            hours_at_conditions, vibration_rms_mm_s, dielectric_stress_factor
        )

        # Step 5: Calculate comprehensive risk assessment
        risk_assessment = self._calculate_advanced_risk_assessment(
            temperatures, electrical_params, aging_health,
            load_percent, harmonic_distortion_thd,
            symmetry_imbalance_percent, partial_discharge_detected
        )

        # Step 6: Calculate derived system parameters for power flow
        rated_current_a = electrical_params['rated_current_a']
        actual_current_a = rated_current_a * (load_percent / 100.0)
        voltage_kv = self.voltage_rating_kv  # Simplified - could include regulation
        apparent_power_mva = self.rating_mva * (load_percent / 100.0)
        power_factor = 0.95  # Assumed lagging - could be made dynamic
        power_factor_angle = math.acos(power_factor)
        real_power_mw = apparent_power_mva * power_factor
        reactive_power_mvar = apparent_power_mva * math.sin(power_factor_angle)

        # Step 7: Calculate efficiency with all loss components
        total_losses_kw = losses['total_losses']
        output_power_mw = real_power_mw
        input_power_mw = output_power_mw + (total_losses_kw / 1000.0)
        efficiency_percent = (output_power_mw / input_power_mw) * 100 if input_power_mw > 0 else 0

        # Step 8: Calculate voltage regulation
        percent_r = (electrical_params['resistance_ohm'] / self.base_impedance_ohm) * 100.0
        percent_x = (self.reactance_ohm / self.base_impedance_ohm) * 100.0
        voltage_regulation_percent = percent_r * power_factor + percent_x * math.sin(power_factor_angle)

        # Step 9: Compile comprehensive results
        result = {
            # === INPUT PARAMETERS ===
            'load_percent': load_percent,
            'ambient_temp_c': ambient_temp_c,
            'cooling_mode': cooling_mode,
            'harmonic_distortion_thd': harmonic_distortion_thd,
            'simulation_hours': hours_at_conditions,
            'vibration_rms_mm_s': vibration_rms_mm_s,
            'dielectric_stress_factor': dielectric_stress_factor,
            'symmetry_imbalance_percent': symmetry_imbalance_percent,
            'partial_discharge_detected': partial_discharge_detected,

            # === ELECTRICAL PARAMETERS ===
            'rated_current_a': round(rated_current_a, 1),
            'actual_current_a': round(actual_current_a, 1),
            'rated_voltage_kv': round(self.voltage_rating_kv, 1),
            'actual_voltage_kv': round(voltage_kv, 1),
            'apparent_power_mva': round(apparent_power_mva, 2),
            'real_power_mw': round(real_power_mw, 2),
            'reactive_power_mvar': round(reactive_power_mvar, 2),
            'power_factor': round(power_factor, 3),
            'resistance_ohm': round(electrical_params['resistance_ohm'], 4),
            'reactance_ohm': round(electrical_params['reactance_ohm'], 4),
            'impedance_ohm': round(electrical_params['impedance_ohm'], 4),
            'impedance_percent': round(electrical_params['impedance_percent'], 2),
            'voltage_regulation_percent': round(voltage_regulation_percent, 2),

            # === LOSSES BREAKDOWN ===
            'no_load_losses_kw': round(losses['total_no_load_losses'], 3),
            'load_losses_kw': round(losses['total_load_losses'], 3),
            'total_losses_kw': round(losses['total_losses'], 3),
            'losses_breakdown': {
                'no_load': {
                    'hysteresis_kw': round(losses['no_load_losses']['hysteresis'], 3),
                    'eddy_current_kw': round(losses['no_load_losses']['eddy_current'], 3),
                    'stray_kw': round(losses['no_load_losses']['stray'], 3)
                },
                'load': {
                    'i2r_dc_kw': round(losses['load_losses']['i2r_dc'], 3),
                    'eddy_winding_kw': round(losses['load_losses']['eddy_winding'], 3),
                    'stray_load_kw': round(losses['load_losses']['stray_load'], 3)
                }
            },
            'harmonic_loss_factors': {
                'no_load': round(losses['harmonic_loss_factor_no_load'], 3),
                'load': round(losses['harmonic_factor_load'], 3)
            },

            # === TEMPERATURES (°C) ===
            'oil_temp_c': round(temperatures['oil_temp_c'], 1),
            'winding_temp_c': round(temperatures['winding_temp_c'], 1),
            'hotspot_temp_c': round(temperatures['hotspot_temp_c'], 1),
            'temperature_rise_oil_c': round(temperatures['delta_t_oil'], 1),
            'temperature_rise_winding_c': round(temperatures['delta_t_winding'], 1),
            'temperature_rise_hotspot_c': round(temperatures['delta_t_hotspot'], 1),
            'hotspot_gradient_c': round(aging_health['hotspot_gradient_c'], 1),
            'oil_winding_gradient_c': round(aging_health['oil_to_winding_gradient_c'], 1),

            # === THERMAL TIME CONSTANTS ===
            'thermal_time_constants_hours': temperatures['thermal_time_constants'],

            # === EFFICIENCY AND LOSSES ===
            'efficiency_percent': round(efficiency_percent, 2),
            'losses_percent': round((total_losses_kw / (self.rating_mva * 1000)) * 100, 2),

            # === AGING AND HEALTH ===
            'health_impact_per_hour': round(aging_health['health_impact_per_hour'], 4),
            'estimated_remaining_hours': round(aging_health['estimated_remaining_hours'], 0),
            'aging_rate_per_hour': round(aging_health['aging_rate_per_hour'], 6),
            'design_life_hours': aging_health['design_life_hours'],
            'combined_aging_factor': round(aging_health['combined_aging_factor'], 3),
            'aging_breakdown': {
                'thermal_aging': round(aging_health['thermal_aging_factor'], 3),
                'harmonic_aging': round(aging_health['harmonic_aging_factor'], 3),
                'vibration_aging': round(aging_health['vibration_aging_factor'], 3),
                'dielectric_aging': round(aging_health['dielectric_aging_factor'], 3),
                'mechanical_stress': round(aging_health['mechanical_stress_aging'], 3)
            },

            # === RISK ASSESSMENT ===
            'risk_level': risk_assessment['overall_risk_level'],
            'risk_level_numeric': risk_assessment['risk_level_numeric'],
            'risk_confidence': round(risk_assessment['confidence_score'], 3),
            'risk_scores': {k: round(v, 1) for k, v in risk_assessment['risk_scores'].items()},
            'max_individual_risk': round(risk_assessment['max_individual_risk'], 1),
            'significant_risk_factors': risk_assessment['contributing_factors'],

            # === DIELECTRIC AND INSULATION ===
            'bil_level_kv': round(self.bil_level_kv, 1),
            'dielectric_stress_actual': round(dielectric_stress_factor, 2),
            'partial_discharge_risk': 'DETECTED' if partial_discharge_detected else 'NONE',

            # === SYSTEM PARAMETERS ===
            'frequency_hz': self.frequency_hz,
            'rated_mva': self.rating_mva,
            'voltage_rating_kv': self.voltage_rating_kv,
            'temp_rise_limit_c': self.temp_rise_limit_c,
            'impedance_percent': self.impedance_percent,
            'x_over_r_ratio': self.x_over_r_ratio,

            # === TIMESTAMP ===
            'timestamp': pd.Timestamp.now().isoformat(),
            'simulation_id': f"enhanced_tx_{int(pd.Timestamp.now().timestamp())}"
        }

        self.logger.debug(f"Enhanced transformer simulation completed: {len(result)} parameters")
        return result


# Factory function for easy instantiation
def create_enhanced_transformer_simulator(rating_mva: float = 10.0,
                                        voltage_rating_kv: float = 23.0,
                                        temp_rise_limit_c: float = 65.0,
                                        frequency_hz: float = 60.0,
                                        impedance_percent: float = 8.0,
                                        x_over_r_ratio: float = 20.0) -> EnhancedTransformerSimulator:
    """
    Create and return an enhanced transformer simulator instance

    Args:
        rating_mva: Transformer rating in MVA
        voltage_rating_kv: Voltage rating in kV
        temp_rise_limit_c: Temperature rise limit in °C
        frequency_hz: System frequency in Hz
        impedance_percent: Percent impedance (%Z)
        x_over_r_ratio: Reactance to resistance ratio (X/R)

    Returns:
        EnhancedTransformerSimulator instance
    """
    return EnhancedTransformerSimulator(
        rating_mva, voltage_rating_kv, temp_rise_limit_c,
        frequency_hz, impedance_percent, x_over_r_ratio
    )


# Example usage and testing
if __name__ == "__main__":
    print("Enhanced Transformer Digital Twin - Comprehensive Analysis")
    print("=" * 70)

    # Create simulator for a 15 MVA, 34.5 kV power transformer
    simulator = create_enhanced_transformer_simulator(
        rating_mva=15.0,
        voltage_rating_kv=34.5,
        temp_rise_limit_c=65.0,
        frequency_hz=60.0,
        impedance_percent=7.5,  # Slightly lower impedance for larger transformer
        x_over_r_ratio=25.0     # Higher X/R ratio typical for larger units
    )

    # Test cases representing challenging operating conditions
    test_scenarios = [
        {
            'name': 'Normal Operation',
            'load_percent': 75,
            'ambient_temp_c': 25,
            'cooling_mode': 'normal',
            'harmonic_thd': 0.03,   # 3% THD
            'hours': 1.0,
            'vibration': 1.5,       # Low vibration
            'imbalance': 2.0,       # 2% imbalance
            'partial_discharge': False
        },
        {
            'name': 'Peak Load Summer Day',
            'load_percent': 95,
            'ambient_temp_c': 38,
            'cooling_mode': 'normal',
            'harmonic_thd': 0.08,   # 8% THD from AC loads
            'hours': 4.0,
            'vibration': 2.0,
            'imbalance': 3.0,
            'partial_discharge': False
        },
        {
            'name': 'Harmonic Rich Environment',
            'load_percent': 80,
            'ambient_temp_c': 30,
            'cooling_mode': 'normal',
            'harmonic_thd': 0.15,   # 15% THD (VFDs, rectifiers)
            'hours': 2.0,
            'vibration': 2.5,
            'imbalance': 4.0,
            'partial_discharge': False
        },
        {
            'name': 'Overload with Forced Cooling',
            'load_percent': 110,
            'ambient_temp_c': 32,
            'cooling_mode': 'forced',
            'harmonic_thd': 0.05,
            'hours': 1.0,
            'vibration': 3.0,
            'imbalance': 2.0,
            'partial_discharge': False
        },
        {
            'name': 'Aged Transformer with PD',
            'load_percent': 60,
            'ambient_temp_c': 28,
            'cooling_mode': 'normal',
            'harmonic_thd': 0.04,
            'hours': 8.0,           # Extended operation
            'vibration': 2.2,
            'imbalance': 1.5,
            'partial_discharge': True  # Indicates dielectric deterioration
        }
    ]

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['name']}:")
        print("-" * 50)

        result = simulator.simulate_enhanced(**scenario)

        # Key electrical parameters
        print(f"⚡ ELECTRICAL:")
        print(f"   Load: {result['load_percent']}% ({result['real_power_mw']} MW)")
        print(f"   Current: {result['actual_current_a']} A (rated: {result['rated_current_a']} A)")
        print(f"   Voltage: {result['actual_voltage_kv']} kV")
        print(f"   Power Factor: {result['power_factor']} (lagging)")
        print(f"   Impedance: {result['impedance_percent']}% (X/R ≈ {result['x_over_r_ratio']})")
        print(f"   Efficiency: {result['efficiency_percent']}%")

        # Losses breakdown
        print(f"🔥 LOSSES:")
        print(f"   No-load: {result['losses_breakdown']['no_load']['hysteresis_kw']:.2f} kW (hysteresis) + "
              f"{result['losses_breakdown']['no_load']['eddy_current_kw']:.2f} kW (eddy)")
        print(f"   Load: {result['losses_breakdown']['load']['i2r_dc_kw']:.2f} kW (I²R) + "
              f"{result['losses_breakdown']['load']['eddy_winding_kw']:.2f} kW (eddy)")
        print(f"   Total: {result['total_losses_kw']} kW ({result['losses_percent']}% of rating)")

        # Temperatures
        print(f"🌡️  TEMPERATURES:")
        print(f"   Ambient: {result['ambient_temp_c']}°C")
        print(f"   Oil: {result['oil_temp_c']}°C (rise: {result['temperature_rise_oil_c']}°C)")
        print(f"   Winding: {result['winding_temp_c']}°C (rise: {result['temperature_rise_winding_c']}°C)")
        print(f"   Hot Spot: {result['hotspot_temp_c']}°C (gradient: +{result['hotspot_gradient_c']}°C over winding)")
        print(f"   Oil-Winding Gradient: {result['oil_winding_gradient_c']}°C")

        # Aging and health
        print(f"⏳ AGING & HEALTH:")
        print(f"   Health Impact/hr: {result['health_impact_per_hour']*100:.3f}%")
        print(f"   Combined Aging Factor: {result['combined_aging_factor']:.2f}x")
        print(f"   Est. Remaining Life: {result['estimated_remaining_hours']:,} hours "
              f"({result['estimated_remaining_hours']/8760:.1f} years)")
        print(f"   Aging Breakdown: Thermal({result['aging_breakdown']['thermal_aging']:.2f}x) "
              f"+ Harmonic({result['aging_breakdown']['harmonic_aging']:.2f}x) "
              f"+ Vibration({result['aging_breakdown']['vibration_aging']:.2f}x) "
              f"+ Dielectric({result['aging_breakdown']['dielectric_aging']:.2f}x)")

        # Risk assessment
        print(f"⚠️  RISK ASSESSMENT:")
        print(f"   Overall Risk: {result['risk_level']} "
              f"(Confidence: {result['risk_confidence']*100:.0f}%)")
        significant_factors = result['significant_risk_factors']
        if significant_factors:
            factor_names = {
                'thermal_winding': 'Winding Temp',
                'thermal_hotspot': 'Hot Spot Temp',
                'insulation_aging': 'Insulation Aging',
                'overload': 'Overload',
                'harmonics': 'Harmonics',
                'dielectric_stress': 'Dielectric Stress',
                'partial_discharge': 'Partial Discharge'
            }
            active_factors = [factor_names.get(k, k) for k, v in significant_factors.items() if v >= 2.5]
            if active_factors:
                print(f"   Active Factors: {', '.join(active_factors[:3])}")  # Show top 3

        # Power quality
        if result['harmonic_distortion_thd'] > 0.05:
            print(f"📊 POWER QUALITY:")
            print(f"   THD: {result['harmonic_distortion_thd']*100:.1f}% "
                  f"(No-load LF: {result['harmonic_loss_factors']['no_load']:.2f}x, "
                  f"Load LF: {result['harmonic_loss_factors']['load']:.2f}x)")

        print(f"⚙️  SYSTEM:")
        print(f"   Cooling: {result['cooling_mode']}")
        print(f"   Vibration: {result['vibration_rms_mm_s']} mm/s RMS")
        print(f"   Phase Imbalance: {result['symmetry_imbalance_percent']}%")
        print(f"   BIL: {result['bil_level_kv']} kV")
        print(f"   Time Constants: Oil={result['thermal_time_constants_hours']['oil_hours']:.1f}h, "
              f"Winding={result['thermal_time_constants_hours']['winding_hours']:.1f}h")

    print("\n" + "=" * 70)
    print("Enhanced Transformer Digital Twin - Ready for Grid Integration Studies")
    print("Features: Harmonics, Thermal Networks, Aging Mechanics, Risk Assessment")