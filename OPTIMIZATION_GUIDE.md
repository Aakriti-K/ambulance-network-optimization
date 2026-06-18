# Ambulance Network Optimization Algorithm - Complete Guide

## 1. WHAT IS AN OPTIMIZATION ALGORITHM FOR AMBULANCE NETWORKS?

An optimization algorithm is a computational method that determines the **optimal placement of ambulances** across NYC's 5 boroughs to achieve competing objectives:
- **Minimize response time** (primary goal: save lives)
- **Minimize operating costs** (secondary goal: budget efficiency)

It answers questions like:
- Where should we place 38 ambulances to cover all 5 boroughs?
- How many ALS vs BLS vs PTV units in each location?
- Which station locations minimize average response time?
- At what cost can we achieve <10 minute response time citywide?

---

## 2. KEY COMPONENTS OF THE OPTIMIZATION PROBLEM

### A. **Decision Variables**
Variables the algorithm must decide:
```
For each borough × vehicle type:
  x[borough][vehicle_type] = number of units to deploy
  
Example:
  x['Manhattan']['ALS'] = 8
  x['Manhattan']['BLS'] = 5
  x['Manhattan']['PTV'] = 3
  ... (repeat for all boroughs)
```

### B. **Objective Function** (What we're optimizing)

**Multi-objective optimization:**
```
Minimize: Cost = Σ(marginal_cost_per_unit × units_deployed)
          Response_Time = Σ(weighted_response_time)

Or weighted combination:
Minimize: α × (Cost) + β × (Response_Time)
Where α, β are weights (α + β = 1)
```

**Example:**
- 70% weight on response time (life-safety critical)
- 30% weight on cost (budget constraint)

### C. **Constraints** (Limitations we must respect)

1. **Total fleet size constraint:**
   ```
   Σ(all units deployed) ≤ 38 units (or whatever budget allows)
   ```

2. **Response time constraint:**
   ```
   Response_time[borough] ≤ 10 minutes (SLA)
   ```

3. **Coverage constraint:**
   ```
   Every location in borough must be within X miles of nearest ambulance
   ```

4. **Capacity constraint:**
   ```
   Each station can house max Y vehicles (physical space limit)
   ```

5. **Demand constraint:**
   ```
   Units deployed ≥ expected call volume (e.g., if borough has 2000 calls/month,
   need enough units to handle concurrent calls)
   ```

---

## 3. TYPES OF OPTIMIZATION ALGORITHMS

### **Type 1: Exact Algorithms** (Guaranteed optimal solution)

#### **Integer Linear Programming (ILP)**
```
Minimize: Cost × x + ResponseTime × y
Subject to: Constraints
x, y are integers (can't have 2.5 ambulances!)

Tools: 
- Python: PuLP, Pyomo, CVXPY
- Commercial: CPLEX, Gurobi
- Open-source: CBC, SCIP
```

**Pros:** Guaranteed optimal solution
**Cons:** Slow for large problems (can take hours/days)
**Use case:** 5 boroughs, 3 vehicle types = manageable

---

#### **Constraint Programming (CP)**
```
Define constraints explicitly, solver finds feasible solution

Example:
  - Manhattan must have ≥ 8 ALS units
  - Total cost ≤ $5M/year
  - Response time ≤ 10 min in 90% of calls
```

**Tools:** OR-Tools (Google), IBM ILOG CPLEX
**Pros:** Handles complex constraints naturally
**Cons:** Still slow for large problems

---

### **Type 2: Heuristic Algorithms** (Good solutions, not guaranteed optimal)

#### **Greedy Algorithm**
```
Start with no vehicles
While budget available:
  Add the vehicle (type + location) that gives best improvement
  in response time per dollar spent
```

**Pros:** Fast, simple to implement
**Cons:** May miss better solutions
**Use case:** Quick initial solution

---

#### **Genetic Algorithm (GA)**
```
1. Create random population of solutions (e.g., 100 random deployments)
2. Evaluate fitness (cost × response time)
3. Keep best solutions (selection)
4. Create new solutions by mixing best ones (crossover)
5. Randomly mutate some solutions (exploration)
6. Repeat until convergence
```

**Pros:** Good for complex problems, finds near-optimal
**Cons:** Slower, requires tuning
**Use case:** When exact algorithm is too slow

---

#### **Simulated Annealing**
```
1. Start with current solution
2. Randomly move to nearby solution
3. Accept if better, or with probability p if worse
4. Gradually decrease probability (cool down)
5. Eventually converge to good solution
```

**Pros:** Escapes local optima
**Cons:** Needs parameter tuning
**Use case:** When stuck in local optima

---

#### **Tabu Search**
```
1. Start with current solution
2. Find best neighboring solution (even if worse)
3. Keep tabu list (forbidden moves) to avoid cycles
4. Continue until stopping criteria
```

**Pros:** Efficient, good for medium problems
**Cons:** Complex to implement
**Use case:** Practical commercial applications

---

### **Type 3: Hybrid Algorithms**

**Combine exact + heuristic:**
```
1. Use heuristic to get initial solution quickly
2. Use exact method to optimize locally
3. Switch between methods based on time/quality trade-off
```

---

## 4. RECOMMENDED APPROACH FOR YOUR PROBLEM

### **Problem Characteristics:**
- **Small-medium size:** 5 boroughs × 3 vehicle types = 15 decision variables (manageable!)
- **Geographic component:** Response time depends on location
- **Multiple objectives:** Cost vs. response time trade-off
- **Real-world constraints:** Station capacity, demand, coverage

### **Recommended Solution: Integer Linear Programming (ILP)**

```
Why ILP?
✓ Problem is small enough (15 variables is trivial for ILP)
✓ Guaranteed optimal solution
✓ Can handle multiple objectives
✓ Constraint-friendly
✓ Mature tools available (PuLP)
```

### **Hybrid Approach (Recommended):**
```
1. ILP for base optimization (exact solution)
2. Sensitivity analysis (how does cost change with fleet size?)
3. Pareto front (trade-off curve: response time vs. cost)
4. Decision-maker chooses preferred solution
```

---

## 5. STEP-BY-STEP IMPLEMENTATION

### **Step 1: Gather Data Needed**

```python
# Geographic data
borough_locations = {
    'Manhattan': {'lat': 40.7831, 'lon': -73.9712, 'area_sqft': 500000},
    'Brooklyn': {...},
    # ... all 5 boroughs
}

# Response time matrix
# travel_time[from_station][to_location] (in minutes)
# Build using Google Maps API or GIS data
travel_times = {
    'Manhattan_Station_1': {
        'location_1': 5.2,
        'location_2': 6.8,
        ...
    }
}

# Demand data
demand = {
    'Manhattan': 8000,  # calls/year
    'Brooklyn': 7500,
    'Queens': 6200,
    'Bronx': 5800,
    'Staten_Island': 2500
}

# Station data
stations = {
    'Manhattan_Station_1': {'capacity': 10, 'rent': 250000},
    'Manhattan_Station_2': {'capacity': 8, 'rent': 200000},
    ...
}

# Cost data (from your comprehensive calculator)
marginal_cost = {
    ('Manhattan', 'ALS'): 280513,
    ('Manhattan', 'BLS'): 245600,
    ...
}
```

---

### **Step 2: Define the Optimization Model**

```python
from pulp import *

# Decision variables
# x[borough][vehicle_type] = number of units
x = {}
for borough in boroughs:
    for vehicle_type in ['ALS', 'BLS', 'PTV']:
        x[(borough, vehicle_type)] = LpVariable(
            f"units_{borough}_{vehicle_type}",
            lowBound=0,
            cat='Integer'
        )

# Objective function: Minimize total annual cost
prob = LpProblem("Ambulance_Network_Optimization", LpMinimize)

prob += lpSum([
    marginal_cost[(borough, vtype)] * x[(borough, vtype)]
    for borough in boroughs
    for vtype in ['ALS', 'BLS', 'PTV']
]), "Total_Cost"

# Alternative: Weighted objective (cost + response time)
# prob += 0.3 * cost_objective + 0.7 * response_time_objective

# Constraints
# 1. Total fleet size
prob += lpSum([x[(b, v)] for b in boroughs for v in vehicle_types]) <= 38

# 2. Borough demand coverage
for borough in boroughs:
    prob += x[(borough, 'ALS')] + x[(borough, 'BLS')] + x[(borough, 'PTV')] >= \
            min_units_per_borough[borough]

# 3. Response time constraint
# (more complex: depends on locations and travel times)
for borough in boroughs:
    prob += expected_response_time(x, borough) <= 10  # minutes

# 4. Station capacity
for station in stations:
    borough = get_borough(station)
    prob += x[(borough, 'ALS')] + x[(borough, 'BLS')] + x[(borough, 'PTV')] <= \
            stations[station]['capacity']

# Solve
prob.solve(PULP_CBC_CMD())

# Results
print(f"Status: {LpStatus[prob.status]}")
print(f"Total Cost: ${value(prob.objective):,.2f}/year")
for borough in boroughs:
    for vtype in vehicle_types:
        print(f"{borough} - {vtype}: {x[(borough, vtype)].varValue} units")
```

---

## 6. RESPONSE TIME MODELING

### **Key Challenge:** How to model response time?

#### **Approach 1: Distance-based (Simple)**
```
Response_time ≈ avg_distance_to_nearest_ambulance / avg_speed
             = avg_distance / 20 mph

For complete coverage, need:
  max_distance_to_any_location ≤ 10 miles
```

#### **Approach 2: Call-demand weighted (Better)**
```
For each location in borough:
  - Count expected calls
  - Find nearest ambulance(s)
  - Calculate travel time (using real road network)
  
avg_response_time[borough] = 
    Σ(calls_at_location × travel_time_to_nearest_ambulance) / total_calls
```

#### **Approach 3: Queue-based (Realistic)**
```
When ambulance is busy:
  - Call gets routed to 2nd nearest ambulance
  - Response time includes dispatch + travel
  
Probability ambulance is available depends on:
  - Call volume
  - Average call duration
  - Number of ambulances (Erlang C formula)
```

**Formula: Erlang C**
```
P_wait = (A^N / N!) / Σ(A^i / i! for i=0 to N-1) * (N/(N-A))

Where:
  A = call volume × avg_call_duration (traffic intensity)
  N = number of ambulances
  P_wait = probability a call must wait
```

---

## 7. MULTI-OBJECTIVE OPTIMIZATION (Cost vs Response Time)

### **Problem:** Can't minimize both simultaneously!
- More units = better response time, higher cost
- Fewer units = lower cost, worse response time

### **Solution: Pareto Optimization**

```
1. For each possible fleet size (10, 15, 20, ..., 38 units):
   - Find best deployment (min response time)
   - Calculate cost
   
2. Plot: Response Time (y-axis) vs Cost (x-axis)

3. Result: Pareto front (trade-off curve)
   - No solution is better in both dimensions
   - Decision-maker picks preferred trade-off

Example output:
Fleet Size | Avg Response | Annual Cost | Notes
-----------|-------------|------------|--------
   10      |   18 min    |  $3.5M     | Minimal coverage
   15      |   14 min    |  $5.2M     |
   20      |   10 min    |  $7.1M     | Acceptable
   25      |    8 min    |  $8.8M     | Good coverage
   30      |    6 min    |  $10.5M    | Excellent
   38      |    5 min    |  $13.4M    | Maximum resources
```

---

## 8. VALIDATION & SENSITIVITY ANALYSIS

### **Is the solution realistic?**

```python
# 1. Check constraints are satisfied
assert sum(all_units) <= 38
assert all(response_time[b] <= 10 for b in boroughs)
assert all(station_load <= station_capacity)

# 2. Sensitivity analysis: How sensitive is solution to changes?
for factor in [0.8, 0.9, 1.0, 1.1, 1.2]:
    # Increase costs by 20%, see if solution changes
    new_cost = marginal_cost * factor
    new_solution = optimize(new_cost, constraints)
    
# 3. What if demand increases by 20%?
new_demand = demand * 1.2
new_solution = optimize(cost, constraints_with_new_demand)

# 4. What if one station closes?
new_constraints = remove_station('Manhattan_Station_1')
new_solution = optimize(cost, new_constraints)
```

---

## 9. IMPLEMENTATION ROADMAP

### **Phase 1: Data Collection (Weeks 1-2)**
- [ ] Get borough boundaries & locations
- [ ] Collect call volume data per location
- [ ] Build travel time matrix (Google Maps API)
- [ ] List potential station locations
- [ ] Extract costs from Excel (use parser script)

### **Phase 2: Basic Model (Weeks 3-4)**
- [ ] Implement simple ILP model (distance-based coverage)
- [ ] Run optimization
- [ ] Validate results against current deployment
- [ ] Calculate baseline cost & response time

### **Phase 3: Enhanced Model (Weeks 5-6)**
- [ ] Add realistic response time calculation (queue-based)
- [ ] Implement multi-objective optimization
- [ ] Generate Pareto front
- [ ] Sensitivity analysis

### **Phase 4: Refinement (Weeks 7-8)**
- [ ] Add constraints for specific scenarios
- [ ] Optimize for specific boroughs
- [ ] Create interactive dashboard
- [ ] Prepare for stakeholder review

---

## 10. TOOLS & LIBRARIES

### **Python Libraries**

```python
# Optimization
pip install pulp                    # ILP modeling
pip install pyomo                   # Advanced optimization
pip install cvxpy                   # Convex optimization
pip install deap                    # Genetic algorithms

# Data & Analysis
pip install pandas numpy scipy      # Data handling
pip install geopandas               # Geographic data
pip install folium                  # Maps visualization

# APIs
pip install googlemaps              # Travel time data
pip install arcgis                  # GIS data

# Visualization
pip install matplotlib seaborn      # Plotting
pip install plotly                  # Interactive plots
pip install streamlit               # Dashboard
```

---

## 11. SIMPLE EXAMPLE: Greedy Algorithm

```python
def greedy_optimization(boroughs, marginal_costs, response_times, budget):
    """
    Simple greedy algorithm: repeatedly add the unit that gives
    best response time improvement per dollar
    """
    deployment = {b: {'ALS': 0, 'BLS': 0, 'PTV': 0} for b in boroughs}
    total_cost = 0
    total_units = 0
    
    while total_units < 38:
        best_move = None
        best_efficiency = 0
        
        # Try each possible addition
        for borough in boroughs:
            for vehicle_type in ['ALS', 'BLS', 'PTV']:
                # Cost of adding one unit
                cost = marginal_costs[(borough, vehicle_type)]
                
                # Response time improvement
                improvement = response_time_improvement(
                    deployment, borough, vehicle_type
                )
                
                # Efficiency: improvement per dollar
                efficiency = improvement / cost
                
                if efficiency > best_efficiency:
                    best_efficiency = efficiency
                    best_move = (borough, vehicle_type)
        
        if best_move is None:
            break  # No more beneficial additions
        
        # Add best unit
        borough, vtype = best_move
        deployment[borough][vtype] += 1
        total_cost += marginal_costs[best_move]
        total_units += 1
    
    return deployment, total_cost
```

---

## 12. NEXT STEPS FOR YOUR PROJECT

1. **Choose algorithm type:**
   - Start with **ILP** (small problem, guaranteed optimal)
   - Later try **genetic algorithm** if needed

2. **Gather geographic data:**
   - NYC borough shapefiles
   - Current station locations
   - Call volume heat maps

3. **Build travel time matrix:**
   - Use Google Maps Distance Matrix API
   - Create time-distance lookup table

4. **Implement basic model:**
   - Start with Python + PuLP
   - Minimize cost with response time constraints

5. **Validate & iterate:**
   - Compare to current deployment
   - Adjust weights, constraints, add real-world factors

---

**Would you like me to:**
1. Create a sample ILP implementation for your problem?
2. Build a data collection script?
3. Create a visualization dashboard?
4. Implement a specific algorithm in detail?

Let me know what's most helpful! 🚀
