"""
===============================================================================
INTEGRATED COST MODEL - QUICK REFERENCE GUIDE
===============================================================================

This guide explains the integrated cost model architecture and how to use it.

===============================================================================
"""

# =============================================================================
# ARCHITECTURE OVERVIEW
# =============================================================================

"""
┌─────────────────────────────────────────────────────────────────────────┐
│                     INTEGRATED COST MODEL ARCHITECTURE                  │
└─────────────────────────────────────────────────────────────────────────┘

                    COMPREHENSIVE COST CALCULATOR
                    (comprehensive_cost_calculator.py)
                              ↓
            ┌─────────────────────────────────────┐
            │  140+ Cost Variables (X1-X139)      │
            │  ├─ Staffing (X1-X7)               │
            │  ├─ Vehicles (X32-X52)             │
            │  ├─ Medical Equipment (X53-X74)    │
            │  ├─ Station (X75-X86)              │
            │  ├─ Dispatch (X87-X108)            │
            │  ├─ Architecture (X109-X120)       │
            │  └─ Compliance (X121-X139)         │
            └─────────────────────────────────────┘
                              ↓
            ┌─────────────────────────────────────┐
            │  INTEGRATED COST MODEL              │
            │  (integrated_cost_model.py)         │
            └─────────────────────────────────────┘
                    ↓              ↓
            ┌──────────┐    ┌──────────┐
            │RESEARCH  │    │RELOCATION│
            │PAPER     │    │DATA      │
            │FORMULAS  │    │(CSV)     │
            └──────────┘    └──────────┘
                    ↓              ↓
    ┌───────────────────────────────────────────┐
    │  NETWORK-LEVEL COSTS                      │
    │  ├─ Station Cost                          │
    │  ├─ Vehicle Cost (marginal approach)      │
    │  ├─ Delay Cost (research paper formula)   │
    │  ├─ Relocation Cost (real data)           │
    │  └─ Opportunity Cost                      │
    └───────────────────────────────────────────┘
                    ↓
        ┌─────────────────────────────┐
        │  TOTAL NETWORK COST         │
        │  + Scenario Comparison      │
        │  + Cost Breakdown Analysis  │
        └─────────────────────────────┘
"""

# =============================================================================
# KEY FORMULAS
# =============================================================================

"""
┌─────────────────────────────────────────────────────────────────────────┐
│                           FORMULA REFERENCE                             │
└─────────────────────────────────────────────────────────────────────────┘

1. STATION COST (from comprehensive calculator)
   ──────────────────────────────────────────────
   Station Cost = Σ_boroughs (num_stations × annual_station_cost)
   
   Where annual_station_cost includes:
   - Rent: X81_rent_annual
   - Utilities: X82_utilities_annual
   - Parking: X83_parking_annual
   - Generator: X84_generator_annual
   - Internet/Telecom: X85_internet_telecom_annual
   - Janitorial: X86_janitorial_annual


2. VEHICLE COST (from comprehensive calculator with marginal approach)
   ──────────────────────────────────────────────────────────────────
   Vehicle Cost = Σ_types Σ_boroughs (
       num_vehicles × [
           (capital_cost / amortization_years) +
           annual_operating_cost +
           staffing_cost
       ]
   )
   
   Where capital_cost includes:
   - Vehicle hardware (chassis, conversion, sirens, etc.)
   - Medical equipment
   - Deployment setup
   
   Where annual_operating includes:
   - Fuel costs
   - Maintenance
   - Medical supplies
   
   Where staffing includes:
   - Personnel salaries
   - Crew allocation


3. DELAY COST (from Su et al., 2015 research paper)
   ──────────────────────────────────────────────────
   Delay Cost = Σ_i (
       P_call × λ_i × a_i × [P_severe × C_severe + P_regular × C_regular]
   )
   
   Where:
   - P_call: Probability of call per person per year (0.03)
   - λ_i: Population at demand point i
   - a_i: Expected delay (minutes) at demand point i
   - P_severe: Probability of severe case (0.07662)
   - C_severe: Cost per minute for severe ($5,000)
   - P_regular: Probability of regular case (0.92338)
   - C_regular: Cost per minute for regular ($500)


4. RELOCATION COST (from relocation_actions.csv)
   ──────────────────────────────────────────────
   Relocation Cost = Σ_actions (
       |net_vehicles_moved| × avg_relocation_distance_km × cost_per_km
   )
   
   Where:
   - net_vehicles_moved: r_in - r_out from CSV
   - avg_relocation_distance_km: ~7.5 km (within NYC)
   - cost_per_km: $120/km (default)


5. OPPORTUNITY COST
   ──────────────────
   Opportunity Cost = Extra_Response_Time × Penalty_Per_Minute
   
   Where:
   - Extra_Response_Time: Minutes (default: 35 min)
   - Penalty_Per_Minute: $500/min


6. TOTAL NETWORK COST
   ──────────────────
   Total Cost = Station Cost + Vehicle Cost + Delay Cost + 
                Relocation Cost + Opportunity Cost
"""

# =============================================================================
# USAGE EXAMPLES
# =============================================================================

"""
┌─────────────────────────────────────────────────────────────────────────┐
│                           USAGE EXAMPLES                                 │
└─────────────────────────────────────────────────────────────────────────┘

EXAMPLE 1: Run Test with Real Data
─────────────────────────────────────

    python test_integrated_model.py
    
    This will:
    1. Load relocation_actions.csv
    2. Extract baseline and optimized network configs
    3. Calculate costs for both scenarios
    4. Show detailed breakdown and comparison


EXAMPLE 2: Custom Cost Analysis
──────────────────────────────────

    from integrated_cost_model import IntegratedCostModel, DemandPoint
    from comprehensive_cost_calculator import ComprehensiveMarginalCostCalculator
    import pandas as pd
    
    # Initialize calculator
    calculator = ComprehensiveMarginalCostCalculator(borough_config)
    
    # Load relocation data
    relocation_df = pd.read_csv('relocation_actions.csv')
    
    # Create demand points
    demand_points = [
        DemandPoint(population=1620000, expected_delay=4.5),
        # ... more points
    ]
    
    # Define network configuration
    network_config = {
        'Manhattan': {'num_stations': 9, 'num_als': 9, 'num_bls': 5, 'num_ptv': 4},
        'Brooklyn': {'num_stations': 8, 'num_als': 8, 'num_bls': 6, 'num_ptv': 3},
        # ... more boroughs
    }
    
    # Initialize model
    model = IntegratedCostModel(
        comprehensive_calculator=calculator,
        network_config=network_config,
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
    
    # Get total cost breakdown
    results = model.total_cost()
    print(f"Total Network Cost: ${results['total_annual_network_cost']:,.2f}")
    
    # Print formatted summary
    model.print_cost_summary()
    
    # Get percentage breakdown
    percentages = model.cost_breakdown_percentage()
    print(percentages)
    
    # Compare scenarios
    comparison = model.compare_scenarios({
        'Scenario A': config_a,
        'Scenario B': config_b
    })


EXAMPLE 3: Analyze Cost Components
───────────────────────────────────

    # Station costs by borough
    station_costs = model.station_cost()
    for borough, cost in station_costs.items():
        print(f"{borough}: ${cost:,.2f}")
    
    # Vehicle costs by type
    vehicle_costs = model.vehicle_cost()
    for vtype in ['ALS', 'BLS', 'PTV']:
        cost = sum(vehicle_costs.get(vtype, {}).values())
        print(f"{vtype}: ${cost:,.2f}")
    
    # Delay cost
    delay = model.delay_cost()
    print(f"Delay Cost: ${delay:,.2f}")
    
    # Relocation cost
    relocation = model.relocation_cost()
    print(f"Relocation Cost: ${relocation['total']:,.2f}")
"""

# =============================================================================
# FILE STRUCTURE
# =============================================================================

"""
┌─────────────────────────────────────────────────────────────────────────┐
│                        PROJECT FILE STRUCTURE                           │
└─────────────────────────────────────────────────────────────────────────┘

ambulance-network-optimization/
│
├── CORE MODULES
│   ├── comprehensive_cost_calculator.py
│   │   └── ComprehensiveMarginalCostCalculator class
│   │       • Calculates 140+ cost variables
│   │       • Borough-specific costs
│   │       • Vehicle/staffing/compliance breakdowns
│   │
│   ├── ems_cost_model.py
│   │   └── EMSCostModel class (research paper formulas)
│   │       • Station cost
│   │       • Vehicle cost (simplified)
│   │       • Delay cost (research paper formula)
│   │
│   └── integrated_cost_model.py ★ NEW
│       └── IntegratedCostModel class
│           • Combines comprehensive + research paper
│           • Processes relocation data
│           • Network-level optimization
│
├── TESTING & EXAMPLES
│   ├── test_integrated_model.py ★ NEW
│   │   └── Run with real relocation_actions.csv
│   │       • Extracts network configs from data
│   │       • Compares baseline vs optimized
│   │       • Produces detailed analysis
│   │
│   └── example_integrated_cost_analysis.py
│       └── Complete example with sample data
│
├── DATA FILES
│   ├── relocation_actions.csv
│   │   └── Vehicle repositioning records (2022-07-01 onwards)
│   │       • date, shift, borough, IDA_id
│   │       • r_in (vehicles added), r_out (removed)
│   │       • prev_units → new_units
│   │
│   ├── cost_estimates.xlsx
│   │   └── Detailed cost breakdown
│   │
│   └── Fixed Costs.xlsx
│       └── Alternative cost data
│
└── DOCUMENTATION
    ├── README.md
    ├── COST_STRUCTURE.md
    ├── OPTIMIZATION_GUIDE.md
    └── QUICK_REFERENCE.md (this file)
"""

# =============================================================================
# PARAMETERS EXPLANATION
# =============================================================================

"""
┌─────────────────────────────────────────────────────────────────────────┐
│                      KEY PARAMETERS & DEFAULTS                          │
└─────────────────────────────────────────────────────────────────────────┘

NETWORK CONFIGURATION (network_config)
──────────────────────────────────────
{
    'Manhattan': {
        'num_stations': int,      # Number of ambulance stations
        'num_als': int,           # Number of ALS vehicles
        'num_bls': int,           # Number of BLS vehicles
        'num_ptv': int,           # Number of PTV vehicles
    },
    # ... other boroughs
}


DEMAND POINTS (from research paper)
───────────────────────────────────
Each DemandPoint has:
- population: int
  ├─ Manhattan: 1,620,000
  ├─ Brooklyn: 2,600,000
  ├─ Queens: 2,330,000
  ├─ Bronx: 1,420,000
  └─ Staten Island: 480,000
  
- expected_delay: float (minutes)
  ├─ Manhattan: 4.5 min
  ├─ Brooklyn: 5.2 min
  ├─ Queens: 5.8 min
  ├─ Bronx: 5.1 min
  └─ Staten Island: 6.2 min


RESEARCH PAPER PARAMETERS (Su et al., 2015)
─────────────────────────────────────────────
- call_probability: 0.03
  └─ Probability of emergency call per person per year

- severe_probability: 0.07662
  └─ P(severe | call occurred)

- regular_probability: 0.92338
  └─ P(regular | call occurred)

- severe_cost_per_minute: $5,000
  └─ Cost impact per minute of delay for severe cases

- regular_cost_per_minute: $500
  └─ Cost impact per minute of delay for regular cases


RELOCATION PARAMETERS
─────────────────────
- relocation_cost_per_km: $120.0
  └─ Cost to relocate a vehicle per km

- avg_relocation_distance_km: ~7.5 km
  └─ Average distance within NYC


OPPORTUNITY COST PARAMETERS
────────────────────────────
- extra_response_time: 35 (minutes)
  └─ Additional response time penalty

- penalty_per_minute: $500
  └─ Cost per minute of extra response time


VEHICLE OPERATING PARAMETERS
─────────────────────────────
- avg_annual_miles: 45,000 miles/year
  └─ Expected annual vehicle usage

- amortization_years: 5 years
  └─ Capital cost amortization period
"""

# =============================================================================
# OUTPUT INTERPRETATION
# =============================================================================

"""
┌─────────────────────────────────────────────────────────────────────────┐
│                       HOW TO READ THE RESULTS                           │
└─────────────────────────────────────────────────────────────────────────┘

COST SUMMARY OUTPUT:
────────────────────
STATION COSTS:        Fixed facility costs (rent, utilities, parking)
VEHICLE COSTS:        Marginal cost of adding/removing vehicles
DELAY COST:           Impact of response time delays on patient outcomes
RELOCATION COST:      Cost of moving vehicles between stations
OPPORTUNITY COST:     Economic impact of slower response times

TOTAL ANNUAL COST:    Sum of all above = Network optimization objective


SCENARIO COMPARISON:
────────────────────
Baseline → Current network configuration
Optimized → Proposed network configuration

If Optimized Cost < Baseline Cost:
  ✓ Optimization is cost-effective
  
If Optimized Cost > Baseline Cost:
  ⚠ Optimization increases costs (but may improve response times)


BOROUGH-LEVEL ANALYSIS:
───────────────────────
Shows which boroughs contribute most to:
- Station costs (highest in Manhattan due to rent)
- Vehicle costs (highest in high-demand areas)
- Relocation costs (highest where repositioning occurs most)


PERCENTAGE BREAKDOWN:
─────────────────────
Typical breakdown:
- Vehicle Costs: 40-50% (largest component)
- Station Costs: 20-30%
- Delay Costs: 15-25% (depends on response times)
- Relocation Costs: 2-5%
- Opportunity Costs: 1-3%
"""

# =============================================================================
# COMMON ISSUES & TROUBLESHOOTING
# =============================================================================

"""
┌─────────────────────────────────────────────────────────────────────────┐
│                   TROUBLESHOOTING GUIDE                                 │
└─────────────────────────────────────────────────────────────────────────┘

ISSUE 1: "FileNotFoundError: relocation_actions.csv not found"
───────────────────────────────────────────────────────────────
SOLUTION: Ensure relocation_actions.csv is in the same directory as the script
          Or provide full path: pd.read_csv('/path/to/relocation_actions.csv')


ISSUE 2: Missing cost variables when initializing calculator
──────────────────────────────────────────────────────────────
SOLUTION: Ensure all X1-X139 variables are defined in borough_config
          Use create_borough_config() as template


ISSUE 3: Large difference between scenarios
─────────────────────────────────────────────
SOLUTION: Check if vehicle allocation is significantly different
          Higher vehicle counts → Higher costs
          May also reflect delay cost reductions


ISSUE 4: Negative costs showing up
────────────────────────────────────
SOLUTION: This is expected when comparing scenarios
          Negative = Savings, Positive = Additional cost


ISSUE 5: ValueError: "Borough 'X' not found"
─────────────────────────────────────────────
SOLUTION: Ensure borough names match exactly (case-sensitive)
          Valid: 'Manhattan', 'Brooklyn', 'Queens', 'Bronx', 'Staten Island'
          Invalid: 'MANHATTAN', 'manhattan', 'Staten'
"""

# =============================================================================
# NEXT STEPS
# =============================================================================

"""
┌─────────────────────────────────────────────────────────────────────────┐
│                           NEXT STEPS                                     │
└─────────────────────────────────────────────────────────────────────────┘

1. RUN THE TEST
   ─────────────
   python test_integrated_model.py
   
   This will produce results with real relocation data


2. ANALYZE RESULTS
   ────────────────
   - Compare baseline vs optimized costs
   - Identify which boroughs benefit most from optimization
   - Understand cost-response time trade-offs


3. FINE-TUNE PARAMETERS
   ───────────────────────
   - Adjust cost parameters based on actual NYC data
   - Update demand point populations/delays
   - Modify vehicle allocation strategy


4. SCENARIO MODELING
   ──────────────────
   - Test different network configurations
   - Analyze impact of adding/removing stations
   - Optimize for specific objectives (cost vs response time)


5. OPTIMIZATION INTEGRATION
   ──────────────────────────
   - Connect to optimization solver (scipy, gurobipy, etc.)
   - Auto-generate optimal network configuration
   - Produce sensitivity analysis
"""

# =============================================================================
# QUICK COMMANDS
# =============================================================================

"""
COMMAND REFERENCE:
──────────────────

1. Run test with relocation data:
   $ python test_integrated_model.py

2. Test specific borough costs:
   calculator.total_marginal_cost_annual('Manhattan', 'ALS', 50000, 38)

3. Compare vehicle types:
   model.compare_marginal_costs(45000, 38)

4. Get cost breakdown:
   results = model.total_cost()
   print(results['total_annual_network_cost'])

5. Export results to CSV:
   pd.DataFrame([results]).to_csv('results.csv')
"""

print(__doc__)
