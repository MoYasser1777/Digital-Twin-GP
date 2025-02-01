import traci
import csv
import os
import math
import pandas as pd

# Simulation parameters for energy consumption for Nissan Patrol 2021
rolling_coefficient = 0.015  # Approximate rolling coefficient
air_density = 1.225  # kg/m^3 at sea level
g = 9.81  # m/s^2
frontal_area = 2.55  # Approximate frontal area 
drag_coefficient = 0.025
mass = 2300

# Define your SUMO configuration file and port
SUMO_BINARY = "sumo-gui"  
CONFIG_FILE = "examples/Town04.sumocfg"  
REMOTE_PORT = 8813  # Port for TraCI connection
TIME_STEP = "0.1"

# Define the vehicle ID you want to track 
VEHICLE_ID = "20"  # ID of the vehicle to track

# Output CSV file
OUTPUT_FILE = "vehicle_data.csv"

def calculate_energy(speed, acceleration):
        F_mass = acceleration * mass
        F_rolling = rolling_coefficient * mass * g
        F_air = 0.5 * air_density * frontal_area * drag_coefficient * speed**2
        F_total = F_mass + F_rolling + F_air
        power = F_total * speed
        energy_consumed = round(power * float(TIME_STEP), 3)   

        return energy_consumed

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
        writer.writerow(["Step", "Vehicle ID", "Speed (m/s)", "Position (x, y)", "Acceleration (m/s^2)", "Fuel Consumption (mg per timestep)","Energy(J)"])

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
                    position = tuple(round(coord, 3) for coord in traci.vehicle.getPosition(VEHICLE_ID))  # (x, y)
                    acceleration = round(traci.vehicle.getAcceleration(VEHICLE_ID), 3)
                    fuel= round(traci.vehicle.getFuelConsumption(VEHICLE_ID),3) * float(TIME_STEP)

                    energy = calculate_energy(speed,acceleration)

                    # Write the data to the CSV file
                    writer.writerow([step, VEHICLE_ID, speed, position, acceleration,fuel,energy])
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
