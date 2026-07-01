"""
===============================================================================
INTEGRATED COST MODEL - EXAMPLE USAGE
===============================================================================

This script demonstrates how to use the IntegratedCostModel with:
1. Your comprehensive cost analysis
2. Research paper formulas (Su et al., 2015)
3. Real relocation data from relocation_actions.csv

Steps:
1. Load cost parameters from Excel files
2. Load relocation data from CSV
3. Configure network parameters
4. Run integrated cost analysis
5. Compare scenarios

===============================================================================
"""

import pandas as pd
from integrated_cost_model import IntegratedCostModel, DemandPoint
from comprehensive_cost_calculator import ComprehensiveMarginalCostCalculator


# =============================================================================
# STEP 1: INITIALIZE COMPREHENSIVE COST CALCULATOR
# =============================================================================

def initialize_comprehensive_calculator():
    """
    Initialize the comprehensive cost calculator with NYC borough-specific costs.
    
    In practice, these values should be loaded from your cost_estimates.xlsx
    and comprehensive cost analysis. These are sample values.
    """
    
    borough_config = {
        'Manhattan': {
            # ========== STAFFING ==========
            'X1_emt_basic_annual': 55000,
            'X2_paramedic_annual': 82000,
            'X3_dispatch_annual': 62000,
            'X4_driver_annual': 52000,
            'X5_dispatch_annual': 62000,
            'X6_medical_director_annual': 190000,
            'X7_supervisor_annual': 100000,
            
            # ========== VEHICLES - ALS ==========
            'X32_als_base_vehicle': 60000,
            'X33_als_conversion_upfit': 95000,
            'X34_als_sirens_lights': 7000,
            'X35_als_mounts_cabinetry': 9000,
            'X36_als_safety_certification': 3000,
            'X47_als_fuel_annual': 15000,
            'X50_als_maintenance_annual': 10000,
            
            # ========== VEHICLES - BLS ==========
            'X37_bls_base_vehicle': 55000,
            'X38_bls_conversion_upfit': 75000,
            'X39_bls_sirens_lights': 6500,
            'X40_bls_mounts_cabinetry': 7500,
            'X41_bls_safety_certification': 2500,
            'X48_bls_fuel_annual': 13000,
            'X51_bls_maintenance_annual': 8500,
            
            # ========== VEHICLES - PTV ==========
            'X42_ptv_base_vehicle': 50000,
            'X43_ptv_conversion_upfit': 40000,
            'X44_ptv_sirens_lights': 4000,
            'X45_ptv_mounts_cabinetry': 5000,
            'X46_ptv_safety_certification': 2000,
            'X49_ptv_fuel_annual': 11000,
            'X52_ptv_maintenance_annual': 6500,
            
            # ========== MEDICAL EQUIPMENT ==========
            'X53_als_oxygen_system': 2000,
            'X54_als_suction_unit': 1500,
            'X55_als_stretcher': 7000,
            'X56_als_aed': 3500,
            'X57_als_basic_supplies': 2500,
            'X58_als_monitor_defibrillator': 30000,
            'X59_als_capnography': 5000,
            'X60_als_airway_kit': 4000,
            'X61_als_iv_access_drugs': 5500,
            'X62_bls_oxygen_system': 1800,
            'X63_bls_suction_unit': 1200,
            'X64_bls_stretcher': 6500,
            'X65_bls_aed': 3000,
            'X66_bls_basic_supplies': 2200,
            'X67_ptv_stretcher': 5500,
            'X68_ptv_wheelchair_ramp': 4500,
            'X69_ptv_wheelchair_securement': 2200,
            'X70_ptv_gps_signage': 1800,
            'X71_ptv_first_aid_kit': 400,
            'X72_als_supply_replenishment_annual': 9000,
            'X73_bls_supply_replenishment_annual': 4500,
            'X74_ptv_supply_replenishment_annual': 1200,
            
            # ========== STATION SETUP ==========
            'X75_security_deposit': 27000,
            'X76_generator_setup': 35000,
            'X77_office_furniture': 18000,
            'X78_crew_facilities': 22000,
            'X79_maintenance_bay': 45000,
            'X80_security_system': 12000,
            'X81_rent_annual': 108000,
            'X82_utilities_annual': 18000,
            'X83_parking_annual': 36000,
            'X84_generator_annual': 3000,
            'X85_internet_telecom_annual': 9600,
            'X86_janitorial_annual': 12000,
            
            # ========== DISPATCH & CONNECTIVITY ==========
            'X87_tollfree_number_onetime': 500,
            'X88_tollfree_number_annual': 2400,
            'X89_sip_trunking_onetime': 8000,
            'X90_sip_trunking_annual': 18000,
            'X91_cad_software_onetime': 85000,
            'X92_cad_software_annual': 24000,
            'X93_gis_routing_onetime': 15000,
            'X94_gis_routing_annual': 36000,
            'X95_emd_protocol_onetime': 12000,
            'X96_emd_protocol_annual': 6000,
            'X97_call_recording_onetime': 18000,
            'X98_call_recording_annual': 9600,
            'X99_radio_network_onetime': 120000,
            'X100_radio_network_annual': 14400,
            'X101_mdt_hardware_onetime': 45000,
            'X102_mdt_hardware_annual': 12000,
            'X103_gps_avl_onetime': 22000,
            'X104_gps_avl_annual': 18000,
            'X105_integration_middleware_onetime': 35000,
            'X106_integration_middleware_annual': 12000,
            'X107_dispatch_workstations_onetime': 28000,
            'X108_cellular_data_annual': 12000,
            
            # ========== ARCHITECTURE & SYSTEM ==========
            'X109_architecture_design_onetime': 65000,
            'X110_network_infrastructure_onetime': 55000,
            'X111_network_infrastructure_annual': 8000,
            'X112_cloud_hosting_onetime': 18000,
            'X113_cloud_hosting_annual': 36000,
            'X114_system_integration_onetime': 80000,
            'X115_cybersecurity_onetime': 35000,
            'X116_cybersecurity_annual': 18000,
            'X117_disaster_recovery_onetime': 25000,
            'X118_disaster_recovery_annual': 9600,
            'X119_uat_testing_onetime': 30000,
            'X120_it_training_onetime': 12000,
            
            # ========== COMPLIANCE ==========
            'X121_ems_licensing_onetime': 5000,
            'X122_ems_licensing_annual': 2500,
            'X123_vehicle_registration_onetime': 6000,
            'X124_vehicle_registration_annual': 6000,
            'X125_liability_insurance_annual': 85000,
            'X126_vehicle_insurance_annual': 48000,
            'X127_malpractice_insurance_annual': 35000,
            'X128_qa_program_onetime': 8000,
            'X129_qa_program_annual': 22000,
            'X130_recertification_annual': 18000,
            'X131_ppe_stock_onetime': 25000,
            'X132_ppe_stock_annual': 12000,
            'X133_background_checks_onetime': 12000,
            'X134_background_checks_annual': 3000,
            'X135_hr_admin_onetime': 18000,
            'X136_hr_admin_annual': 24000,
            'X137_hipaa_audit_onetime': 20000,
            'X138_hipaa_audit_annual': 15000,
            'X139_reserve_downtime_annual': 26300,
        },
        'Brooklyn': {
            # Similar structure with borough-specific adjustments
            'X1_emt_basic_annual': 52000,
            'X2_paramedic_annual': 78000,
            'X3_dispatch_annual': 58000,
            'X4_driver_annual': 50000,
            'X5_dispatch_annual': 58000,
            'X6_medical_director_annual': 180000,
            'X7_supervisor_annual': 95000,
            # ... (add remaining variables for Brooklyn)
        },
        'Queens': {
            'X1_emt_basic_annual': 51000,
            'X2_paramedic_annual': 76000,
            'X3_dispatch_annual': 56000,
            'X4_driver_annual': 48000,
            'X5_dispatch_annual': 56000,
            'X6_medical_director_annual': 175000,
            'X7_supervisor_annual': 90000,
            # ... (add remaining variables for Queens)
        },
        'Bronx': {
            'X1_emt_basic_annual': 51000,
            'X2_paramedic_annual': 76000,
            'X3_dispatch_annual': 56000,
            'X4_driver_annual': 48000,
            'X5_dispatch_annual': 56000,
            'X6_medical_director_annual': 175000,
            'X7_supervisor_annual': 90000,
            # ... (add remaining variables for Bronx)
        },
        'Staten Island': {
            'X1_emt_basic_annual': 50000,
            'X2_paramedic_annual': 74000,
            'X3_dispatch_annual': 54000,
            'X4_driver_annual': 46000,
            'X5_dispatch_annual': 54000,
            'X6_medical_director_annual': 170000,
            'X7_supervisor_annual': 85000,
            # ... (add remaining variables for Staten Island)
        }
    }
    
    calculator = ComprehensiveMarginalCostCalculator(borough_config)
    return calculator


# =============================================================================
# STEP 2: LOAD RELOCATION DATA
# =============================================================================

def load_relocation_data(filepath='relocation_actions.csv'):
    """Load relocation data from CSV."""
    df = pd.read_csv(filepath)
    print(f"✓ Loaded {len(df)} relocation actions")
    print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
    print(f"  Boroughs: {df['borough'].unique()}")
    return df


# =============================================================================
# STEP 3: DEFINE DEMAND POINTS (from research paper)
# =============================================================================

def create_demand_points():
    """
    Define demand points for NYC boroughs.
    
    These represent population density and expected response delays.
    Values should be calibrated based on actual NYC data.
    """
    return [
        DemandPoint(population=1620000, expected_delay=4.5),  # Manhattan
        DemandPoint(population=2600000, expected_delay=5.2),  # Brooklyn
        DemandPoint(population=2330000, expected_delay=5.8),  # Queens
        DemandPoint(population=1420000, expected_delay=5.1),  # Bronx
        DemandPoint(population=480000, expected_delay=6.2),   # Staten Island
    ]


# =============================================================================
# STEP 4: DEFINE NETWORK CONFIGURATION
# =============================================================================

def create_network_config_baseline():
    """
    Define baseline network configuration (current state).
    
    Based on typical NYC EMS deployment:
    - Manhattan: 9 ALS, 5 BLS, 4 PTV
    - Brooklyn: 8 ALS, 6 BLS, 3 PTV
    - Queens: 6 ALS, 5 BLS, 2 PTV
    - Bronx: 5 ALS, 4 BLS, 2 PTV
    - Staten Island: 2 ALS, 1 BLS, 1 PTV
    """
    return {
        'Manhattan': {
            'num_stations': 9,
            'num_als': 9,
            'num_bls': 5,
            'num_ptv': 4,
        },
        'Brooklyn': {
            'num_stations': 8,
            'num_als': 8,
            'num_bls': 6,
            'num_ptv': 3,
        },
        'Queens': {
            'num_stations': 6,
            'num_als': 6,
            'num_bls': 5,
            'num_ptv': 2,
        },
        'Bronx': {
            'num_stations': 5,
            'num_als': 5,
            'num_bls': 4,
            'num_ptv': 2,
        },
        'Staten Island': {
            'num_stations': 2,
            'num_als': 2,
            'num_bls': 1,
            'num_ptv': 1,
        }
    }


def create_network_config_optimized():
    """Define optimized network configuration (after optimization)."""
    return {
        'Manhattan': {
            'num_stations': 10,
            'num_als': 11,
            'num_bls': 6,
            'num_ptv': 5,
        },
        'Brooklyn': {
            'num_stations': 9,
            'num_als': 9,
            'num_bls': 7,
            'num_ptv': 4,
        },
        'Queens': {
            'num_stations': 7,
            'num_als': 7,
            'num_bls': 6,
            'num_ptv': 3,
        },
        'Bronx': {
            'num_stations': 6,
            'num_als': 6,
            'num_bls': 5,
            'num_ptv': 3,
        },
        'Staten Island': {
            'num_stations': 2,
            'num_als': 2,
            'num_bls': 1,
            'num_ptv': 1,
        }
    }


# =============================================================================
# STEP 5: CREATE AND RUN INTEGRATED COST MODEL
# =============================================================================

def main():
    """Main execution function."""
    
    print("\n" + "=" * 80)
    print("INTEGRATED COST MODEL - EXECUTION")
    print("=" * 80)
    
    # Initialize calculator
    print("\n[1/5] Initializing comprehensive cost calculator...")
    calculator = initialize_comprehensive_calculator()
    print("✓ Comprehensive calculator ready")
    
    # Load relocation data
    print("\n[2/5] Loading relocation data...")
    try:
        relocation_df = load_relocation_data()
    except FileNotFoundError:
        print("⚠ relocation_actions.csv not found, continuing without relocation data")
        relocation_df = None
    
    # Create demand points
    print("\n[3/5] Creating demand points...")
    demand_points = create_demand_points()
    print(f"✓ {len(demand_points)} demand points created")
    
    # Create baseline network configuration
    print("\n[4/5] Creating network configurations...")
    baseline_config = create_network_config_baseline()
    optimized_config = create_network_config_optimized()
    print("✓ Baseline and optimized configurations ready")
    
    # Initialize integrated cost model
    print("\n[5/5] Initializing integrated cost model...")
    model = IntegratedCostModel(
        comprehensive_calculator=calculator,
        network_config=baseline_config,
        demand_points=demand_points,
        
        # Research paper parameters
        call_probability=0.03,
        severe_probability=0.07662,
        regular_probability=0.92338,
        severe_cost_per_minute=5000,
        regular_cost_per_minute=500,
        
        # Relocation
        relocation_df=relocation_df,
        relocation_cost_per_km=120.0,
        
        # Opportunity cost
        extra_response_time=35,
        penalty_per_minute=500,
        
        # Additional parameters
        avg_annual_miles=45000,
        amortization_years=5
    )
    print("✓ Integrated model initialized")
    
    # =========================================================================
    # RUN ANALYSIS
    # =========================================================================
    
    print("\n" + "=" * 80)
    print("BASELINE SCENARIO ANALYSIS")
    print("=" * 80)
    
    model.print_cost_summary()
    
    baseline_costs = model.total_cost()
    baseline_total = baseline_costs['total_annual_network_cost']
    
    # Get percentage breakdown
    percentages = model.cost_breakdown_percentage()
    print("\n[COST BREAKDOWN - PERCENTAGE]")
    for component, pct in percentages.items():
        print(f"  {component.replace('_', ' ').title()}: {pct:.1f}%")
    
    # =========================================================================
    # SCENARIO COMPARISON
    # =========================================================================
    
    print("\n" + "=" * 80)
    print("SCENARIO COMPARISON: BASELINE vs OPTIMIZED")
    print("=" * 80)
    
    scenarios = {
        'Baseline': baseline_config,
        'Optimized': optimized_config
    }
    
    comparison = model.compare_scenarios(scenarios)
    
    print("\n[COST COMPARISON]")
    print(f"{'Scenario':<20} {'Total Annual Cost':<25} {'Difference':<20}")
    print("─" * 65)
    
    baseline_total = comparison['Baseline']['total_annual_network_cost']
    optimized_total = comparison['Optimized']['total_annual_network_cost']
    difference = optimized_total - baseline_total
    pct_change = (difference / baseline_total) * 100
    
    print(f"{'Baseline':<20} ${baseline_total:>22,.2f}")
    print(f"{'Optimized':<20} ${optimized_total:>22,.2f}")
    print("─" * 65)
    print(f"{'Difference':<20} ${difference:>22,.2f}  ({pct_change:+.1f}%)")
    
    # Detail breakdown
    print("\n[DETAILED COST BREAKDOWN]")
    print(f"\n{'Cost Component':<25} {'Baseline':<20} {'Optimized':<20} {'Change':<15}")
    print("─" * 80)
    
    components = ['station_costs', 'vehicle_costs', 'delay_cost', 
                  'relocation_cost', 'opportunity_cost']
    
    for component in components:
        if component in comparison['Baseline']:
            baseline_val = comparison['Baseline'].get(component, {})
            optimized_val = comparison['Optimized'].get(component, {})
            
            if isinstance(baseline_val, dict):
                baseline_val = baseline_val.get('total', sum(
                    v for v in baseline_val.values() if isinstance(v, (int, float))
                ))
            if isinstance(optimized_val, dict):
                optimized_val = optimized_val.get('total', sum(
                    v for v in optimized_val.values() if isinstance(v, (int, float))
                ))
            
            change = optimized_val - baseline_val
            change_pct = (change / baseline_val * 100) if baseline_val != 0 else 0
            
            print(f"{component.replace('_', ' ').title():<25} "
                  f"${baseline_val:>17,.2f} "
                  f"${optimized_val:>17,.2f} "
                  f"${change:>12,.2f} ({change_pct:+.1f}%)")
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
