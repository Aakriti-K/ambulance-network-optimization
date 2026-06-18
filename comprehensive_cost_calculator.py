"""
Comprehensive Marginal Cost Calculator with Regional Variations
Supports 70+ parameterized cost variables across all 7 cost factors
Allows borough-specific cost variations for NYC ambulance network
"""

from typing import Dict, List
import json


class ComprehensiveMarginalCostCalculator:
    """
    Enhanced calculator supporting all cost factors with regional variations:
    - Factor 1: Staffing (7 roles + onboarding)
    - Factor 2: Vehicles (ALS, BLS, PTV components + fuel + maintenance)
    - Factor 3: Medical Equipment (per vehicle type + annual supplies)
    - Factor 4: Station Setup (per station, scalable with region)
    - Factor 5: Dispatch & Connectivity (network infrastructure)
    - Factor 6: Architecture & System (cloud, security, integration)
    - Factor 7: Compliance (insurance, licensing, training)
    """
    
    def __init__(self, borough_config: Dict[str, Dict]):
        """
        Initialize calculator with borough-specific cost parameters
        
        Args:
            borough_config: Dictionary with borough names and their cost parameters
            Example:
            {
                'Manhattan': {
                    'X1_emt_basic_annual': 55000,
                    'X2_paramedic_annual': 82000,
                    'X23_station_rent_per_sqft': 250,
                    ...
                },
                'Brooklyn': {
                    'X1_emt_basic_annual': 52000,
                    ...
                }
            }
        """
        self.borough_config = borough_config
        self.boroughs = list(borough_config.keys())
    
    def get_borough_cost(self, borough: str, variable: str, default: float = 0) -> float:
        """
        Get cost parameter for a specific borough
        
        Args:
            borough: Borough name
            variable: Variable name (e.g., 'X1_emt_basic_annual')
            default: Default value if not found
        
        Returns:
            Cost value for that borough
        """
        if borough not in self.borough_config:
            raise ValueError(f"Borough '{borough}' not found. Available: {self.boroughs}")
        
        return self.borough_config[borough].get(variable, default)
    
    # ==================== FACTOR 1: STAFFING COSTS ====================
    
    def calculate_staffing_cost_per_vehicle(self, 
                                           borough: str,
                                           vehicle_type: str) -> Dict[str, float]:
        """
        Calculate total annual staffing cost allocated per vehicle
        
        Args:
            borough: Borough name
            vehicle_type: 'ALS', 'BLS', or 'PTV'
        
        Returns:
            Dictionary with staffing breakdown
        """
        staffing_breakdown = {
            'ALS': {  # 2 paramedics per ALS
                'primary_personnel': 'X2_paramedic_annual',
                'crew_size': 2,
                'secondary_cost_split': ['X7_supervisor_annual', 'X5_dispatch_annual']
            },
            'BLS': {  # 2 EMTs per BLS
                'primary_personnel': 'X1_emt_basic_annual',
                'crew_size': 2,
                'secondary_cost_split': ['X7_supervisor_annual', 'X5_dispatch_annual']
            },
            'PTV': {  # 1 driver per PTV
                'primary_personnel': 'X4_driver_annual',
                'crew_size': 1,
                'secondary_cost_split': ['X5_dispatch_annual']
            }
        }
        
        if vehicle_type not in staffing_breakdown:
            raise ValueError(f"Vehicle type '{vehicle_type}' not supported")
        
        config = staffing_breakdown[vehicle_type]
        primary_salary = self.get_borough_cost(borough, config['primary_personnel'], 0)
        primary_cost = primary_salary * config['crew_size']
        
        # Allocate secondary costs (supervisor, dispatch) proportionally
        secondary_cost = 0
        for secondary_var in config['secondary_cost_split']:
            secondary_cost += self.get_borough_cost(borough, secondary_var, 0)
        
        # Proportional allocation (simplified: ALS gets more, PTV gets less)
        allocation_factor = {
            'ALS': 0.4,   # ALS: 40% of shared supervisory/dispatch
            'BLS': 0.35,  # BLS: 35% of shared
            'PTV': 0.25   # PTV: 25% of shared
        }
        secondary_allocation = secondary_cost * allocation_factor.get(vehicle_type, 0.33)
        
        total_staffing_cost = primary_cost + secondary_allocation
        
        return {
            'primary_personnel_cost': primary_cost,
            'secondary_allocation': secondary_allocation,
            'total_annual_staffing': total_staffing_cost,
            'vehicle_type': vehicle_type,
            'borough': borough
        }
    
    # ==================== FACTOR 2: VEHICLE COSTS ====================
    
    def calculate_vehicle_capital_cost(self,
                                      borough: str,
                                      vehicle_type: str) -> Dict[str, float]:
        """
        Calculate one-time capital cost per vehicle (all components)
        
        Args:
            borough: Borough name
            vehicle_type: 'ALS', 'BLS', or 'PTV'
        
        Returns:
            Dictionary with capital cost breakdown
        """
        # Vehicle components
        components_map = {
            'ALS': {
                'X32_als_base_vehicle': 'Base Vehicle',
                'X33_als_conversion_upfit': 'Conversion/Upfit',
                'X34_als_sirens_lights': 'Sirens & Lights',
                'X35_als_mounts_cabinetry': 'Mounts & Cabinetry',
                'X36_als_safety_certification': 'Safety Certification'
            },
            'BLS': {
                'X37_bls_base_vehicle': 'Base Vehicle',
                'X38_bls_conversion_upfit': 'Conversion/Upfit',
                'X39_bls_sirens_lights': 'Sirens & Lights',
                'X40_bls_mounts_cabinetry': 'Mounts & Cabinetry',
                'X41_bls_safety_certification': 'Safety Certification'
            },
            'PTV': {
                'X42_ptv_base_vehicle': 'Base Vehicle',
                'X43_ptv_conversion_upfit': 'Conversion/Upfit',
                'X44_ptv_sirens_lights': 'Sirens & Lights',
                'X45_ptv_mounts_cabinetry': 'Mounts & Cabinetry',
                'X46_ptv_safety_certification': 'Safety Certification'
            }
        }
        
        if vehicle_type not in components_map:
            raise ValueError(f"Vehicle type '{vehicle_type}' not supported")
        
        components = components_map[vehicle_type]
        total_capital = 0
        breakdown = {}
        
        for var_name, component_name in components.items():
            cost = self.get_borough_cost(borough, var_name, 0)
            breakdown[component_name] = cost
            total_capital += cost
        
        return {
            'breakdown': breakdown,
            'total_capital': total_capital,
            'vehicle_type': vehicle_type,
            'borough': borough
        }
    
    def calculate_vehicle_annual_operating_cost(self,
                                               borough: str,
                                               vehicle_type: str,
                                               avg_annual_miles: float) -> Dict[str, float]:
        """
        Calculate annual vehicle operating cost (fuel + maintenance)
        
        Args:
            borough: Borough name
            vehicle_type: 'ALS', 'BLS', or 'PTV'
            avg_annual_miles: Expected annual miles
        
        Returns:
            Dictionary with operating cost breakdown
        """
        fuel_map = {
            'ALS': 'X47_als_fuel_annual',
            'BLS': 'X48_bls_fuel_annual',
            'PTV': 'X49_ptv_fuel_annual'
        }
        
        maintenance_map = {
            'ALS': 'X50_als_maintenance_annual',
            'BLS': 'X51_bls_maintenance_annual',
            'PTV': 'X52_ptv_maintenance_annual'
        }
        
        fuel_cost = self.get_borough_cost(borough, fuel_map[vehicle_type], 0)
        maintenance_cost = self.get_borough_cost(borough, maintenance_map[vehicle_type], 0)
        
        total_operating = fuel_cost + maintenance_cost
        
        return {
            'fuel_cost': fuel_cost,
            'maintenance_cost': maintenance_cost,
            'total_annual': total_operating,
            'vehicle_type': vehicle_type,
            'borough': borough
        }
    
    # ==================== FACTOR 3: MEDICAL EQUIPMENT ====================
    
    def calculate_medical_equipment_cost(self,
                                        borough: str,
                                        vehicle_type: str) -> Dict[str, float]:
        """
        Calculate one-time medical equipment cost per vehicle
        
        Args:
            borough: Borough name
            vehicle_type: 'ALS', 'BLS', or 'PTV'
        
        Returns:
            Dictionary with equipment cost breakdown
        """
        equipment_map = {
            'ALS': {
                'X53_als_oxygen_system': 'Oxygen System',
                'X54_als_suction_unit': 'Suction Unit',
                'X55_als_stretcher': 'Stretcher',
                'X56_als_aed': 'AED',
                'X57_als_basic_supplies': 'Basic Supplies',
                'X58_als_monitor_defibrillator': 'Monitor/Defibrillator',
                'X59_als_capnography': 'Capnography Monitor',
                'X60_als_airway_kit': 'Airway Kit',
                'X61_als_iv_access_drugs': 'IV/IO Access & Drugs'
            },
            'BLS': {
                'X62_bls_oxygen_system': 'Oxygen System',
                'X63_bls_suction_unit': 'Suction Unit',
                'X64_bls_stretcher': 'Stretcher',
                'X65_bls_aed': 'AED',
                'X66_bls_basic_supplies': 'Basic Supplies'
            },
            'PTV': {
                'X67_ptv_stretcher': 'Stretcher',
                'X68_ptv_wheelchair_ramp': 'Wheelchair Ramp',
                'X69_ptv_wheelchair_securement': 'Wheelchair Securement',
                'X70_ptv_gps_signage': 'GPS & Signage',
                'X71_ptv_first_aid_kit': 'First Aid Kit'
            }
        }
        
        equipment = equipment_map[vehicle_type]
        total_equipment = 0
        breakdown = {}
        
        for var_name, component_name in equipment.items():
            cost = self.get_borough_cost(borough, var_name, 0)
            breakdown[component_name] = cost
            total_equipment += cost
        
        return {
            'breakdown': breakdown,
            'total_capital': total_equipment,
            'vehicle_type': vehicle_type,
            'borough': borough
        }
    
    def calculate_medical_supplies_annual(self,
                                         borough: str,
                                         vehicle_type: str) -> float:
        """
        Calculate annual medical supply replenishment cost
        
        Args:
            borough: Borough name
            vehicle_type: 'ALS', 'BLS', or 'PTV'
        
        Returns:
            Annual supply cost
        """
        supply_map = {
            'ALS': 'X72_als_supply_replenishment_annual',
            'BLS': 'X73_bls_supply_replenishment_annual',
            'PTV': 'X74_ptv_supply_replenishment_annual'
        }
        
        return self.get_borough_cost(borough, supply_map[vehicle_type], 0)
    
    # ==================== FACTOR 4: STATION SETUP ====================
    
    def calculate_station_setup_cost_one_time(self,
                                             borough: str) -> Dict[str, float]:
        """
        Calculate one-time station setup costs
        
        Args:
            borough: Borough name
        
        Returns:
            Dictionary with setup costs
        """
        one_time_components = {
            'X75_security_deposit': 'Security Deposit',
            'X76_generator_setup': 'Generator Setup',
            'X77_office_furniture': 'Office Furniture',
            'X78_crew_facilities': 'Crew Facilities',
            'X79_maintenance_bay': 'Maintenance Bay',
            'X80_security_system': 'Security System'
        }
        
        total_setup = 0
        breakdown = {}
        
        for var_name, component_name in one_time_components.items():
            cost = self.get_borough_cost(borough, var_name, 0)
            breakdown[component_name] = cost
            total_setup += cost
        
        return {
            'breakdown': breakdown,
            'total_one_time': total_setup,
            'borough': borough
        }
    
    def calculate_station_annual_cost(self,
                                     borough: str) -> Dict[str, float]:
        """
        Calculate annual station operating costs (per station)
        
        Args:
            borough: Borough name
        
        Returns:
            Dictionary with annual costs
        """
        annual_components = {
            'X81_rent_annual': 'Rent',
            'X82_utilities_annual': 'Utilities',
            'X83_parking_annual': 'Parking/Bay Rental',
            'X84_generator_annual': 'Generator Maintenance',
            'X85_internet_telecom_annual': 'Internet & Telecom',
            'X86_janitorial_annual': 'Janitorial Services'
        }
        
        total_annual = 0
        breakdown = {}
        
        for var_name, component_name in annual_components.items():
            cost = self.get_borough_cost(borough, var_name, 0)
            breakdown[component_name] = cost
            total_annual += cost
        
        return {
            'breakdown': breakdown,
            'total_annual': total_annual,
            'borough': borough
        }
    
    # ==================== FACTORS 5-7: SHARED INFRASTRUCTURE ====================
    
    def calculate_dispatch_connectivity_cost(self,
                                            borough: str,
                                            current_total_fleet_units: int = 1) -> Dict[str, float]:
        """
        Calculate dispatch & connectivity costs (allocated per vehicle)
        
        Args:
            borough: Borough name
            current_total_fleet_units: Total vehicles to allocate costs across
        
        Returns:
            Dictionary with allocated dispatch costs
        """
        dispatch_components = {
            'X87_tollfree_number_onetime': 'Toll-free Setup',
            'X88_tollfree_number_annual': 'Toll-free Annual',
            'X89_sip_trunking_onetime': 'SIP Trunking Setup',
            'X90_sip_trunking_annual': 'SIP Trunking Annual',
            'X91_cad_software_onetime': 'CAD Software Setup',
            'X92_cad_software_annual': 'CAD Software Annual',
            'X93_gis_routing_onetime': 'GIS Routing Setup',
            'X94_gis_routing_annual': 'GIS Routing Annual',
            'X95_emd_protocol_onetime': 'EMD Protocol Setup',
            'X96_emd_protocol_annual': 'EMD Protocol Annual',
            'X97_call_recording_onetime': 'Call Recording Setup',
            'X98_call_recording_annual': 'Call Recording Annual',
            'X99_radio_network_onetime': 'Radio Network Setup',
            'X100_radio_network_annual': 'Radio Network Annual',
            'X101_mdt_hardware_onetime': 'MDT Hardware',
            'X102_mdt_hardware_annual': 'MDT Maintenance',
            'X103_gps_avl_onetime': 'GPS/AVL Setup',
            'X104_gps_avl_annual': 'GPS/AVL Annual',
            'X105_integration_middleware_onetime': 'Integration Middleware Setup',
            'X106_integration_middleware_annual': 'Integration Middleware Annual',
            'X107_dispatch_workstations_onetime': 'Dispatch Workstations',
            'X108_cellular_data_annual': 'Cellular Data Plans'
        }
        
        total_onetime = 0
        total_annual = 0
        breakdown = {}
        
        for var_name, component_name in dispatch_components.items():
            cost = self.get_borough_cost(borough, var_name, 0)
            if 'onetime' in var_name:
                total_onetime += cost
            else:
                total_annual += cost
            breakdown[component_name] = cost
        
        # Allocate per vehicle
        onetime_per_vehicle = total_onetime / max(current_total_fleet_units, 1)
        annual_per_vehicle = total_annual / max(current_total_fleet_units, 1)
        
        return {
            'breakdown': breakdown,
            'total_onetime': total_onetime,
            'total_annual': total_annual,
            'per_vehicle_onetime': onetime_per_vehicle,
            'per_vehicle_annual': annual_per_vehicle,
            'borough': borough
        }
    
    def calculate_architecture_cost(self,
                                   borough: str,
                                   current_total_fleet_units: int = 1) -> Dict[str, float]:
        """
        Calculate system architecture costs (allocated per vehicle)
        
        Args:
            borough: Borough name
            current_total_fleet_units: Total vehicles to allocate costs across
        
        Returns:
            Dictionary with allocated architecture costs
        """
        arch_components = {
            'X109_architecture_design_onetime': 'Architecture Design',
            'X110_network_infrastructure_onetime': 'Network Infrastructure Setup',
            'X111_network_infrastructure_annual': 'Network Infrastructure Annual',
            'X112_cloud_hosting_onetime': 'Cloud Setup',
            'X113_cloud_hosting_annual': 'Cloud Hosting Annual',
            'X114_system_integration_onetime': 'System Integration',
            'X115_cybersecurity_onetime': 'Cybersecurity Setup',
            'X116_cybersecurity_annual': 'Cybersecurity Annual',
            'X117_disaster_recovery_onetime': 'Disaster Recovery Setup',
            'X118_disaster_recovery_annual': 'Disaster Recovery Annual',
            'X119_uat_testing_onetime': 'UAT & Testing',
            'X120_it_training_onetime': 'IT Training'
        }
        
        total_onetime = 0
        total_annual = 0
        breakdown = {}
        
        for var_name, component_name in arch_components.items():
            cost = self.get_borough_cost(borough, var_name, 0)
            if 'onetime' in var_name:
                total_onetime += cost
            else:
                total_annual += cost
            breakdown[component_name] = cost
        
        # Allocate per vehicle
        onetime_per_vehicle = total_onetime / max(current_total_fleet_units, 1)
        annual_per_vehicle = total_annual / max(current_total_fleet_units, 1)
        
        return {
            'breakdown': breakdown,
            'total_onetime': total_onetime,
            'total_annual': total_annual,
            'per_vehicle_onetime': onetime_per_vehicle,
            'per_vehicle_annual': annual_per_vehicle,
            'borough': borough
        }
    
    def calculate_compliance_costs(self,
                                  borough: str,
                                  vehicle_count: int = 1,
                                  staff_count: int = 40) -> Dict[str, float]:
        """
        Calculate compliance costs
        
        Args:
            borough: Borough name
            vehicle_count: Number of vehicles
            staff_count: Total staff count for scaling costs
        
        Returns:
            Dictionary with compliance costs
        """
        compliance_map = {
            'X121_ems_licensing_onetime': 'EMS Licensing Setup',
            'X122_ems_licensing_annual': 'EMS Licensing Annual',
            'X123_vehicle_registration_onetime': 'Vehicle Registration Setup',
            'X124_vehicle_registration_annual': 'Vehicle Registration Annual',
            'X125_liability_insurance_annual': 'General Liability Insurance',
            'X126_vehicle_insurance_annual': 'Vehicle Insurance',
            'X127_malpractice_insurance_annual': 'Malpractice Insurance',
            'X128_qa_program_onetime': 'QA Program Setup',
            'X129_qa_program_annual': 'QA Program Annual',
            'X130_recertification_annual': 'Recertification',
            'X131_ppe_stock_onetime': 'PPE Stock',
            'X132_ppe_stock_annual': 'PPE Annual',
            'X133_background_checks_onetime': 'Background Checks Setup',
            'X134_background_checks_annual': 'Background Checks Annual',
            'X135_hr_admin_onetime': 'HR/Admin Setup',
            'X136_hr_admin_annual': 'HR/Admin Annual',
            'X137_hipaa_audit_onetime': 'HIPAA Audit',
            'X138_hipaa_audit_annual': 'HIPAA Audit Annual',
            'X139_reserve_downtime_annual': 'Reserve Downtime Allowance'
        }
        
        total_onetime = 0
        total_annual = 0
        breakdown = {}
        
        for var_name, component_name in compliance_map.items():
            cost = self.get_borough_cost(borough, var_name, 0)
            if 'onetime' in var_name:
                total_onetime += cost
            else:
                total_annual += cost
            breakdown[component_name] = cost
        
        return {
            'breakdown': breakdown,
            'total_one_time': total_onetime,
            'total_annual': total_annual,
            'borough': borough
        }
    
    # ==================== COMPREHENSIVE MARGINAL COST ====================
    
    def total_marginal_cost_annual(self,
                                   borough: str,
                                   vehicle_type: str,
                                   avg_annual_miles: float,
                                   current_total_fleet_units: int,
                                   amortization_years: int = 5,
                                   num_stations: int = 1) -> Dict:
        """
        Calculate total annual marginal cost of adding ONE vehicle
        
        Args:
            borough: Borough name
            vehicle_type: 'ALS', 'BLS', or 'PTV'
            avg_annual_miles: Expected annual miles
            current_total_fleet_units: Current total fleet size
            amortization_years: Years to amortize capital (default 5)
            num_stations: Stations this vehicle will use (usually 1)
        
        Returns:
            Comprehensive cost breakdown
        """
        # Calculate all components
        staffing = self.calculate_staffing_cost_per_vehicle(borough, vehicle_type)
        vehicle_capital = self.calculate_vehicle_capital_cost(borough, vehicle_type)
        vehicle_operating = self.calculate_vehicle_annual_operating_cost(borough, vehicle_type, avg_annual_miles)
        medical_equipment = self.calculate_medical_equipment_cost(borough, vehicle_type)
        medical_supplies = self.calculate_medical_supplies_annual(borough, vehicle_type)
        
        station_setup = self.calculate_station_setup_cost_one_time(borough)
        station_annual = self.calculate_station_annual_cost(borough)
        
        dispatch = self.calculate_dispatch_connectivity_cost(borough, current_total_fleet_units)
        architecture = self.calculate_architecture_cost(borough, current_total_fleet_units)
        compliance = self.calculate_compliance_costs(borough, vehicle_count=1)
        
        # Aggregate costs
        total_capital = (
            vehicle_capital['total_capital'] +
            medical_equipment['total_capital'] +
            station_setup['total_one_time'] / num_stations +
            dispatch['per_vehicle_onetime'] +
            architecture['per_vehicle_onetime'] +
            compliance['total_one_time']
        )
        
        total_annual = (
            staffing['total_annual_staffing'] +
            vehicle_operating['total_annual'] +
            medical_supplies +
            station_annual['total_annual'] / num_stations +
            dispatch['per_vehicle_annual'] +
            architecture['per_vehicle_annual'] +
            compliance['total_annual']
        )
        
        amortized_capital = total_capital / amortization_years
        total_annual_cost = amortized_capital + total_annual
        
        return {
            'vehicle_type': vehicle_type,
            'borough': borough,
            'capital_costs': {
                'vehicle_hardware': vehicle_capital['total_capital'],
                'medical_equipment': medical_equipment['total_capital'],
                'station_setup_allocated': station_setup['total_one_time'] / num_stations,
                'dispatch_connectivity': dispatch['per_vehicle_onetime'],
                'architecture_system': architecture['per_vehicle_onetime'],
                'compliance': compliance['total_one_time'],
                'total_capital': total_capital
            },
            'annual_costs': {
                'staffing': staffing['total_annual_staffing'],
                'vehicle_operating': vehicle_operating['total_annual'],
                'medical_supplies': medical_supplies,
                'station_facility': station_annual['total_annual'] / num_stations,
                'dispatch_connectivity': dispatch['per_vehicle_annual'],
                'architecture_system': architecture['per_vehicle_annual'],
                'compliance': compliance['total_annual'],
                'total_annual': total_annual
            },
            'amortization': {
                'years': amortization_years,
                'capital_amortized': amortized_capital
            },
            'total_annual_cost': total_annual_cost,
            'avg_annual_miles': avg_annual_miles,
            'current_fleet_size': current_total_fleet_units
        }
    
    def compare_vehicles_by_borough(self,
                                    borough: str,
                                    avg_annual_miles: float,
                                    current_total_fleet_units: int) -> Dict:
        """
        Compare marginal costs for ALS vs BLS vs PTV in a specific borough
        
        Args:
            borough: Borough name
            avg_annual_miles: Expected annual miles
            current_total_fleet_units: Current total fleet
        
        Returns:
            Comparison of costs across vehicle types
        """
        comparison = {}
        for vehicle_type in ['ALS', 'BLS', 'PTV']:
            comparison[vehicle_type] = self.total_marginal_cost_annual(
                borough, vehicle_type, avg_annual_miles, current_total_fleet_units
            )
        
        return comparison
    
    def compare_boroughs_by_vehicle(self,
                                   vehicle_type: str,
                                   avg_annual_miles: float,
                                   current_total_fleet_units: int) -> Dict:
        """
        Compare marginal costs across boroughs for a specific vehicle type
        
        Args:
            vehicle_type: 'ALS', 'BLS', or 'PTV'
            avg_annual_miles: Expected annual miles
            current_total_fleet_units: Current total fleet
        
        Returns:
            Comparison of costs across boroughs
        """
        comparison = {}
        for borough in self.boroughs:
            comparison[borough] = self.total_marginal_cost_annual(
                borough, vehicle_type, avg_annual_miles, current_total_fleet_units
            )
        
        return comparison
    
    def print_marginal_cost_summary(self, cost_analysis: Dict):
        """Print formatted cost summary"""
        print(f"\n{'='*80}")
        print(f"MARGINAL COST ANALYSIS: {cost_analysis['vehicle_type']} in {cost_analysis['borough']}")
        print(f"{'='*80}")
        
        print(f"\n[CAPITAL COSTS - One-time]")
        cap = cost_analysis['capital_costs']
        for component, cost in cap.items():
            if component != 'total_capital':
                print(f"  {component.replace('_', ' ').title()}: ${cost:,.2f}")
        print(f"  {'─'*70}")
        print(f"  TOTAL CAPITAL: ${cap['total_capital']:,.2f}")
        
        print(f"\n[ANNUAL COSTS]")
        annual = cost_analysis['annual_costs']
        for component, cost in annual.items():
            if component != 'total_annual':
                print(f"  {component.replace('_', ' ').title()}: ${cost:,.2f}")
        print(f"  {'─'*70}")
        print(f"  TOTAL ANNUAL: ${annual['total_annual']:,.2f}")
        
        print(f"\n[AMORTIZATION ({cost_analysis['amortization']['years']} years)]")
        print(f"  Capital Amortized: ${cost_analysis['amortization']['capital_amortized']:,.2f}")
        
        print(f"\n[TOTAL ANNUAL MARGINAL COST]")
        print(f"  ${cost_analysis['total_annual_cost']:,.2f}/year")
        
        print(f"\n[ASSUMPTIONS]")
        print(f"  Annual Miles: {cost_analysis['avg_annual_miles']:,.0f}")
        print(f"  Current Fleet Size: {cost_analysis['current_fleet_size']} units")
        print(f"\n{'='*80}\n")


if __name__ == "__main__":
    # Example borough configuration with sample cost variables
    # In practice, these would be loaded from extracted Excel data
    borough_config = {
        'Manhattan': {
            # Staffing
            'X1_emt_basic_annual': 55000,
            'X2_paramedic_annual': 82000,
            'X3_dispatch_annual': 62000,
            'X4_driver_annual': 52000,
            'X5_dispatch_annual': 62000,
            'X6_medical_director_annual': 190000,
            'X7_supervisor_annual': 100000,
            # Vehicles - ALS
            'X32_als_base_vehicle': 60000,
            'X33_als_conversion_upfit': 95000,
            'X34_als_sirens_lights': 7000,
            'X35_als_mounts_cabinetry': 9000,
            'X36_als_safety_certification': 3000,
            'X47_als_fuel_annual': 15000,
            'X50_als_maintenance_annual': 10000,
            # Additional variables would go here...
        },
        'Brooklyn': {
            'X1_emt_basic_annual': 52000,
            'X2_paramedic_annual': 78000,
            # ... all variables
        }
    }
    
    calculator = ComprehensiveMarginalCostCalculator(borough_config)
    
    # Example calculation
    print("✓ Comprehensive Marginal Cost Calculator initialized")
    print("✓ Ready to use with full 140+ variable support")
    print("\nTo use:")
    print("  cost = calculator.total_marginal_cost_annual('Manhattan', 'ALS', 50000, 38)")
    print("  calculator.print_marginal_cost_summary(cost)")
