# Ambulance Network Optimization - Cost Model

A comprehensive cost modeling framework for optimizing ambulance network placement across NYC's 5 boroughs (Manhattan, Brooklyn, Queens, Bronx, Staten Island).

## Project Overview

This project focuses on **minimizing response time and operating costs** by optimally placing three types of ambulance vehicles:
- **ALS** (Advanced Life Support)
- **BLS** (Basic Life Support)
- **PTV** (Patient Transport Vehicle)

## Key Features

### 1. **Marginal Cost Calculator**
Calculates the incremental cost of adding one additional vehicle of each type, considering:
- **Capital Costs**: Vehicle purchase, equipment, deployment setup
- **Operating Costs**: Fuel, maintenance, insurance, staffing
- **Facility Costs**: Station rent, utilities, dispatch center, administration

### 2. **Parameterized Cost Model**
All costs are represented as variables (X1, X2, ... X30) for easy updates when actual costs change:
- **X1-X3**: Vehicle purchase costs
- **X4-X6**: Equipment costs
- **X7**: Deployment setup cost
- **X8-X10**: Fuel costs per mile
- **X11-X13**: Maintenance costs
- **X14-X16**: Insurance costs
- **X17-X19**: Personnel salaries
- **X20-X22**: Crew sizes
- **X23-X30**: Facility and overhead costs

### 3. **Borough-Level Configuration**
Supports demand-driven vehicle placement across:
- Manhattan
- Brooklyn
- Queens
- Bronx
- Staten Island

## Core Formulas

### Marginal Capital Cost
```
For ALS: MC_Capital = X1 + X4 + X7
For BLS: MC_Capital = X2 + X5 + X7
For PTV: MC_Capital = X3 + X6 + X7
```

### Marginal Annual Operating Cost
```
MC_Operating = (Avg Annual Miles × Fuel/Mile) + Maintenance + Insurance + (Crew Size × Salary)
```

### Marginal Annual Facility Cost
```
MC_Facility = (Station Rent + Utilities) + (Shared Costs / Total Fleet Units)
```

### Total Annual Marginal Cost (5-year amortization)
```
Total = (Capital / 5) + Operating + Facility
```

## Project Structure

```
ambulance-network-optimization/
├── README.md                          # This file
├── cost_estimates.xlsx                # Your cost data (to be added)
├── marginal_cost_calculator.py        # Main calculator class
├── cost_model.py                      # Full network cost analysis
├── config/
│   └── cost_parameters.json           # Parameterized costs (auto-generated from xlsx)
└── examples/
    └── usage_examples.py              # Example calculations and scenarios
```

## Usage Example

```python
from marginal_cost_calculator import MarginalCostCalculator

# Initialize with cost parameters
cost_params = {...}  # From cost_estimates.xlsx
calculator = MarginalCostCalculator(cost_params)

# Calculate cost of adding 1 ALS vehicle to Manhattan
annual_cost = calculator.total_marginal_cost_annual(
    vehicle_type='ALS',
    avg_annual_miles=50000,
    current_total_fleet_units=38,
    amortization_years=5
)

print(f"Adding 1 ALS costs: ${annual_cost['total_annual']:,.2f}/year")

# Compare all vehicle types
comparison = calculator.compare_marginal_costs(45000, 38)
for vehicle_type, costs in comparison.items():
    print(f"{vehicle_type}: ${costs['total_annual']:,.2f}/year")
```

## Next Steps

1. **Add `cost_estimates.xlsx`** to this repository with your actual cost data
2. Script will automatically parse the Excel file and update cost parameters
3. Use marginal cost calculations for optimization algorithm
4. Integrate with response time metrics for placement decisions

## Cost Parameter Mapping

The Excel file should contain rows for each cost component and columns for ALS, BLS, and PTV:

| Cost Component | ALS | BLS | PTV |
|---|---|---|---|
| Vehicle Purchase Cost | X1 | X2 | X3 |
| Equipment Cost | X4 | X5 | X6 |
| Deployment Setup (per unit) | X7 | X7 | X7 |
| Fuel Cost (per mile) | X8 | X9 | X10 |
| Annual Maintenance | X11 | X12 | X13 |
| Annual Insurance | X14 | X15 | X16 |
| Annual Salary (per personnel) | X17 | X18 | X19 |
| Crew Size | X20 | X21 | X22 |

**Facility & Overhead Costs (Network-wide):**
- X23: Station Rent (per sqft, annually)
- X24-X26: Station Space Allocation (sqft per vehicle type)
- X27: Utilities (per station, annually)
- X28: Dispatch Center Cost (annual)
- X29: Administration Overhead (annual)
- X30: Medical Equipment Replacement (annual)

## Author

Created for NYC Ambulance Network Optimization Project

## License

MIT
