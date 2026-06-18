"""
Marginal Cost Calculator for Ambulance Network
Calculates the incremental cost of adding one additional vehicle of each type
"""

from typing import Dict


class MarginalCostCalculator:
    """
    Calculates the incremental (marginal) cost of adding one additional vehicle
    to the ambulance network. This is essential for optimization algorithms that
    determine optimal vehicle placement based on cost-response time trade-offs.
    """
    
    def __init__(self, cost_params: Dict[str, float]):
        """
        Initialize with cost parameters.
        
        Args:
            cost_params: Dictionary containing all cost parameters (X1, X2, ... X30)
        """
        self.cost_params = cost_params
    
    # ==================== MARGINAL CAPITAL COST ====================
    
    def marginal_capital_cost(self, vehicle_type: str) -> float:
        """
        Calculate the one-time capital cost of adding one additional vehicle.
        
        Formula:
        Marginal Capital Cost = Vehicle Purchase + Equipment + Deployment Setup
        
        For ALS: MC_Capital = X1 + X4 + X7
        For BLS: MC_Capital = X2 + X5 + X7
        For PTV: MC_Capital = X3 + X6 + X7
        
        Args:
            vehicle_type: 'ALS', 'BLS', or 'PTV'
        
        Returns:
            One-time capital cost for one additional vehicle
        """
        capital_map = {
            'ALS': ('X1_als_vehicle', 'X4_als_equipment'),
            'BLS': ('X2_bls_vehicle', 'X5_bls_equipment'),
            'PTV': ('X3_ptv_vehicle', 'X6_ptv_equipment')
        }
        
        vehicle_key, equipment_key = capital_map[vehicle_type]
        vehicle_cost = self.cost_params.get(vehicle_key, 0)
        equipment_cost = self.cost_params.get(equipment_key, 0)
        deployment_cost = self.cost_params.get('X7_deployment_setup', 0)
        
        return vehicle_cost + equipment_cost + deployment_cost
    
    # ==================== MARGINAL ANNUAL OPERATING COST ====================
    
    def marginal_annual_operating_cost(self, 
                                       vehicle_type: str, 
                                       avg_annual_miles: float) -> float:
        """
        Calculate the annual operating cost of adding one additional vehicle.
        
        Formula:
        MC_Operating = (Avg Annual Miles × Fuel Per Mile) + Maintenance + Insurance + Staffing
        
        Where Staffing Cost = Crew Size × Annual Salary
        
        Args:
            vehicle_type: 'ALS', 'BLS', or 'PTV'
            avg_annual_miles: Expected annual miles for this vehicle (borough-dependent)
        
        Returns:
            Annual operating cost for one additional vehicle
        
        Example:
            If ALS vehicle travels 50,000 miles/year:
            MC_Operating = (50,000 × 0.12) + 8,000 + 12,000 + (2 × 65,000)
                         = 6,000 + 8,000 + 12,000 + 130,000
                         = $156,000/year
        """
        operating_map = {
            'ALS': {
                'fuel': 'X8_als_fuel_per_mile',
                'maintenance': 'X11_als_maintenance_annual',
                'insurance': 'X14_als_insurance_annual',
                'salary': 'X17_als_paramedic_salary',
                'crew_size': 'X20_als_crew_size'
            },
            'BLS': {
                'fuel': 'X9_bls_fuel_per_mile',
                'maintenance': 'X12_bls_maintenance_annual',
                'insurance': 'X15_bls_insurance_annual',
                'salary': 'X18_bls_emt_salary',
                'crew_size': 'X21_bls_crew_size'
            },
            'PTV': {
                'fuel': 'X10_ptv_fuel_per_mile',
                'maintenance': 'X13_ptv_maintenance_annual',
                'insurance': 'X16_ptv_insurance_annual',
                'salary': 'X19_ptv_driver_salary',
                'crew_size': 'X22_ptv_crew_size'
            }
        }
        
        params = operating_map[vehicle_type]
        fuel_per_mile = self.cost_params.get(params['fuel'], 0)
        maintenance = self.cost_params.get(params['maintenance'], 0)
        insurance = self.cost_params.get(params['insurance'], 0)
        salary = self.cost_params.get(params['salary'], 0)
        crew_size = self.cost_params.get(params['crew_size'], 1)
        
        fuel_cost = avg_annual_miles * fuel_per_mile
        staffing_cost = crew_size * salary
        
        return fuel_cost + maintenance + insurance + staffing_cost
    
    # ==================== MARGINAL ANNUAL FACILITY COST ====================
    
    def marginal_annual_facility_cost(self, 
                                      vehicle_type: str,
                                      current_total_fleet_units: int,
                                      num_stations: int = 1) -> float:
        """
        Calculate the annual facility cost of adding one additional vehicle.
        
        This includes:
        1. Proportional share of station costs (rent + utilities)
        2. Proportional share of shared facility costs (dispatch, admin, equipment)
        
        Formula:
        MC_Facility = (Station Rent + Utilities) + (Shared Costs / Total Fleet Units)
        
        Where:
        - Station Rent = Sqft Allocation × Rent Per Sqft
        - Shared Costs = Dispatch Center + Administration + Medical Equipment Replacement
        
        Args:
            vehicle_type: 'ALS', 'BLS', or 'PTV'
            current_total_fleet_units: Current total vehicles in network (for shared cost allocation)
            num_stations: Number of stations where this new vehicle will be added (default 1)
        
        Returns:
            Annual facility cost for one additional vehicle
        
        Example:
            If adding 1 ALS to 38-unit network with 1 station:
            MC_Facility = (2000 × 25) + 15,000 + (250,000 + 500,000 + 100,000) / 39
                        = 50,000 + 15,000 + 20,512.82
                        = $85,512.82/year
        """
        facility_map = {
            'ALS': 'X24_als_station_sqft',
            'BLS': 'X25_bls_station_sqft',
            'PTV': 'X26_ptv_station_sqft'
        }
        
        rent_per_sqft = self.cost_params.get('X23_station_rent_per_sqft', 0)
        sqft_allocation = self.cost_params.get(facility_map[vehicle_type], 0)
        utilities_per_station = self.cost_params.get('X27_utilities_per_station', 0)
        dispatch_cost = self.cost_params.get('X28_dispatch_center_cost', 0)
        admin_overhead = self.cost_params.get('X29_admin_overhead', 0)
        med_equip_replacement = self.cost_params.get('X30_med_equipment_replacement', 0)
        
        # Direct facility costs (station-specific)
        rent_cost = num_stations * sqft_allocation * rent_per_sqft
        utilities_cost = num_stations * utilities_per_station
        direct_facility_cost = rent_cost + utilities_cost
        
        # Shared facility costs allocated per vehicle
        total_shared_cost = dispatch_cost + admin_overhead + med_equip_replacement
        new_total_units = current_total_fleet_units + 1
        shared_cost_per_vehicle = total_shared_cost / new_total_units
        
        return direct_facility_cost + shared_cost_per_vehicle
    
    # ==================== TOTAL MARGINAL COST ====================
    
    def total_marginal_cost_annual(self, 
                                   vehicle_type: str, 
                                   avg_annual_miles: float,
                                   current_total_fleet_units: int,
                                   amortization_years: int = 5) -> Dict[str, float]:
        """
        Calculate total annual marginal cost (amortized capital + annual operating + facility).
        
        Formula:
        Total Marginal Cost = (Capital Cost / Amortization Years) + Operating Cost + Facility Cost
        
        Args:
            vehicle_type: 'ALS', 'BLS', or 'PTV'
            avg_annual_miles: Expected annual miles for this vehicle
            current_total_fleet_units: Current total vehicles in network
            amortization_years: Years to amortize capital cost (default 5)
        
        Returns:
            Dictionary with cost breakdown:
            {
                'capital_amortized': annual amortized capital cost,
                'operating': annual operating cost,
                'facility': annual facility cost,
                'total_annual': total annual marginal cost
            }
        
        Example:
            Adding 1 ALS with 5-year amortization:
            {
                'capital_amortized': $39,000 (= 195,000 / 5)
                'operating': $156,000,
                'facility': $85,513,
                'total_annual': $280,513
            }
        """
        capital_cost = self.marginal_capital_cost(vehicle_type)
        amortized_capital = capital_cost / amortization_years
        
        operating_cost = self.marginal_annual_operating_cost(vehicle_type, avg_annual_miles)
        
        facility_cost = self.marginal_annual_facility_cost(vehicle_type, 
                                                          current_total_fleet_units)
        
        total_annual = amortized_capital + operating_cost + facility_cost
        
        return {
            'capital_amortized': amortized_capital,
            'operating': operating_cost,
            'facility': facility_cost,
            'total_annual': total_annual,
            'vehicle_type': vehicle_type
        }
    
    def total_marginal_cost_5year(self, 
                                  vehicle_type: str,
                                  avg_annual_miles: float,
                                  current_total_fleet_units: int,
                                  horizon_years: int = 5) -> Dict[str, float]:
        """
        Calculate total marginal cost over a 5-year (or custom) horizon.
        
        Formula:
        5-Year Total Cost = Capital Cost + (Annual Cost × Years)
        
        Args:
            vehicle_type: 'ALS', 'BLS', or 'PTV'
            avg_annual_miles: Expected annual miles
            current_total_fleet_units: Current total vehicles
            horizon_years: Time horizon (default 5)
        
        Returns:
            Dictionary with costs and cost per year
        """
        capital_cost = self.marginal_capital_cost(vehicle_type)
        operating_cost = self.marginal_annual_operating_cost(vehicle_type, avg_annual_miles)
        facility_cost = self.marginal_annual_facility_cost(vehicle_type, 
                                                          current_total_fleet_units)
        
        annual_cost = operating_cost + facility_cost
        total_cost_horizon = capital_cost + (annual_cost * horizon_years)
        
        return {
            'capital': capital_cost,
            'operating_annual': operating_cost,
            'facility_annual': facility_cost,
            'annual_total': annual_cost,
            f'total_{horizon_years}year': total_cost_horizon,
            'cost_per_year': total_cost_horizon / horizon_years,
            'vehicle_type': vehicle_type,
            'horizon_years': horizon_years
        }
    
    # ==================== COMPARISON & ANALYSIS ====================
    
    def compare_marginal_costs(self, 
                               avg_annual_miles: float,
                               current_total_fleet_units: int,
                               amortization_years: int = 5) -> Dict:
        """
        Compare marginal costs across all three vehicle types.
        
        Useful for determining which vehicle type to add to minimize cost
        while meeting response time requirements.
        
        Args:
            avg_annual_miles: Average annual miles per vehicle
            current_total_fleet_units: Current total vehicles
            amortization_years: Amortization period
        
        Returns:
            Dictionary with marginal costs for ALS, BLS, PTV
        """
        return {
            'ALS': self.total_marginal_cost_annual('ALS', avg_annual_miles, 
                                                   current_total_fleet_units, 
                                                   amortization_years),
            'BLS': self.total_marginal_cost_annual('BLS', avg_annual_miles, 
                                                   current_total_fleet_units, 
                                                   amortization_years),
            'PTV': self.total_marginal_cost_annual('PTV', avg_annual_miles, 
                                                   current_total_fleet_units, 
                                                   amortization_years)
        }
    
    def cost_per_response_metric(self,
                                 vehicle_type: str,
                                 avg_annual_miles: float,
                                 current_total_fleet_units: int,
                                 expected_calls_per_year: float) -> float:
        """
        Calculate marginal cost per expected call/response for a vehicle type.
        
        Useful for cost-effectiveness analysis when combined with response time metrics.
        
        Args:
            vehicle_type: 'ALS', 'BLS', or 'PTV'
            avg_annual_miles: Expected annual miles
            current_total_fleet_units: Current total vehicles
            expected_calls_per_year: Expected number of calls/responses per year
        
        Returns:
            Annual cost per expected call
        """
        annual_cost = self.total_marginal_cost_annual(
            vehicle_type, 
            avg_annual_miles, 
            current_total_fleet_units
        )
        return annual_cost['total_annual'] / max(expected_calls_per_year, 1)
    
    def print_marginal_cost_summary(self, 
                                    vehicle_type: str,
                                    avg_annual_miles: float,
                                    current_total_fleet_units: int,
                                    expected_calls_per_year: float = None):
        """Print formatted marginal cost analysis"""
        print(f"\n{'='*70}")
        print(f"MARGINAL COST ANALYSIS: Adding 1 {vehicle_type} Vehicle")
        print(f"{'='*70}")
        
        annual_cost = self.total_marginal_cost_annual(vehicle_type, 
                                                      avg_annual_miles, 
                                                      current_total_fleet_units)
        
        print(f"\nCost Breakdown (Annual):")
        print(f"  Capital (amortized over 5 years): ${annual_cost['capital_amortized']:,.2f}")
        print(f"  Operating Costs: ${annual_cost['operating']:,.2f}")
        print(f"  Facility Costs: ${annual_cost['facility']:,.2f}")
        print(f"  {'─'*50}")
        print(f"  TOTAL ANNUAL COST: ${annual_cost['total_annual']:,.2f}")
        
        if expected_calls_per_year:
            cost_per_call = self.cost_per_response_metric(vehicle_type, 
                                                         avg_annual_miles,
                                                         current_total_fleet_units,
                                                         expected_calls_per_year)
            print(f"\nCost Effectiveness:")
            print(f"  Expected Calls/Year: {expected_calls_per_year:,.0f}")
            print(f"  Cost per Call: ${cost_per_call:,.2f}")
        
        print(f"\n{'='*70}\n")


# ==================== EXAMPLE USAGE ====================

if __name__ == "__main__":
    # Cost parameters (same as in main cost_model.py)
    cost_params = {
        'X1_als_vehicle': 150000,
        'X2_bls_vehicle': 120000,
        'X3_ptv_vehicle': 85000,
        'X4_als_equipment': 45000,
        'X5_bls_equipment': 30000,
        'X6_ptv_equipment': 20000,
        'X7_deployment_setup': 5000,
        'X8_als_fuel_per_mile': 0.12,
        'X9_bls_fuel_per_mile': 0.11,
        'X10_ptv_fuel_per_mile': 0.10,
        'X11_als_maintenance_annual': 8000,
        'X12_bls_maintenance_annual': 6500,
        'X13_ptv_maintenance_annual': 5000,
        'X14_als_insurance_annual': 12000,
        'X15_bls_insurance_annual': 10000,
        'X16_ptv_insurance_annual': 8000,
        'X17_als_paramedic_salary': 65000,
        'X18_bls_emt_salary': 55000,
        'X19_ptv_driver_salary': 45000,
        'X20_als_crew_size': 2,
        'X21_bls_crew_size': 2,
        'X22_ptv_crew_size': 1,
        'X23_station_rent_per_sqft': 25,
        'X24_als_station_sqft': 2000,
        'X25_bls_station_sqft': 1500,
        'X26_ptv_station_sqft': 1000,
        'X27_utilities_per_station': 15000,
        'X28_dispatch_center_cost': 250000,
        'X29_admin_overhead': 500000,
        'X30_med_equipment_replacement': 100000
    }
    
    calculator = MarginalCostCalculator(cost_params)
    
    # Example 1: Marginal cost of adding 1 ALS to current 38-unit network
    print("\n### EXAMPLE 1: Adding ALS to Manhattan (50,000 miles/year) ###")
    calc = calculator.total_marginal_cost_annual('ALS', 50000, current_total_fleet_units=38)
    calculator.print_marginal_cost_summary('ALS', 50000, 38, expected_calls_per_year=8000)
    
    # Example 2: Compare costs across vehicle types
    print("\n### EXAMPLE 2: Comparing All Vehicle Types ###")
    comparison = calculator.compare_marginal_costs(45000, current_total_fleet_units=38)
    for vehicle_type, costs in comparison.items():
        print(f"\n{vehicle_type}: ${costs['total_annual']:,.2f}/year")
    
    # Example 3: 5-year cost horizon
    print("\n### EXAMPLE 3: 5-Year Cost Horizon ###")
    five_year = calculator.total_marginal_cost_5year('BLS', 45000, 38, horizon_years=5)
    print(f"Adding 1 BLS Unit (5-year horizon):")
    print(f"  Capital Cost: ${five_year['capital']:,.2f}")
    print(f"  Operating (annual): ${five_year['operating_annual']:,.2f}")
    print(f"  Facility (annual): ${five_year['facility_annual']:,.2f}")
    print(f"  Total 5-Year Cost: ${five_year['total_5year']:,.2f}")
    print(f"  Average Cost/Year: ${five_year['cost_per_year']:,.2f}")
