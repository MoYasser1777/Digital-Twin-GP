import pandas as pd
import matplotlib.pyplot as plt
import configparser
import os

class Vehicle:
    def __init__(self, excel_file):
        # Load the Excel file into a DataFrame
        self.data = pd.read_excel(excel_file)
        self.time_index = 0  # Start at the first row

    def update(self):
        # Move to the next row in the DataFrame (simulate a time step)
        if self.time_index < len(self.data) - 1:
            self.time_index += 1

    def get_speed(self):
        return self.data.iloc[self.time_index]["Speed (m/s)"]

    def get_acceleration(self):
        return self.data.iloc[self.time_index]["Acceleration (m/s^2)"]

    def get_throttle(self):
        return self.data.iloc[self.time_index]["Throttle"]

    def get_braking(self):
        return self.data.iloc[self.time_index]["Braking"]

    def get_steering(self):
        return self.data.iloc[self.time_index]["Steering"]

    def get_time(self):
        return self.data.iloc[self.time_index]["Time"]

def calculate_forces(velocity, acceleration, parameters):
    F_mass = acceleration * parameters["mass"]
    F_rolling = 0.01 * parameters["mass"] * parameters["g"]
    F_air = 0.5 * parameters["air_density"] * parameters["frontal_area"] * parameters["drag_coefficient"] *velocity**2
    F_total = F_mass + F_rolling + F_air
    return F_total    

def read_config_file():
    # Load configuration from INI file
    config = configparser.ConfigParser()
    config.read("config.ini")

    # Convert the section into a dictionary
    parameters = {key: float(value) for key, value in config["simulation_parameters"].items()}
    return parameters

def save_graph(time_values, original_throttle_values, predicted_throttle_values, filename="throttle_comparison.png"):
    # Create the outputs folder if it doesn't exist
    output_directory = "outputs"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Created directory: {output_directory}")
    
    # Plotting the curves
    plt.figure(figsize=(10, 6))
    plt.plot(time_values, predicted_throttle_values, label="Predicted Throttle", color="blue")
    plt.plot(time_values, original_throttle_values, label="Original Throttle", color="orange", linestyle="--")
    plt.xlabel("Time (s)")
    plt.ylabel("Throttle")
    plt.title("Predicted Throttle vs Original Throttle")
    plt.legend()
    plt.grid(True)

    # Save the plot in the outputs directory
    save_path = os.path.join(output_directory, filename)
    plt.savefig(save_path, dpi=300)  # Save with high resolution (300 DPI)
    plt.close()  # Close the figure to free memory

    print(f"Graph saved as: {save_path}")
    return


def save_predicted_throttle_to_excel(time_values, predicted_throttle_values, filename="predicted_throttle.xlsx"):
    # Create the outputs folder if it doesn't exist
    output_directory = "outputs"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        print(f"Created directory: {output_directory}")
    
    # Create a DataFrame with the time and throttle values
    data = {
        "Time (s)": time_values,
        "Predicted Throttle": predicted_throttle_values,
    }
    
    df = pd.DataFrame(data)

    # Save the DataFrame to an Excel file in the outputs directory
    save_path = os.path.join(output_directory, filename)
    df.to_excel(save_path, index=False)

    print(f"Predicted throttle values saved to: {save_path}")
    return