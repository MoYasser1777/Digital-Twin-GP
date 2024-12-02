from utils import *
from MPC_Controller import *

def main():  
    parameters = read_config_file()

    # Add storage for predicted and original throttle values
    predicted_throttle_values = []
    original_throttle_values = []
    time_values = []

    # Load the vehicle data from Excel
    vehicle_data = Vehicle("vehicle_energy_data_automatic_control.xlsx")  # Replace with the actual file name
    controller = MPCController(parameters ,steps_ahead=10, dt=0.1)

    for _ in range(len(vehicle_data.data)):
        # Get the predicted throttle
        predicted_throttle = controller.control(vehicle_data)

        # Append the values to the lists for plotting later
        predicted_throttle_values.append(predicted_throttle)
        original_throttle_values.append(vehicle_data.get_throttle())
        time_values.append(vehicle_data.get_time())

        # Print the predicted throttle for debugging
        print(f"Time: {vehicle_data.get_time():.2f}, Predicted Throttle: {predicted_throttle:.2f}")

        # Update to the next time step
        vehicle_data.update()

    save_graph(time_values,original_throttle_values,predicted_throttle_values,"throttle_comparison.png")
    save_predicted_throttle_to_excel(time_values,predicted_throttle_values,"predicted_throttle.xlsx")
    return


main()