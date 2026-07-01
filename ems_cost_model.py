"""
===============================================================================
EMS COST MODEL
===============================================================================

Research Paper:
Su, Q., Luo, Q., & Huang, S.H.
"Cost-effective Analyses for Emergency Medical Services Deployment:
A Case Study in Shanghai"
International Journal of Production Economics, 2015.

This implementation reproduces the cost model proposed in the paper
and extends it with:

1. Relocation Cost
2. Opportunity Cost

Author:
(Modify as needed)

===============================================================================
"""

from dataclasses import dataclass
from typing import List


# =============================================================================
# Demand Point
# =============================================================================

@dataclass
class DemandPoint:
    """
    Represents one demand point.

    population             -> λ_i
    expected_delay         -> a_i (minutes)
    """

    population: float
    expected_delay: float


# =============================================================================
# EMS Cost Model
# =============================================================================

class EMSCostModel:

    def __init__(

        self,

        # -----------------------------
        # Network
        # -----------------------------
        num_stations: int,
        num_vehicles: int,

        # -----------------------------
        # Annual Costs
        # -----------------------------
        station_cost_per_year: float,
        vehicle_cost_per_year: float,

        # -----------------------------
        # Delay Cost Parameters
        # -----------------------------
        call_probability: float,
        severe_probability: float,
        regular_probability: float,

        severe_cost_per_minute: float,
        regular_cost_per_minute: float,

        demand_points: List[DemandPoint],

        # -----------------------------
        # Relocation
        # -----------------------------
        relocation_distance_km: float = 0,
        relocation_cost_per_km: float = 0,

        # -----------------------------
        # Opportunity Cost
        # -----------------------------
        extra_response_time: float = 0,
        penalty_per_minute: float = 0

    ):

        self.num_stations = num_stations
        self.num_vehicles = num_vehicles

        self.station_cost_per_year = station_cost_per_year
        self.vehicle_cost_per_year = vehicle_cost_per_year

        self.call_probability = call_probability
        self.severe_probability = severe_probability
        self.regular_probability = regular_probability

        self.severe_cost_per_minute = severe_cost_per_minute
        self.regular_cost_per_minute = regular_cost_per_minute

        self.demand_points = demand_points

        self.relocation_distance_km = relocation_distance_km
        self.relocation_cost_per_km = relocation_cost_per_km

        self.extra_response_time = extra_response_time
        self.penalty_per_minute = penalty_per_minute

    # =========================================================================
    # STATION COST
    # =========================================================================

    def station_cost(self):
        """
        Research Paper

        Station Cost =
            Number of Stations × Annual Cost per Station
        """

        return self.num_stations * self.station_cost_per_year

    # =========================================================================
    # VEHICLE COST
    # =========================================================================

    def vehicle_cost(self):
        """
        Research Paper

        Vehicle Cost =
            Number of Vehicles × Annual Cost per Vehicle
        """

        return self.num_vehicles * self.vehicle_cost_per_year

    # =========================================================================
    # DELAY COST
    # =========================================================================

    def delay_cost(self):
        """
        Research Paper Formula

        Delay Cost

        Σ Pcall × λ_i × a_i ×
        ( Ps×Cs + Pr×Cr )
        """

        total = 0

        penalty = (

            self.severe_probability * self.severe_cost_per_minute +

            self.regular_probability * self.regular_cost_per_minute

        )

        for point in self.demand_points:

            total += (

                self.call_probability *

                point.population *

                point.expected_delay *

                penalty

            )

        return total

    # =========================================================================
    # RELOCATION COST
    # =========================================================================

    def relocation_cost(self):
        """
        Proposed Extension

        Relocation Cost =
            Distance Moved × Cost per km
        """

        return (

            self.relocation_distance_km *

            self.relocation_cost_per_km

        )

    # =========================================================================
    # OPPORTUNITY COST
    # =========================================================================

    def opportunity_cost(self):
        """
        Proposed Extension

        Opportunity Cost =
            Extra Response Time × Penalty per Minute
        """

        return (

            self.extra_response_time *

            self.penalty_per_minute

        )

    # =========================================================================
    # TOTAL COST
    # =========================================================================

    def total_cost(self):

        return (

            self.station_cost()

            + self.vehicle_cost()

            + self.delay_cost()

            + self.relocation_cost()

            + self.opportunity_cost()

        )

    # =========================================================================
    # COST BREAKDOWN
    # =========================================================================

    def summary(self):

        print("=" * 60)

        print("EMS COST MODEL SUMMARY")

        print("=" * 60)

        print(f"Station Cost       : {self.station_cost():,.2f}")

        print(f"Vehicle Cost       : {self.vehicle_cost():,.2f}")

        print(f"Delay Cost         : {self.delay_cost():,.2f}")

        print(f"Relocation Cost    : {self.relocation_cost():,.2f}")

        print(f"Opportunity Cost   : {self.opportunity_cost():,.2f}")

        print("-" * 60)

        print(f"TOTAL NETWORK COST : {self.total_cost():,.2f}")

        print("=" * 60)

'''
# =============================================================================
# Example
# =============================================================================

if __name__ == "__main__":

    demand_points = [

        DemandPoint(

            population=12000,

            expected_delay=3.2

        ),

        DemandPoint(

            population=18000,

            expected_delay=4.1

        ),

        DemandPoint(

            population=22000,

            expected_delay=2.7

        ),

    ]

    model = EMSCostModel(

        # Network
        num_stations=35,
        num_vehicles=63,

        # Costs
        station_cost_per_year=150000,
        vehicle_cost_per_year=400000,

        # Delay Parameters
        call_probability=0.03,

        severe_probability=0.07662,
        regular_probability=0.92338,

        severe_cost_per_minute=5000,
        regular_cost_per_minute=500,

        demand_points=demand_points,

        # Relocation
        relocation_distance_km=18,
        relocation_cost_per_km=120,

        # Opportunity Cost
        extra_response_time=35,
        penalty_per_minute=500

    )

    model.summary()
'''