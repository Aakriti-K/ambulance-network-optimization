"""
Parse cost_estimates.xlsx and generate parameterized cost variables
Maps all costs to variables (X1, X2, ... X70+) for flexibility
"""

import pandas as pd
import json
import re
from typing import Dict, Tuple


class CostEstimateParser:
    """Parse Excel cost estimates and generate parameterized variables"""
    
    def __init__(self, excel_file_path: str):
        """
        Initialize parser with Excel file
        
        Args:
            excel_file_path: Path to cost_estimates.xlsx
        """
        self.excel_file = excel_file_path
        self.cost_params = {}
        self.variable_counter = 1
        self.factor_details = {}
    
    def parse_excel(self) -> Dict[str, Dict]:
        """
        Parse Excel file and extract all cost data
        
        Returns:
            Dictionary with all factors and their costs
        """
        print(f"Parsing Excel file: {self.excel_file}")
        
        # Read all sheets
        excel_file = pd.ExcelFile(self.excel_file)
        sheet_name = excel_file.sheet_names[0]  # Assuming first sheet
        
        df = pd.read_excel(self.excel_file, sheet_name=sheet_name)
        
        print(f"Sheet: {sheet_name}")
        print(f"Columns: {df.columns.tolist()}")
        print(f"\nDataframe shape: {df.shape}")
        print("\nFirst 20 rows:")
        print(df.head(20))
        
        return df
    
    def clean_numeric_value(self, value) -> float:
        """
        Convert string or numeric value to float
        
        Args:
            value: Value to clean (may contain $, commas, /yr, etc.)
        
        Returns:
            Float value
        """
        if pd.isna(value) or value == "" or value == "—" or value == "NaN":
            return 0.0
        
        # Convert to string
        value_str = str(value).strip()
        
        # Remove currency symbols
        value_str = value_str.replace("$", "").replace("€", "").replace("£", "")
        
        # Remove descriptive suffixes
        value_str = re.sub(r'/yr|/year|per year|annually|per unit|per person|per FTE', '', value_str, flags=re.IGNORECASE)
        
        # Remove commas
        value_str = value_str.replace(",", "")
        
        # Extract just the number
        match = re.search(r'-?\d+\.?\d*', value_str)
        if match:
            return float(match.group())
        
        return 0.0
    
    def assign_variable(self, cost_name: str, cost_type: str = "numeric") -> str:
        """
        Assign a unique variable name to a cost
        
        Args:
            cost_name: Name of the cost
            cost_type: Type of cost (numeric, percentage, count, etc.)
        
        Returns:
            Variable name (e.g., 'X1', 'X2', etc.)
        """
        var_name = f"X{self.variable_counter}"
        self.variable_counter += 1
        return var_name
    
    def extract_factor_1_staffing(self, df: pd.DataFrame) -> Dict:
        """Extract Factor 1: Staffing costs"""
        factor_1 = {}
        
        # Staffing roles (annual per person)
        staffing_roles = {
            'EMT-Basic (per FTE)': 'emt_basic_annual',
            'Paramedic / ALS clinician (per FTE)': 'paramedic_annual',
            'Dispatch staff (per FTE)': 'dispatch_annual',
            'Supervisor / field ops (per FTE)': 'supervisor_annual',
            'Medical director / oversight (per FTE)': 'medical_director_annual',
            'Driver (non-clinical, per FTE)': 'driver_annual',
        }
        
        # One-time costs
        one_time_costs = {
            'Recruitment & onboarding (per hire)': 'recruitment_onboarding_per_hire',
            'Initial training & orientation (per hire)': 'training_orientation_per_hire',
        }
        
        print("\n" + "="*70)
        print("FACTOR 1: STAFFING COSTS")
        print("="*70)
        
        for cost_name, cost_key in staffing_roles.items():
            var_name = self.assign_variable(cost_name)
            # Looking for annual salary values - placeholder
            factor_1[var_name] = {
                'name': cost_name,
                'type': 'annual_per_person',
                'cost_key': cost_key,
                'description': f'Annual salary/cost for {cost_name}'
            }
            print(f"{var_name}: {cost_name} = $[To be extracted from Excel]")
        
        for cost_name, cost_key in one_time_costs.items():
            var_name = self.assign_variable(cost_name)
            factor_1[var_name] = {
                'name': cost_name,
                'type': 'one_time_per_hire',
                'cost_key': cost_key,
                'description': f'One-time cost for {cost_name}'
            }
            print(f"{var_name}: {cost_name} = $[To be extracted from Excel]")
        
        return factor_1
    
    def extract_factor_2_vehicles(self, df: pd.DataFrame) -> Dict:
        """Extract Factor 2: Vehicle costs (ALS, BLS, PTV)"""
        factor_2 = {}
        
        vehicle_components = {
            'Base vehicle (chassis/van)': 'base_vehicle',
            'Conversion / upfit (patient compartment build)': 'conversion_upfit',
            'Sirens, lights & warning systems': 'sirens_lights',
            'Mounts, cabinetry & restraint hardware': 'mounts_cabinetry',
            'Safety certification (DOT / NFPA)': 'safety_certification',
        }
        
        fuel_annual = {
            'ALS fuel cost': 'als_fuel_annual',
            'BLS fuel cost': 'bls_fuel_annual',
            'PTV fuel cost': 'ptv_fuel_annual',
        }
        
        maintenance_annual = {
            'Annual vehicle maintenance & inspection': 'maintenance_inspection_annual'
        }
        
        print("\n" + "="*70)
        print("FACTOR 2: VEHICLE COSTS (ALS / BLS / PTV)")
        print("="*70)
        
        # Capital components (per vehicle type)
        vehicle_types = ['ALS', 'BLS', 'PTV']
        for component_name, component_key in vehicle_components.items():
            for vtype in vehicle_types:
                var_name = self.assign_variable(f"{vtype}_{component_key}")
                factor_2[var_name] = {
                    'name': f"{component_name}",
                    'vehicle_type': vtype,
                    'type': 'capital_per_unit',
                    'component': component_key,
                    'description': f'{component_name} for {vtype}'
                }
                print(f"{var_name}: {vtype} - {component_name}")
        
        # Fuel costs (annual)
        for fuel_type, fuel_key in fuel_annual.items():
            for vtype in vehicle_types:
                var_name = self.assign_variable(f"{vtype}_{fuel_key}")
                factor_2[var_name] = {
                    'name': fuel_type,
                    'vehicle_type': vtype,
                    'type': 'annual_fuel',
                    'component': fuel_key,
                    'description': f'Annual fuel cost for {vtype}'
                }
                print(f"{var_name}: {vtype} - Annual Fuel")
        
        # Maintenance (annual)
        for vtype in vehicle_types:
            var_name = self.assign_variable(f"{vtype}_maintenance")
            factor_2[var_name] = {
                'name': 'Annual vehicle maintenance & inspection',
                'vehicle_type': vtype,
                'type': 'annual_maintenance',
                'description': f'Annual maintenance for {vtype}'
            }
            print(f"{var_name}: {vtype} - Annual Maintenance")
        
        return factor_2
    
    def extract_factor_3_medical_equipment(self, df: pd.DataFrame) -> Dict:
        """Extract Factor 3: In-vehicle medical equipment"""
        factor_3 = {}
        
        medical_equipment = {
            'Oxygen delivery system': 'oxygen_system',
            'Suction unit': 'suction_unit',
            'Stretcher': 'stretcher',
            'AED / basic defibrillator': 'aed',
            'Basic splints, bandaging': 'basic_supplies',
            'Monitor/defibrillator with pacing': 'monitor_defibrillator',
            'Capnography / end-tidal CO₂ monitor': 'capnography',
            'Advanced airway / intubation kit': 'airway_kit',
            'IV/IO access, drug kits': 'iv_access_drugs',
            'Wheelchair ramp system': 'wheelchair_ramp',
            'Wheelchair securement': 'wheelchair_securement',
            'GPS & vehicle signage': 'gps_signage',
            'First aid kit': 'first_aid_kit',
        }
        
        print("\n" + "="*70)
        print("FACTOR 3: IN-VEHICLE MEDICAL EQUIPMENT")
        print("="*70)
        
        for equipment_name, equipment_key in medical_equipment.items():
            for vtype in ['ALS', 'BLS', 'PTV']:
                var_name = self.assign_variable(f"{vtype}_{equipment_key}")
                factor_3[var_name] = {
                    'name': equipment_name,
                    'vehicle_type': vtype,
                    'type': 'capital_equipment',
                    'component': equipment_key,
                    'description': f'{equipment_name} for {vtype}'
                }
                print(f"{var_name}: {vtype} - {equipment_name}")
        
        # Annual supply replenishment
        for vtype in ['ALS', 'BLS', 'PTV']:
            var_name = self.assign_variable(f"{vtype}_supply_replenishment")
            factor_3[var_name] = {
                'name': 'Annual supply replenishment',
                'vehicle_type': vtype,
                'type': 'annual_supplies',
                'description': f'Annual drug and supply replenishment for {vtype}'
            }
            print(f"{var_name}: {vtype} - Annual Supply Replenishment")
        
        return factor_3
    
    def extract_factor_4_station_setup(self, df: pd.DataFrame) -> Dict:
        """Extract Factor 4: Station setup (per station)"""
        factor_4 = {}
        
        station_components = {
            'Lease / rent': 'rent_annual',
            'Security deposit': 'security_deposit_onetime',
            'Utilities': 'utilities_annual',
            'Parking / bay rental': 'parking_annual',
            'Power backup / generator': 'generator_onetime',
            'Internet & telecom': 'internet_telecom',
            'Office furniture & workstations': 'office_furniture',
            'Cleaning & janitorial services': 'janitorial_annual',
            'Lockers, restrooms & crew rest area': 'crew_facilities',
            'Maintenance bay setup': 'maintenance_bay',
            'Safety & security system': 'security_system',
        }
        
        print("\n" + "="*70)
        print("FACTOR 4: STATION SETUP (Per Station)")
        print("="*70)
        
        for component_name, component_key in station_components.items():
            var_name = self.assign_variable(f"station_{component_key}")
            factor_4[var_name] = {
                'name': component_name,
                'type': 'station_cost',
                'component': component_key,
                'description': f'{component_name} per station'
            }
            print(f"{var_name}: {component_name}")
        
        return factor_4
    
    def extract_factor_5_dispatch_connectivity(self, df: pd.DataFrame) -> Dict:
        """Extract Factor 5: Dispatch and connectivity architecture"""
        factor_5 = {}
        
        dispatch_components = {
            'Toll-free number provisioning': 'tollfree_number',
            'Carrier interconnect & SIP trunking': 'sip_trunking',
            'CAD software license': 'cad_software',
            'GIS routing engine': 'gis_routing',
            'EMD protocol scripts': 'emd_protocol',
            'Call recording & quality monitoring': 'call_recording',
            'Radio network': 'radio_network',
            'Mobile data terminals': 'mdt_hardware',
            'GPS / AVL platform': 'gps_avl',
            'Integration middleware': 'integration_middleware',
            'Dispatch workstations': 'dispatch_workstations',
            'Cellular data plans': 'cellular_data',
        }
        
        print("\n" + "="*70)
        print("FACTOR 5: DISPATCH & CONNECTIVITY")
        print("="*70)
        
        for component_name, component_key in dispatch_components.items():
            var_name = self.assign_variable(f"dispatch_{component_key}")
            factor_5[var_name] = {
                'name': component_name,
                'type': 'dispatch_connectivity',
                'component': component_key,
                'description': f'{component_name}'
            }
            print(f"{var_name}: {component_name}")
        
        return factor_5
    
    def extract_factor_6_architecture(self, df: pd.DataFrame) -> Dict:
        """Extract Factor 6: Architectural and system setup"""
        factor_6 = {}
        
        architecture_components = {
            'System architecture design & consulting': 'architecture_design',
            'Network infrastructure': 'network_infrastructure',
            'Cloud hosting setup': 'cloud_hosting',
            'System integration & API development': 'system_integration',
            'Cybersecurity hardening': 'cybersecurity',
            'Disaster recovery & backup': 'disaster_recovery',
            'UAT, load testing & go-live': 'uat_testing',
            'Staff IT training': 'it_training',
        }
        
        print("\n" + "="*70)
        print("FACTOR 6: ARCHITECTURAL / SYSTEM SETUP")
        print("="*70)
        
        for component_name, component_key in architecture_components.items():
            var_name = self.assign_variable(f"arch_{component_key}")
            factor_6[var_name] = {
                'name': component_name,
                'type': 'system_setup',
                'component': component_key,
                'description': f'{component_name}'
            }
            print(f"{var_name}: {component_name}")
        
        return factor_6
    
    def extract_factor_7_compliance(self, df: pd.DataFrame) -> Dict:
        """Extract Factor 7: Compliance costs"""
        factor_7 = {}
        
        compliance_components = {
            'EMS agency licensing': 'ems_licensing',
            'Vehicle registration & inspection': 'vehicle_registration',
            'General liability insurance': 'liability_insurance',
            'Vehicle insurance': 'vehicle_insurance',
            'Medical malpractice insurance': 'malpractice_insurance',
            'Medical director / QA program': 'qa_program',
            'Driver & clinical recertification': 'recertification',
            'PPE stock': 'ppe_stock',
            'Background checks & fingerprinting': 'background_checks',
            'HR & admin setup': 'hr_admin',
            'Data security & HIPAA audit': 'hipaa_audit',
            'Reserve vehicle downtime allowance': 'reserve_downtime',
        }
        
        print("\n" + "="*70)
        print("FACTOR 7: COMPLIANCE COSTS")
        print("="*70)
        
        for component_name, component_key in compliance_components.items():
            var_name = self.assign_variable(f"compliance_{component_key}")
            factor_7[var_name] = {
                'name': component_name,
                'type': 'compliance',
                'component': component_key,
                'description': f'{component_name}'
            }
            print(f"{var_name}: {component_name}")
        
        return factor_7
    
    def generate_variable_mapping(self) -> Dict:
        """Generate complete variable mapping"""
        print("\n" + "="*70)
        print("SUMMARY: TOTAL VARIABLES GENERATED")
        print("="*70)
        print(f"Total Variables: {self.variable_counter - 1}")
        print("\nNow run: python extract_costs_from_xlsx.py")
        print("to extract actual numeric values from the Excel file")
        
        return {
            'total_variables': self.variable_counter - 1,
            'message': 'Use extract_costs_from_xlsx.py to extract values from Excel'
        }


if __name__ == "__main__":
    parser = CostEstimateParser("cost_estimates.xlsx")
    
    # Parse Excel
    df = parser.parse_excel()
    
    # Extract all factors
    factor_1 = parser.extract_factor_1_staffing(df)
    factor_2 = parser.extract_factor_2_vehicles(df)
    factor_3 = parser.extract_factor_3_medical_equipment(df)
    factor_4 = parser.extract_factor_4_station_setup(df)
    factor_5 = parser.extract_factor_5_dispatch_connectivity(df)
    factor_6 = parser.extract_factor_6_architecture(df)
    factor_7 = parser.extract_factor_7_compliance(df)
    
    # Summary
    summary = parser.generate_variable_mapping()
