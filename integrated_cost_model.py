"""
===============================================================================
INTEGRATED COST MODEL
===============================================================================

This module integrates:
1. Comprehensive Marginal Cost Calculator (detailed NYC cost breakdown)
2. EMS Research Paper Model (Su et al., 2015 - network-level optimization)
3. Relocation Actions Data (real vehicle repositioning costs)

The hybrid model provides:
- Station Cost: Number of stations × detailed annual station cost
- Vehicle Cost: Vehicle marginal costs from comprehensive calculator
- Delay Cost: Research paper formula (Pcall × λ_i × a_i × penalty)
- Relocation Cost: Actual relocation distances from relocation_actions.csv
- Opportunity Cost: Extra response time penalties

Author: Aakriti-K
===============================================================================
"""

import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Optional
from comprehensive_cost_calculator import ComprehensiveMarginalCostCalculator


# =============================================================================
# Demand Point (from research paper)
# =============================================================================

@dataclass
class DemandPoint:
    """Represents one demand point with population and expected delay."""
    population: float
    expected_delay: float  # minutes


# =============================================================================
# Integrated Network Cost Model
# =============================================================================

class IntegratedCostModel:
    """
    Hybrid cost model combining comprehensive cost analysis with research 
    paper framework for network-level optimization.
    
    Structure:
    - Station Cost = num_stations × station_annual_cost (from comprehensive calc)
    - Vehicle Cost = sum(vehicle costs by type) with marginal cost approach
    - Delay Cost = Σ Pcall × λ_i × a_i × (Ps×Cs + Pr×Cr)  [Research paper formula]
    - Relocation Cost = Σ relocation_distances × cost_per_km
    - Opportunity Cost = extra_response_time × penalty_per_minute
    """

    def __init__(
        self,
        comprehensive_calculator: ComprehensiveMarginalCostCalculator,
        
        # Network Configuration
        network_config: Dict,  # {borough: {station_info, vehicle_allocation}}
        
        # Delay Cost Parameters (from research paper)
        demand_points: List[DemandPoint],
        call_probability: float,
        severe_probability: float,
        regular_probability: float,
        severe_cost_per_minute: float,
        regular_cost_per_minute: float,
        
        # Relocation Data
        relocation_df: Optional[pd.DataFrame] = None,
        relocation_cost_per_km: float = 120.0,
        
        # Opportunity Cost
        extra_response_time: float = 0.0,
        penalty_per_minute: float = 500.0,
        
        # Additional Parameters
        avg_annual_miles: float = 45000,
        amortization_years: int = 5
    ):
        """
        Initialize integrated cost model.
        
        Args:
            comprehensive_calculator: ComprehensiveMarginalCostCalculator instance
            network_config: Dict with borough-level network configuration
            demand_points: List of DemandPoint objects
            call_probability: P(call)
            severe_probability: P(severe | call)
            regular_probability: P(regular | call)
            severe_cost_per_minute: Cost per minute for severe cases
            regular_cost_per_minute: Cost per minute for regular cases
            relocation_df: DataFrame from relocation_actions.csv
            relocation_cost_per_km: Cost per km for vehicle relocation
            extra_response_time: Additional response time (minutes)
            penalty_per_minute: Penalty cost per minute of delay
            avg_annual_miles: Average annual miles per vehicle
            amortization_years: Capital amortization period
        """
        self.calculator = comprehensive_calculator
        self.network_config = network_config
        self.demand_points = demand_points
        
        self.call_probability = call_probability
        self.severe_probability = severe_probability
        self.regular_probability = regular_probability
        self.severe_cost_per_minute = severe_cost_per_minute
        self.regular_cost_per_minute = regular_cost_per_minute
        
        self.relocation_df = relocation_df
        self.relocation_cost_per_km = relocation_cost_per_km
        
        self.extra_response_time = extra_response_time
        self.penalty_per_minute = penalty_per_minute
        
        self.avg_annual_miles = avg_annual_miles
        self.amortization_years = amortization_years
        
        # Parse relocation data if provided
        self.relocation_costs_by_action = {}
        if relocation_df is not None:
            self._process_relocation_data()
    
    # =========================================================================
    # RELOCATION DATA PROCESSING
    # =========================================================================
    
    def _process_relocation_data(self):
        """
        Process relocation_actions.csv to calculate relocation costs.
        
        relocation_actions.csv structure:
        date, shift, shift_label, borough, IDA_id, r_in, r_out, net, 
        prev_units, new_units
        
        We use 'net' (net vehicles moved) to estimate relocation activity.
        """
        if self.relocation_df is None or self.relocation_df.empty:
            return
        
        # Calculate cost per relocation action
        # Assumption: each vehicle relocation covers ~5-10 km within NYC
        avg_relocation_distance_km = 7.5
        
        self.relocation_df['relocation_cost'] = (
            abs(self.relocation_df['net']) * 
            avg_relocation_distance_km * 
            self.relocation_cost_per_km
        )
        
        # Store by borough for breakdown analysis
        self.relocation_costs_by_borough = (
            self.relocation_df.groupby('borough')['relocation_cost'].sum()
        )
    
    # =========================================================================
    # STATION COST (from comprehensive calculator)
    # =========================================================================
    
    def station_cost(self) -> Dict[str, float]:
        """
        Calculate station costs using comprehensive cost breakdown.
        
        Formula:
        Station Cost = Σ_boroughs (num_stations × annual_station_cost)
        
        Returns:
            Dict with breakdown:
            {
                'manhattan': cost,
                'brooklyn': cost,
                ...
                'total': total_station_cost
            }
        """
        station_costs = {}
        total = 0
        
        for borough, config in self.network_config.items():
            num_stations = config.get('num_stations', 0)
            
            if num_stations > 0:
                station_annual = self.calculator.calculate_station_annual_cost(
                    borough
                )
                borough_station_cost = num_stations * station_annual['total_annual']
                station_costs[borough.lower()] = borough_station_cost
                total += borough_station_cost
        
        station_costs['total'] = total
        return station_costs
    
    # =========================================================================
    # VEHICLE COST (from comprehensive calculator with marginal approach)
    # =========================================================================
    
    def vehicle_cost(self) -> Dict[str, float]:
        """
        Calculate vehicle costs using comprehensive cost breakdown.
        
        Formula:
        Vehicle Cost = Σ_types Σ_boroughs (
            num_vehicles × (amortized_capital + annual_operating + staffing)
        )
        
        Returns:
            Dict with breakdown by vehicle type and borough
        """
        vehicle_costs = {
            'ALS': {},
            'BLS': {},
            'PTV': {},
            'total': 0
        }
        
        current_fleet_size = sum(
            config.get(f'num_{vtype.lower()}', 0)
            for config in self.network_config.values()
            for vtype in ['ALS', 'BLS', 'PTV']
        )
        
        for borough, config in self.network_config.items():
            for vehicle_type in ['ALS', 'BLS', 'PTV']:
                key = f'num_{vehicle_type.lower()}'
                num_vehicles = config.get(key, 0)
                
                if num_vehicles > 0:
                    # Get comprehensive annual cost per vehicle
                    marginal_cost = self.calculator.total_marginal_cost_annual(
                        borough=borough,
                        vehicle_type=vehicle_type,
                        avg_annual_miles=self.avg_annual_miles,
                        current_total_fleet_units=current_fleet_size,
                        amortization_years=self.amortization_years
                    )
                    
                    borough_vehicle_cost = (
                        num_vehicles * marginal_cost['total_annual_cost']
                    )
                    vehicle_costs[vehicle_type][borough.lower()] = (
                        borough_vehicle_cost
                    )
                    vehicle_costs['total'] += borough_vehicle_cost
        
        return vehicle_costs
    
    # =========================================================================
    # DELAY COST (from research paper)
    # =========================================================================
    
    def delay_cost(self) -> float:
        """
        Calculate network delay cost using research paper formula.
        
        Research Paper Formula:
        Delay Cost = Σ Pcall × λ_i × a_i × (Ps×Cs + Pr×Cr)
        
        Where:
        - Pcall: Probability of call per person per year
        - λ_i: Population at demand point i
        - a_i: Expected delay (minutes) at demand point i
        - Ps, Cs: Probability & cost per minute for severe cases
        - Pr, Cr: Probability & cost per minute for regular cases
        
        Returns:
            Total annual delay cost
        """
        total = 0.0
        
        # Combined penalty per minute
        penalty_per_minute = (
            self.severe_probability * self.severe_cost_per_minute +
            self.regular_probability * self.regular_cost_per_minute
        )
        
        # Sum across all demand points
        for point in self.demand_points:
            delay_cost_point = (
                self.call_probability *
                point.population *
                point.expected_delay *
                penalty_per_minute
            )
            total += delay_cost_point
        
        return total
    
    # =========================================================================
    # RELOCATION COST (from relocation_actions.csv)
    # =========================================================================
    
    def relocation_cost(self) -> Dict[str, float]:
        """
        Calculate relocation cost from actual repositioning data.
        
        Formula:
        Relocation Cost = Σ (|net_vehicles_moved| × avg_distance × cost_per_km)
        
        Returns:
            Dict with breakdown by borough and total
        """
        if not hasattr(self, 'relocation_costs_by_borough'):
            return {
                'by_borough': {},
                'total': 0.0
            }
        
        return {
            'by_borough': self.relocation_costs_by_borough.to_dict(),
            'total': self.relocation_costs_by_borough.sum()
        }
    
    # =========================================================================
    # OPPORTUNITY COST
    # =========================================================================
    
    def opportunity_cost(self) -> float:
        """
        Calculate opportunity cost from extra response time.
        
        Formula:
        Opportunity Cost = Extra Response Time × Penalty per Minute
        
        Returns:
            Total opportunity cost
        """
        return self.extra_response_time * self.penalty_per_minute
    
    # =========================================================================
    # TOTAL NETWORK COST
    # =========================================================================
    
    def total_cost(self) -> Dict[str, float]:
        """
        Calculate total network cost combining all components.
        
        Formula:
        Total Cost = Station Cost + Vehicle Cost + Delay Cost + 
                     Relocation Cost + Opportunity Cost
        
        Returns:
            Dict with complete cost breakdown
        """
        station_costs = self.station_cost()
        vehicle_costs = self.vehicle_cost()
        delay = self.delay_cost()
        relocation = self.relocation_cost()
        opportunity = self.opportunity_cost()
        
        total = (
            station_costs['total'] +
            vehicle_costs['total'] +
            delay +
            relocation['total'] +
            opportunity
        )
        
        return {
            'station_costs': station_costs,
            'vehicle_costs': vehicle_costs,
            'delay_cost': delay,
            'relocation_cost': relocation,
            'opportunity_cost': opportunity,
            'total_annual_network_cost': total
        }
    
    # =========================================================================
    # COST COMPARISON & ANALYSIS
    # =========================================================================
    
    def compare_scenarios(self, scenarios: Dict) -> Dict:
        """
        Compare costs across multiple network scenarios.
        
        Args:
            scenarios: Dict of {scenario_name: network_config}
        
        Returns:
            Dict with cost comparison across scenarios
        """
        results = {}
        
        for scenario_name, config in scenarios.items():
            # Create temporary model with this scenario
            temp_model = IntegratedCostModel(
                comprehensive_calculator=self.calculator,
                network_config=config,
                demand_points=self.demand_points,
                call_probability=self.call_probability,
                severe_probability=self.severe_probability,
                regular_probability=self.regular_probability,
                severe_cost_per_minute=self.severe_cost_per_minute,
                regular_cost_per_minute=self.regular_cost_per_minute,
                relocation_df=self.relocation_df,
                relocation_cost_per_km=self.relocation_cost_per_km,
                extra_response_time=self.extra_response_time,
                penalty_per_minute=self.penalty_per_minute,
                avg_annual_miles=self.avg_annual_miles,
                amortization_years=self.amortization_years
            )
            
            results[scenario_name] = temp_model.total_cost()
        
        return results
    
    # =========================================================================
    # REPORTING & VISUALIZATION
    # =========================================================================
    
    def print_cost_summary(self):
        """Print formatted cost breakdown."""
        total_costs = self.total_cost()
        
        print("\n" + "=" * 80)
        print("INTEGRATED EMS NETWORK COST MODEL")
        print("=" * 80)
        
        print("\n[STATION COSTS]")
        for borough, cost in total_costs['station_costs'].items():
            if borough != 'total':
                print(f"  {borough.title()}: ${cost:,.2f}")
        print(f"  {'─' * 70}")
        print(f"  Total Station Cost: ${total_costs['station_costs']['total']:,.2f}")
        
        print("\n[VEHICLE COSTS - By Type]")
        vehicle_by_type = {}
        for vtype in ['ALS', 'BLS', 'PTV']:
            vtype_cost = sum(
                total_costs['vehicle_costs'].get(vtype, {}).get(b, 0)
                for b in self.network_config.keys()
            )
            vehicle_by_type[vtype] = vtype_cost
            print(f"  {vtype}: ${vtype_cost:,.2f}")
        print(f"  {'─' * 70}")
        print(f"  Total Vehicle Cost: ${total_costs['vehicle_costs']['total']:,.2f}")
        
        print("\n[DELAY COST]")
        print(f"  Total Delay Cost: ${total_costs['delay_cost']:,.2f}")
        
        print("\n[RELOCATION COST]")
        for borough, cost in total_costs['relocation_cost']['by_borough'].items():
            print(f"  {borough.title()}: ${cost:,.2f}")
        print(f"  {'─' * 70}")
        print(f"  Total Relocation Cost: ${total_costs['relocation_cost']['total']:,.2f}")
        
        print("\n[OPPORTUNITY COST]")
        print(f"  Total Opportunity Cost: ${total_costs['opportunity_cost']:,.2f}")
        
        print("\n" + "=" * 80)
        print(f"TOTAL ANNUAL NETWORK COST: ${total_costs['total_annual_network_cost']:,.2f}")
        print("=" * 80 + "\n")
    
    def cost_breakdown_percentage(self) -> Dict[str, float]:
        """Return cost breakdown as percentages of total."""
        total_costs = self.total_cost()
        total = total_costs['total_annual_network_cost']
        
        return {
            'station_cost_pct': (total_costs['station_costs']['total'] / total) * 100,
            'vehicle_cost_pct': (total_costs['vehicle_costs']['total'] / total) * 100,
            'delay_cost_pct': (total_costs['delay_cost'] / total) * 100,
            'relocation_cost_pct': (total_costs['relocation_cost']['total'] / total) * 100,
            'opportunity_cost_pct': (total_costs['opportunity_cost'] / total) * 100
        }


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    
    print("✓ Integrated Cost Model initialized")
    print("✓ Ready to combine comprehensive costs with research paper framework")
    print("\nUsage:")
    print("  1. Initialize ComprehensiveMarginalCostCalculator with borough config")
    print("  2. Load relocation_actions.csv with pandas")
    print("  3. Define demand points and parameters from research paper")
    print("  4. Create IntegratedCostModel instance")
    print("  5. Call total_cost() for network-level analysis")
