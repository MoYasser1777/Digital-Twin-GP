import traci
import csv
import os
import math
import pandas as pd

# Simulation parameters for energy consumption for Nissan Patrol 2021
rolling_coefficient = 0.01  # Approximate rolling coefficient
air_density = 1.225  # kg/m^3 at sea level
g = 9.81  # m/s^2
drag_coefficient = 0.3

# Constants for CMEM model 
eta = 0.45  # Indicated efficiency
b1 = 1e-4   # Coefficient
C = 0.00125 # Coefficient
LHV = 43.2  # Lower heating value of diesel fuel in kJ/g
K0 = 1  # Default value, could be adjusted based on real data

# Define your SUMO configuration file and port
SUMO_BINARY = "sumo-gui"  
CONFIG_FILE = "examples/Town04.sumocfg"  
REMOTE_PORT = 8813  # Port for TraCI connection
TIME_STEP = "0.05"

# Define the vehicle ID you want to track 
VEHICLE_ID = "0"  # ID of the vehicle to track

# Output CSV file
OUTPUT_FILE = "vehicle_data.csv"


def calculate_power(speed, acceleration,mass,frontal_area):

    F_mass = acceleration * mass
    F_rolling = rolling_coefficient * mass * g
    F_air = 0.5 * air_density * frontal_area * drag_coefficient * speed**2
    F_total = F_mass + F_rolling + F_air
    power = (F_total * speed)/1000

    return power   

def calculate_fuel_rate(P, N= 0.035, V=3.6):
    """
    Calculate fuel use rate in mg per 0.05 seconds using CMEM model.

    Parameters:
    P : float  -> Engine power output in kW
    N : float  -> Engine speed in revolutions per second
    V : float  -> Engine displacement in liters

    Returns:
    fuel_rate_per_timestep : float  -> Fuel consumption in mg per timestep
    """

    N0 = 30 * math.sqrt(3.0 / V)

    K = K0 * (1 + C * (N - N0))

    FR = (K * N * V + (P / eta)) * (1 / LHV) * (1 + b1 * (N - N0)**2) # (g/s)

    # Convert to mg per time_step
    fuel_rate_per_timestep = FR * 1000 * float(TIME_STEP)  # mg/tiemstep

    return fuel_rate_per_timestep        

# Function to run the simulation and collect data
def run_sumo_and_collect_data():

    flag = False
    # Start SUMO with the TraCI server
    traci.start([SUMO_BINARY, "-c", CONFIG_FILE, "--step-length", TIME_STEP])
    print(f"Starting SUMO with command: {[SUMO_BINARY, '-c', CONFIG_FILE]}")
    print("Connected to SUMO...")

    # Open the CSV file for writing
    with open(OUTPUT_FILE, mode="w", newline="") as file:
        writer = csv.writer(file)
        # Write the header row
        writer.writerow(["Step", "Speed (m/s)", "Acceleration (m/s^2)", "Fuel HBEFA (mg)","Fuel CMEM (mg)"])
        mass = traci.vehicle.getMass(VEHICLE_ID)
        frontal_area = traci.vehicle.getWidth(VEHICLE_ID) * traci.vehicle.getHeight(VEHICLE_ID)
        step = 0
        try:
            # Run the simulation
            while traci.simulation.getMinExpectedNumber() > 0:
                traci.simulationStep()  # Advance the simulation by one step

                # Check if the vehicle exists in the simulation
                if VEHICLE_ID in traci.vehicle.getIDList():
                    # Collect data for the vehicle
                    flag = True
                    speed = round(traci.vehicle.getSpeed(VEHICLE_ID), 3)
                    acceleration = round(traci.vehicle.getAcceleration(VEHICLE_ID), 3)
                    fuel_HBEFA= round(traci.vehicle.getFuelConsumption(VEHICLE_ID),3) * float(TIME_STEP)

                    power = calculate_power(speed,acceleration,mass,frontal_area)

                    fuel_CMEM = calculate_fuel_rate(power)

                    # Write the data to the CSV file
                    writer.writerow([step, speed, acceleration,fuel_HBEFA,fuel_CMEM])
                else:
                    print(f"Step {step}: Vehicle {VEHICLE_ID} is not in simulation right now.")
                    if(flag):
                        break
                    

                step += 1
        except KeyboardInterrupt:
            print("Simulation interrupted by user.")
        finally:
            # Close the connection and clean up
            traci.close()
            print(f"Simulation finished. Data saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    # Ensure SUMO_HOME is set correctly
    if "SUMO_HOME" not in os.environ:
        print("Error: SUMO_HOME environment variable is not set.")
        print("Set SUMO_HOME to the directory where SUMO is installed.")
    else:
        run_sumo_and_collect_data()
