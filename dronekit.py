import cv2
import numpy as np
import time
from dronekit import connect, VehicleMode
from pymavlink import mavutil

# Connect to the Vehicle (Pixhawk)
connection_string = '/dev/ttyUSB0'  # Change to your connection string
baud_rate = 57600
vehicle = connect(connection_string, baud=baud_rate, wait_ready=True)

# Initialize camera
cap = cv2.VideoCapture("libcamerasrc ! video/x-raw,width=640,height=480,framerate=30/1 ! videoconvert ! appsink", cv2.CAP_GSTREAMER)

def send_ned_velocity(vehicle, velocity_x, velocity_y, velocity_z, duration):
    """
    Move vehicle in direction based on specified velocity vectors.
    """
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0, 0, 0, mavutil.mavlink.MAV_FRAME_LOCAL_NED,
        0b0000111111000111, 0, 0, 0,
        velocity_x, velocity_y, velocity_z,
        0, 0, 0, 0, 0)
    vehicle.send_mavlink(msg)
    vehicle.flush()

def drone_movement(quadrant, region):
    vx, vy, vz = 0, 0, 0
    if region == "Not Bounded":
        if quadrant == "Top-right":
            vy = 0.1  # move top
            vx = 0.1  # move right
        elif quadrant == "Top-left":
            vy = 0.1  # move up
            vx = -0.1 # move left
        elif quadrant == "Bottom-right":
            vy = -0.1 # move down
            vx = 0.1  # move right
        elif quadrant == "Bottom-left":
            vy = -0.1 # move down
            vx = -0.1 # move left
    else:
        vz = -0.1  # land

    send_ned_velocity(vehicle, vx, vy, vz, 1)

def detection():
    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            print("Failed to capture frame. Exiting...")
            break

        # Convert the frame to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply GaussianBlur to reduce noise and improve contour detection
        blurred_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)

        # Apply Canny edge detection
        edges = cv2.Canny(blurred_frame, 50, 150)

        # Find contours in the edges
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Initialize variables to store information about the chosen landing pad
        max_contour = None
        max_contour_area = 0

        for contour in contours:
            # Filter contours based on area or other criteria to identify the landing pad
            contour_area = cv2.contourArea(contour)
            if contour_area > 1000 and contour_area > max_contour_area:
                max_contour = contour
                max_contour_area = contour_area

        if max_contour is not None:
            # Calculate the centroid of the landing pad
            M = cv2.moments(max_contour)
            if M["m00"] != 0:  # Ensure m00 is not zero before calculating centroid
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])

                # Determine quadrant
                if cx < frame.shape[1] / 2 and cy < frame.shape[0] / 2:
                    quadrant = "Top-left"
                elif cx >= frame.shape[1] / 2 and cy < frame.shape[0] / 2:
                    quadrant = "Top-right"
                elif cx < frame.shape[1] / 2 and cy >= frame.shape[0] / 2:
                    quadrant = "Bottom-left"
                else:
                    quadrant = "Bottom-right"

                # Draw the contour and quadrant on the frame
                cv2.drawContours(frame, [max_contour], -1, (0, 255, 0), 2)
                cv2.putText(frame, quadrant, (cx - 50, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                # Check if the object is within the reduced square region
                region_top_left = (frame.shape[1] // 3, frame.shape[0] // 3)
                region_bottom_right = (2 * frame.shape[1] // 3, 2 * frame.shape[0] // 3)

                if region_top_left[0] <= cx <= region_bottom_right[0] and \
                        region_top_left[1] <= cy <= region_bottom_right[1]:
                    cv2.rectangle(frame, region_top_left, region_bottom_right, (0, 0, 255), 2)
                    region_status = "Bounded"
                else:
                    region_status = "Not Bounded"

                drone_movement(quadrant, region_status)

        # Display the result
        cv2.imshow("Landing Pad", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
            break

    # Release video capture and close all windows
    cap.release()
    cv2.destroyAllWindows()

# Example of arming and taking off
vehicle.mode = VehicleMode("GUIDED")
vehicle.armed = True
while not vehicle.armed:
    time.sleep(1)

vehicle.simple_takeoff(5)  # Take off to 5 meters

detection()  # Start detection and landing process

# Close vehicle object before exiting script
vehicle.close()

