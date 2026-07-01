"""
===============================================================================
INTEGRATED COST MODEL - TEST WITH REAL RELOCATION DATA
===============================================================================

This script runs the integrated model with actual relocation_actions.csv data
to produce real cost analysis results for NYC ambulance network optimization.

Key outputs:
1. Baseline network cost breakdown
2. Cost per component analysis
3. Relocation cost impact
4. Scenario comparison (before/after optimization)

===============================================================================
"""

import pandas as pd
import numpy as np
from integrated_cost_model import IntegratedCostModel, DemandPoint
from comprehensive_cost_calculator import ComprehensiveMarginalCostCalculator


# =============================================================================
# STEP 1: CREATE MINIMAL COMPLETE BOROUGH CONFIG
# =============================================================================

def create_borough_config():
    """
    Create complete borough configuration with all required cost variables.
    Uses realistic NYC EMS cost data from your comprehensive analysis.
    """
    
    # Base template with all required variables (X1-X139)
    base_template = {
        # ========== STAFFING (X1-X7) ==========
        'X1_emt_basic_annual': 52000,
        'X2_paramedic_annual': 78000,
        'X3_dispatch_annual': 58000,
        'X4_driver_annual': 50000,
        'X5_dispatch_annual': 58000,
        'X6_medical_director_annual': 180000,
        'X7_supervisor_annual': 95000,
        
        # ========== VEHICLES - ALS (X32-X36) ==========
        'X32_als_base_vehicle': 60000,
        'X33_als_conversion_upfit': 95000,
        'X34_als_sirens_lights': 7000,
        'X35_als_mounts_cabinetry': 9000,
        'X36_als_safety_certification': 3000,
        
        # ========== VEHICLES - BLS (X37-X41) ==========
        'X37_bls_base_vehicle': 55000,
        'X38_bls_conversion_upfit': 75000,
        'X39_bls_sirens_lights': 6500,
        'X40_bls_mounts_cabinetry': 7500,
        'X41_bls_safety_certification': 2500,
        
        # ========== VEHICLES - PTV (X42-X46) ==========
        'X42_ptv_base_vehicle': 50000,
        'X43_ptv_conversion_upfit': 40000,
        'X44_ptv_sirens_lights': 4000,
        'X45_ptv_mounts_cabinetry': 5000,
        'X46_ptv_safety_certification': 2000,
        
        # ========== VEHICLE FUEL (X47-X49) ==========
        'X47_als_fuel_annual': 15000,
        'X48_bls_fuel_annual': 13000,
        'X49_ptv_fuel_annual': 11000,
        
        # ========== VEHICLE MAINTENANCE (X50-X52) ==========
        'X50_als_maintenance_annual': 10000,
        'X51_bls_maintenance_annual': 8500,
        'X52_ptv_maintenance_annual': 6500,
        
        # ========== MEDICAL EQUIPMENT - ALS (X53-X61) ==========
        'X53_als_oxygen_system': 2000,
        'X54_als_suction_unit': 1500,
        'X55_als_stretcher': 7000,
        'X56_als_aed': 3500,
        'X57_als_basic_supplies': 2500,
        'X58_als_monitor_defibrillator': 30000,
        'X59_als_capnography': 5000,
        'X60_als_airway_kit': 4000,
        'X61_als_iv_access_drugs': 5500,
        
        # ========== MEDICAL EQUIPMENT - BLS (X62-X66) ==========
        'X62_bls_oxygen_system': 1800,
        'X63_bls_suction_unit': 1200,
        'X64_bls_stretcher': 6500,
        'X65_bls_aed': 3000,
        'X66_bls_basic_supplies': 2200,
        
        # ========== MEDICAL EQUIPMENT - PTV (X67-X71) ==========
        'X67_ptv_stretcher': 5500,
        'X68_ptv_wheelchair_ramp': 4500,
        'X69_ptv_wheelchair_securement': 2200,
        'X70_ptv_gps_signage': 1800,
        'X71_ptv_first_aid_kit': 400,
        
        # ========== MEDICAL SUPPLIES (X72-X74) ==========
        'X72_als_supply_replenishment_annual': 9000,
        'X73_bls_supply_replenishment_annual': 4500,
        'X74_ptv_supply_replenishment_annual': 1200,
        
        # ========== STATION SETUP (X75-X80) ==========
        'X75_security_deposit': 27000,
        'X76_generator_setup': 35000,
        'X77_office_furniture': 18000,
        'X78_crew_facilities': 22000,
        'X79_maintenance_bay': 45000,
        'X80_security_system': 12000,
        
        # ========== STATION ANNUAL (X81-X86) ==========
        'X81_rent_annual': 108000,
        'X82_utilities_annual': 18000,
        'X83_parking_annual': 36000,
        'X84_generator_annual': 3000,
        'X85_internet_telecom_annual': 9600,
        'X86_janitorial_annual': 12000,
        
        # ========== DISPATCH & CONNECTIVITY - SETUP (X87-X107) ==========
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
        
        # ========== ARCHITECTURE & SYSTEM (X109-X120) ==========
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
        
        # ========== COMPLIANCE (X121-X139) ==========
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
    }
    
    # Borough-specific adjustments
    boroughs = {
        'Manhattan': {**base_template, 'X81_rent_annual': 120000},  # Higher rent
        'Brooklyn': {**base_template, 'X81_rent_annual': 95000},
        'Queens': {**base_template, 'X81_rent_annual': 85000},
        'Bronx': {**base_template, 'X81_rent_annual': 75000},
        'Staten Island': {**base_template, 'X81_rent_annual': 65000},
    }
    
    return boroughs


# =============================================================================
# STEP 2: CREATE DEMAND POINTS
# =============================================================================

def create_demand_points():
    """Create demand points based on NYC borough populations and response times."""
    return [
        DemandPoint(population=1620000, expected_delay=4.5),    # Manhattan
        DemandPoint(population=2600000, expected_delay=5.2),    # Brooklyn
        DemandPoint(population=2330000, expected_delay=5.8),    # Queens
        DemandPoint(population=1420000, expected_delay=5.1),    # Bronx
        DemandPoint(population=480000, expected_delay=6.2),     # Staten Island
    ]


# =============================================================================
# STEP 3: EXTRACT NETWORK CONFIG FROM RELOCATION DATA
# =============================================================================

def extract_network_from_relocation_data(relocation_df):
    """
    Extract baseline network configuration from relocation_actions.csv.
    Calculates average units per borough from prev_units column.
    """
    network_config = {}
    
    # Group by borough and get average vehicle counts
    for borough in relocation_df['borough'].unique():
        borough_data = relocation_df[relocation_df['borough'] == borough]
        
        # Average previous units gives us the baseline
        avg_units = borough_data['prev_units'].mean()
        
        # Estimate ALS/BLS/PTV split (typical: 40% ALS, 35% BLS, 25% PTV)
        num_als = int(avg_units * 0.40)
        num_bls = int(avg_units * 0.35)
        num_ptv = int(avg_units * 0.25)
        
        # Number of stations (roughly 1 station per 15-20 vehicles)
        num_stations = max(1, int(avg_units / 18))
        
        network_config[borough] = {
            'num_stations': num_stations,
            'num_als': max(1, num_als),  # At least 1
            'num_bls': max(1, num_bls),
            'num_ptv': max(1, num_ptv),
        }
    
    return network_config


# =============================================================================
# STEP 4: CREATE OPTIMIZED NETWORK CONFIG
# =============================================================================

def create_optimized_network_from_relocation(relocation_df):
    """
    Create optimized network configuration based on relocation actions.
    Adds vehicles where net moves were positive (increase demand).
    """
    network_config = {}
    
    for borough in relocation_df['borough'].unique():
        borough_data = relocation_df[relocation_df['borough'] == borough]
        
        # Get final units as optimized state
        final_units = borough_data['new_units'].mean()
        
        # Same split
        num_als = int(final_units * 0.40)
        num_bls = int(final_units * 0.35)
        num_ptv = int(final_units * 0.25)
        
        num_stations = max(1, int(final_units / 18))
        
        network_config[borough] = {
            'num_stations': num_stations,
            'num_als': max(1, num_als),
            'num_bls': max(1, num_bls),
            'num_ptv': max(1, num_ptv),
        }
    
    return network_config


# =============================================================================
# MAIN TEST EXECUTION
# =============================================================================

def main():
    """Main test execution with real relocation data."""
    
    print("\n" + "=" * 90)
    print("INTEGRATED COST MODEL - TEST WITH REAL RELOCATION DATA")
    print("=" * 90)
    
    # Load relocation data
    print("\n[STEP 1] Loading relocation_actions.csv...")
    try:
        relocation_df = pd.read_csv('relocation_actions.csv')
        print(f"✓ Loaded {len(relocation_df)} relocation records")
        print(f"  Date range: {relocation_df['date'].min()} to {relocation_df['date'].max()}")
        print(f"  Shifts: {relocation_df['shift_label'].unique()}")
        print(f"  Boroughs: {sorted(relocation_df['borough'].unique())}")
    except FileNotFoundError:
        print("✗ Error: relocation_actions.csv not found")
        return
    
    # Display relocation summary
    print("\n[RELOCATION SUMMARY]")
    relocation_summary = relocation_df.groupby('borough').agg({
        'net': 'sum',
        'prev_units': 'mean',
        'new_units': 'mean'
    }).round(1)
    print(relocation_summary)
    
    # Initialize comprehensive calculator
    print("\n[STEP 2] Initializing comprehensive cost calculator...")
    borough_config = create_borough_config()
    calculator = ComprehensiveMarginalCostCalculator(borough_config)
    print("✓ Calculator initialized with 140+ cost variables")
    
    # Create demand points
    print("\n[STEP 3] Creating demand points...")
    demand_points = create_demand_points()
    print(f"✓ {len(demand_points)} demand points created")
    
    # Extract network configurations
    print("\n[STEP 4] Extracting network configurations from relocation data...")
    baseline_config = extract_network_from_relocation_data(relocation_df)
    optimized_config = create_optimized_network_from_relocation(relocation_df)
    
    print("\n  BASELINE CONFIGURATION (prev_units average):")
    for borough, config in baseline_config.items():
        total = config['num_als'] + config['num_bls'] + config['num_ptv']
        print(f"    {borough:20} | Stations: {config['num_stations']} | "
              f"ALS: {config['num_als']:2} BLS: {config['num_bls']:2} PTV: {config['num_ptv']:2} | Total: {total}")
    
    print("\n  OPTIMIZED CONFIGURATION (new_units average):")
    for borough, config in optimized_config.items():
        total = config['num_als'] + config['num_bls'] + config['num_ptv']
        print(f"    {borough:20} | Stations: {config['num_stations']} | "
              f"ALS: {config['num_als']:2} BLS: {config['num_bls']:2} PTV: {config['num_ptv']:2} | Total: {total}")
    
    # Initialize integrated model
    print("\n[STEP 5] Initializing integrated cost model...")
    model_baseline = IntegratedCostModel(
        comprehensive_calculator=calculator,
        network_config=baseline_config,
        demand_points=demand_points,
        call_probability=0.03,
        severe_probability=0.07662,
        regular_probability=0.92338,
        severe_cost_per_minute=5000,
        regular_cost_per_minute=500,
        relocation_df=relocation_df,
        relocation_cost_per_km=120.0,
        extra_response_time=35,
        penalty_per_minute=500,
        avg_annual_miles=45000,
        amortization_years=5
    )
    print("✓ Baseline model ready")
    
    # Run analysis
    print("\n" + "=" * 90)
    print("BASELINE NETWORK COST ANALYSIS")
    print("=" * 90)
    
    model_baseline.print_cost_summary()
    baseline_results = model_baseline.total_cost()
    
    # Cost breakdown percentages
    print("\n[COST BREAKDOWN - PERCENTAGES]")
    percentages = model_baseline.cost_breakdown_percentage()
    for component, pct in sorted(percentages.items(), key=lambda x: x[1], reverse=True):
        label = component.replace('_pct', '').replace('_', ' ').title()
        print(f"  {label:<30} {pct:>6.1f}%")
    
    # Borough-level breakdown
    print("\n[STATION COSTS - BY BOROUGH]")
    station_costs = model_baseline.station_cost()
    for borough in sorted(baseline_config.keys()):
        cost = station_costs.get(borough.lower(), 0)
        print(f"  {borough:<20} ${cost:>15,.2f}")
    
    print("\n[VEHICLE COSTS - BY TYPE]")
    vehicle_costs = model_baseline.vehicle_cost()
    for vtype in ['ALS', 'BLS', 'PTV']:
        type_cost = sum(vehicle_costs.get(vtype, {}).values())
        print(f"  {vtype:<20} ${type_cost:>15,.2f}")
    
    # Relocation cost analysis
    print("\n[RELOCATION COSTS - BY BOROUGH]")
    relocation_costs = model_baseline.relocation_cost()
    for borough, cost in relocation_costs['by_borough'].items():
        print(f"  {borough:<20} ${cost:>15,.2f}")
    
    # =========================================================================
    # SCENARIO COMPARISON
    # =========================================================================
    
    print("\n" + "=" * 90)
    print("SCENARIO COMPARISON: BASELINE vs OPTIMIZED")
    print("=" * 90)
    
    model_optimized = IntegratedCostModel(
        comprehensive_calculator=calculator,
        network_config=optimized_config,
        demand_points=demand_points,
        call_probability=0.03,
        severe_probability=0.07662,
        regular_probability=0.92338,
        severe_cost_per_minute=5000,
        regular_cost_per_minute=500,
        relocation_df=relocation_df,
        relocation_cost_per_km=120.0,
        extra_response_time=35,
        penalty_per_minute=500,
        avg_annual_miles=45000,
        amortization_years=5
    )
    
    optimized_results = model_optimized.total_cost()
    
    baseline_total = baseline_results['total_annual_network_cost']
    optimized_total = optimized_results['total_annual_network_cost']
    difference = optimized_total - baseline_total
    pct_change = (difference / baseline_total) * 100 if baseline_total != 0 else 0
    
    print(f"\n{'Metric':<40} {'Baseline':>20} {'Optimized':>20} {'Change':>20}")
    print("─" * 100)
    print(f"{'Total Annual Network Cost':<40} ${baseline_total:>18,.2f} ${optimized_total:>18,.2f} ${difference:>18,.2f}")
    print(f"{'Percentage Change':<40} {'':>20} {'':>20} {pct_change:>19.1f}%")
    
    # Component comparison
    print("\n[COMPONENT COMPARISON]")
    print(f"\n{'Cost Component':<40} {'Baseline':>20} {'Optimized':>20} {'Change':>20}")
    print("─" * 100)
    
    components = {
        'Station Costs': 'station_costs',
        'Vehicle Costs': 'vehicle_costs',
        'Delay Cost': 'delay_cost',
        'Relocation Cost': 'relocation_cost',
        'Opportunity Cost': 'opportunity_cost'
    }
    
    for label, key in components.items():
        baseline_val = baseline_results.get(key, {})
        optimized_val = optimized_results.get(key, {})
        
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
        
        print(f"{label:<40} ${baseline_val:>18,.2f} ${optimized_val:>18,.2f} ${change:>18,.2f} ({change_pct:+.1f}%)")
    
    # Summary statistics
    print("\n" + "=" * 90)
    print("SUMMARY")
    print("=" * 90)
    print(f"Total Vehicles (Baseline): {sum(c['num_als'] + c['num_bls'] + c['num_ptv'] for c in baseline_config.values())}")
    print(f"Total Vehicles (Optimized): {sum(c['num_als'] + c['num_bls'] + c['num_ptv'] for c in optimized_config.values())}")
    print(f"Total Stations (Baseline): {sum(c['num_stations'] for c in baseline_config.values())}")
    print(f"Total Stations (Optimized): {sum(c['num_stations'] for c in optimized_config.values())}")
    print(f"\nAnnual Cost Impact: ${difference:,.2f} ({pct_change:+.1f}%)")
    
    if difference < 0:
        print(f"✓ OPTIMIZATION SAVES ${abs(difference):,.2f} per year")
    else:
        print(f"⚠ OPTIMIZATION COSTS ${difference:,.2f} more per year")
    
    print("\n" + "=" * 90 + "\n")


if __name__ == "__main__":
    main()
