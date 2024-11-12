# MPC-Controller

This `MPCController` class implements a Model Predictive Control (MPC) algorithm designed to optimize vehicle throttle and acceleration over a prediction horizon in a simulation environment, such as CARLA. The goal of this controller is to balance energy-efficient driving with smooth throttle transitions, maintaining fuel efficiency while avoiding abrupt speed changes.

### Key Features:
- **Prediction Horizon**: Controls vehicle behavior over `steps_ahead` steps, using the time interval `dt`.
- **Constraints**: Enforces non-negative acceleration and throttle values between 0 and 1.
- **Cost Function**:
  - Minimizes **fuel consumption** by calculating total energy cost based on vehicle speed and total force exerted on the vehicle.
  - Adds a **minimum speed penalty** to encourage forward motion.
  - Smoothes throttle changes with a **penalty on throttle adjustments** to ensure gradual acceleration or deceleration, promoting stable vehicle dynamics.

### Control Loop:
1. **Objective Function**: The `objective` method computes a cost function using predicted vehicle acceleration and throttle values. The total cost is a sum of fuel consumption, minimum speed penalty, and throttle change penalty.
2. **Optimize Control Inputs**: The `control` method takes the initial state of the vehicle (position, speed, acceleration) and runs optimization with an initial guess. The `SLSQP` method is used to minimize the objective function within the specified bounds.
3. **Throttle Command**: If optimization is successful, the controller returns the first predicted throttle value to guide the vehicle in the current timestep.
