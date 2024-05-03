"""
R = L / tan(steering_angle)
Circle Center = (-R, 0)

Obstacle = (rsin(theta), rcos(theta))

Angle from center to obstacle = tan(O_y / (O_x + R))
Dist from center to obstacle = sqrt((O_x + R)^2 + O_y^2)

Circum dist to obstacle = R * angle from center to obstacle
Time to hit obstacle = circum dist to obstacle / velocity
"""
import math
import matplotlib.pyplot as plt

VEHICLE_LENGTH = .3
VEHICLE_WIDTH = 0.25
AUTOBRAKE_TIME = 1 # .45
AUTOBRAKE_DISTANCE = .5

MIN_COLLISIONS_FOR_BRAKE = 1
LIDAR_HORIZONTAL_OFFSET = .035

steering_angle = -math.pi/7
velocity = 1

class LidarScan:
    def __init__(self, angle_min, angle_max, angle_increment, ranges):
        self.angle_min = angle_min
        self.angle_max = angle_max
        self.angle_increment = angle_increment
        self.ranges = ranges

def find_obstacles(data: LidarScan):
    global steering_angle
    invert_flag = 1

    if steering_angle < 0:
        invert_flag = -1

    turning_radius = VEHICLE_LENGTH / math.tan(invert_flag * steering_angle) if abs(steering_angle) > .01 else float('inf')
    if turning_radius == float('inf'):
        for i in range(len(data.ranges)):
            theta = (data.angle_min + i * data.angle_increment)
            r = data.ranges[i]
            x = r * math.sin(theta)
            y = r * math.cos(theta)

            if abs(x) < VEHICLE_WIDTH/2:
                dist_to_obstacle = y
                time_to_hit = dist_to_obstacle / velocity
                print(dist_to_obstacle, time_to_hit)
                if dist_to_obstacle <= AUTOBRAKE_DISTANCE or time_to_hit <= AUTOBRAKE_TIME:
                    print(f"Obstacle at ({x}, {y})")

    else:
        left_wheel_radius = turning_radius - VEHICLE_WIDTH/2
        right_wheel_radius = turning_radius + VEHICLE_WIDTH/2

        for i in range(len(data.ranges)):
            theta = (data.angle_min + i * data.angle_increment)
            r = data.ranges[i]
            x = invert_flag * (r * math.sin(theta))
            y = r * math.cos(theta)

            dist_to_obstacle = math.sqrt((x + turning_radius)**2 + y**2)

            # print("OBSTACLE: ", invert_flag * x, y)
            # print(dist_to_obstacle)

            if right_wheel_radius < dist_to_obstacle < left_wheel_radius or left_wheel_radius < dist_to_obstacle < right_wheel_radius:
                print(f"Obstacle in path at ({invert_flag * x}, {y})")

                # print(turning_radius)

                angle_from_center_to_obstacle = math.atan2(y, turning_radius + x)

                if angle_from_center_to_obstacle < 0:
                    angle_from_center_to_obstacle += 2 * math.pi
                
                angle_from_center_to_obstacle %= 2 * math.pi

                print(math.degrees(angle_from_center_to_obstacle))

                circum_dist_to_obstacle = turning_radius * angle_from_center_to_obstacle
                time_to_hit = circum_dist_to_obstacle / velocity

                print(circum_dist_to_obstacle, time_to_hit)

                if circum_dist_to_obstacle <= AUTOBRAKE_DISTANCE or time_to_hit <= AUTOBRAKE_TIME:
                    print(f"Obstacle at ({invert_flag * x}, {y})")


data = LidarScan(-math.pi/2, math.pi/2, math.pi/10, [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1])

find_obstacles(data)

# Plot the lidar data and add the circle
fig, ax = plt.subplots()
x = []
y = []
for i in range(len(data.ranges)):
    theta = (data.angle_min + i * data.angle_increment)
    r = data.ranges[i]
    x.append(r * math.sin(theta))
    y.append(r * math.cos(theta))
    ax.scatter(x, y)

# Add a point at the origin
ax.scatter(0, 0)

# Set aspect ratio to be equal, ensuring square boundaries
ax.set_aspect('equal', adjustable='box')

# PLOT DATA
if abs(steering_angle) > .01:
    turning_radius = VEHICLE_LENGTH / math.tan(steering_angle)
    bigger_radius = turning_radius + VEHICLE_WIDTH/2
    smaller_radius = turning_radius - VEHICLE_WIDTH/2

    circle_center = (-turning_radius, 0)

    # Add the circle
    # ax.add_patch(plt.Circle(circle_center, turning_radius, color='r', fill=False))
    ax.add_patch(plt.Circle(circle_center, bigger_radius, color='b', fill=False))
    ax.add_patch(plt.Circle(circle_center, smaller_radius, color='b', fill=False))
else:
    center = (0, 0)
    left = (-VEHICLE_WIDTH/2, 0)
    right = (VEHICLE_WIDTH/2, 0)

    # Add lines for the vehicle at x = -VEHICLE_WIDTH/2 and x = VEHICLE_WIDTH/2
    ax.axvline(x=-VEHICLE_WIDTH/2, color='g', linestyle='--')
    ax.axvline(x=VEHICLE_WIDTH/2, color='g', linestyle='--')

# Show the plot
plt.show()

