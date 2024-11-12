import carla
import numpy as np
from scipy.optimize import minimize
import math

# Simulation parameters for energy consumption
rolling_coefficient = 0.01  # Approximate rolling coefficient
air_density = 1.225  # kg/m^3 at sea level
g = 9.81  # m/s^2
frontal_area = 2.22  # Approximate frontal area for a Tesla
drag_coefficient = 0.23  # Drag coefficient for Tesla Model 3
mass = 1847  # Approximate mass of Tesla Model 3 in kg
time_step = 0.1  # in seconds


class MPCController:
    def __init__(self, steps_ahead=10, dt=0.1):
        self.steps_ahead = steps_ahead
        self.dt = dt
        self.bounds = [(0, None)] * steps_ahead + [(0, 1)] * steps_ahead  # Acceleration >= 0, Throttle 0 to 1

    def objective(self, control_vars, init_state):
        cost = 0
        x, v, accel = init_state[0], init_state[1], 0

        for t in range(self.steps_ahead):
            accel = control_vars[t]  # Predicted acceleration
            throttle = control_vars[self.steps_ahead + t]  # Predicted throttle

            # Update the speed based on the current acceleration
            v += accel * self.dt
            F_total = calculate_forces(v, accel)
            power = F_total * v
            energy_cost = power * self.dt  # Fuel consumption cost

            # Penalty for very low speeds to encourage forward movement
            min_speed_penalty = 200 / max(v, 0.1)

            # Smooth throttle change penalty to prevent rapid changes
            throttle_change_cost = abs(throttle - (control_vars[self.steps_ahead + t - 1] if t > 0 else 0.5)) * 5

            cost += energy_cost + min_speed_penalty + throttle_change_cost

        return cost

    def control(self, vehicle):
        # Initial state (position, speed, acceleration) of the vehicle
        init_state = (vehicle.get_location().x, get_speed(vehicle), get_acceleration(vehicle))

        # Initial guess for control variables: moderate acceleration and throttle
        control_vars = [get_acceleration(vehicle) + 0.02] * self.steps_ahead + [vehicle.get_control().throttle+ 0.05] * self.steps_ahead

        # Run the optimization
        result = minimize(self.objective, control_vars, args=(init_state,), bounds=self.bounds, method='SLSQP')

        # Check optimization result
        if result.success:
            #print(f"Optimization Success: Cost={result.fun}, Throttle values={result.x[self.steps_ahead:self.steps_ahead*2]}")
            return result.x[self.steps_ahead]  # Return the first optimized throttle value
        else:
            #print(f"Optimization Failed: {result.message}")
            return 0.5



def get_speed(vehicle):
    velocity = vehicle.get_velocity()
    return math.sqrt(velocity.x**2 + velocity.y**2 + velocity.z**2)

def get_acceleration(vehicle):
    acceleration = vehicle.get_acceleration()
    return math.sqrt(acceleration.x**2 + acceleration.y**2 + acceleration.z**2)

# Define the set_perspective function
def set_perspective(vehicle, spectator):
    transform = carla.Transform(vehicle.get_transform().transform(carla.Location(x=5, z=1.6)), vehicle.get_transform().rotation)
    spectator.set_transform(transform)

def calculate_forces(speed, acceleration):
        F_mass = acceleration * mass
        F_rolling = 0.01 * mass * g
        F_air = 0.5 * air_density * frontal_area * drag_coefficient * speed**2
        F_total = F_mass + F_rolling + F_air
        return F_total    
