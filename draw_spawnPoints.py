import pickle
import carla
import argparse
import matplotlib.pyplot as plt
import random

# Define a class to store line data
class Line:
    x = []  # X-coordinates of the line
    y = []  # Y-coordinates of the line

# Class to handle map visualization in CARLA
class MapVisualization:
    def __init__(self, args):
        # Initialize CARLA client and map
        self.carla_client = carla.Client(args.host, args.port, worker_threads=1)
        self.world = self.carla_client.get_world()
        self.map = self.world.get_map()
        
        # Setup Matplotlib figure and axis
        self.fig, self.ax = plt.subplots()
        self.line_list = []  # List to store lines for visualization

    def destroy(self):
        # Clean up CARLA client and related resources
        self.carla_client = None
        self.world = None
        self.map = None

    @staticmethod
    def lateral_shift(transform, shift):
        """Makes a lateral shift of the forward vector of a transform."""
        transform.rotation.yaw += 90  # Rotate the yaw by 90 degrees
        return transform.location + shift * transform.get_forward_vector()

    def draw_line(self, points: list):
        """Draws a line on the map using the given points."""
        x = []
        y = []
        for p in points:
            x.append(p.x)  # Append X-coordinate
            y.append(-p.y)  # Append inverted Y-coordinate for correct orientation

        # Create a Line object and store coordinates
        line = Line()
        line.x = x
        line.y = y
        self.line_list.append(line)

        # Plot the line using Matplotlib
        self.ax.plot(x, y, color='darkslategrey', markersize=2)
        return True

    def draw_spawn_points(self, step=5):
        """Draws spawn points on the map."""
        spawn_points = self.map.get_spawn_points()
        
        # Only display every 'step'-th spawn point to avoid overlap
        for i in range(0, len(spawn_points), step):
            p = spawn_points[i]
            x = p.location.x  # X-coordinate of spawn point
            y = -p.location.y  # Inverted Y-coordinate for correct orientation
            
            # Add a small random offset to reduce overlap of text labels
            offset_x = random.uniform(-5, 5)
            offset_y = random.uniform(-5, 5)

            # Annotate spawn points with their indices
            self.ax.text(x + offset_x, y + offset_y, str(i),
                         fontsize=6,
                         color='darkorange',
                         va='center',
                         ha='center',
                         weight='bold')

    def draw_roads(self):
        """Draws road edges on the map."""
        precision = 0.1  # Precision for waypoints along the road
        topology = self.map.get_topology()  # Get road topology

        # Sort topology by Z-coordinate of their locations
        topology = [x[0] for x in topology]
        topology = sorted(topology, key=lambda w: w.transform.location.z)

        set_waypoints = []
        for waypoint in topology:
            waypoints = [waypoint]
            nxt = waypoint.next(precision)  # Get next waypoint with the specified precision
            if len(nxt) > 0:
                nxt = nxt[0]
                while nxt.road_id == waypoint.road_id:  # Continue until road ID changes
                    waypoints.append(nxt)
                    nxt = nxt.next(precision)
                    if len(nxt) > 0:
                        nxt = nxt[0]
                    else:
                        break
            set_waypoints.append(waypoints)

        # Draw the left and right sides of the roads
        for waypoints in set_waypoints:
            road_left_side = [self.lateral_shift(w.transform, -w.lane_width * 0.5) for w in waypoints]
            road_right_side = [self.lateral_shift(w.transform, w.lane_width * 0.5) for w in waypoints]

            if len(road_left_side) > 2:
                self.draw_line(points=road_left_side)  # Draw left side of the road
            if len(road_right_side) > 2:
                self.draw_line(points=road_right_side)  # Draw right side of the road

# Main function to run the map visualization
def main():
    # Parse command-line arguments
    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '--host',
        metavar='H',
        default='localhost',
        help='IP of the host CARLA Simulator (default: localhost)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port of CARLA Simulator (default: 2000)')
    argparser.add_argument(
        '-m', '--map',
        default='Town04',
        help='Load a new map to visualize')

    args = argparser.parse_args()

    # Initialize the map visualization
    viz = MapVisualization(args)

    # Draw roads and spawn points on the map
    viz.draw_roads()
    viz.draw_spawn_points(step=10)  # Display every 10th spawn point (adjust step as needed)

    # Clean up visualization resources
    viz.destroy()
    
    # Adjust plot to have equal axis scaling
    plt.axis('equal')

    # Save map visualization information to a pickle file
    with open('/tmp/map_info.pkl', 'wb') as pickle_file:
        pickle.dump(viz.line_list, pickle_file)

    # Display the plot
    plt.show()

# Execute the script
if __name__ == "__main__":
    main()
