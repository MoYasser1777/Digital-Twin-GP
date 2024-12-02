from scipy.optimize import minimize
from utils import *

class MPCController:
    def __init__(self, parameters, steps_ahead=10, dt=0.1):
        self.steps_ahead = steps_ahead
        self.dt = dt
        print(parameters["mass"])
        self.bounds = [(parameters["max_deceleration"], parameters["max_acceleration"])] * steps_ahead + [(0, 1)] * steps_ahead  # Acceleration >= 0, Throttle 0 to 1
        self.parameters = parameters

    def objective(self, control_vars, init_state):
        cost = 0
        v, accel = init_state[0], init_state[1]  # Initial speed and acceleration

        total_distance = 0  # Total distance traveled (in meters)

        for t in range(self.steps_ahead):
            accel = control_vars[t]  # Predicted acceleration
            throttle = control_vars[self.steps_ahead + t]  # Predicted throttle

            # Update speed using acceleration and calculate distance
            v += accel * self.dt
            distance = v * self.dt  # Calculate distance traveled in this step
            total_distance += distance  # Add to total distance

            F_total = calculate_forces(v, accel, self.parameters)
            power = F_total * v
            energy_cost = power * self.dt  # Energy consumption

            # Penalty for very low speeds
            min_speed_penalty = 50 / max(v, 0.1)

            # Throttle change penalty
            throttle_change_cost = abs(throttle - (control_vars[self.steps_ahead + t - 1] if t > 0 else 0.5)) * 2

            # Add costs for this distance
            cost += energy_cost + min_speed_penalty + throttle_change_cost

        # Normalize the total cost by the distance traveled to get cost per distance
        cost_per_distance = cost / total_distance
        return cost_per_distance


    def control(self, vehicle):
        # Initial state (speed, acceleration) from the Vehicle class
        init_state = (vehicle.get_speed(), vehicle.get_acceleration())

        # Initial guess for control variables: moderate acceleration and throttle
        control_vars = [vehicle.get_acceleration() + 0.02] * self.steps_ahead + [vehicle.get_throttle() + 0.05] * self.steps_ahead

        # Run the optimization
        result = minimize(self.objective, control_vars, args=(init_state,), bounds=self.bounds, method='SLSQP')

        # Check optimization result
        if result.success:
            return result.x[self.steps_ahead]  # Return the first optimized throttle value
        else:
            return 0.5