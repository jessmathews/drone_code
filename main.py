import cv2
import numpy as np
import sys

# Load the image
image = cv2.imread('dronelanding.jpg', cv2.IMREAD_COLOR)

# Convert the image to HSV color space
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Define the color range for the landing pad (adjust these values based on your landing pad color)
lower_color = np.array([20, 100, 100])
upper_color = np.array([30, 255, 255])

# Create a mask using the color range
mask = cv2.inRange(hsv, lower_color, upper_color)

# Find contours in the mask
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

if contours:
    # Choose the largest contour (assumed to be the landing pad)
    landing_pad_contour = max(contours, key=cv2.contourArea)

    # Calculate the centroid of the landing pad
    M = cv2.moments(landing_pad_contour)
    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])

    # Determine quadrant
    if cx < image.shape[1] / 2 and cy < image.shape[0] / 2:
        quadrant = "Top-left"
    elif cx >= image.shape[1] / 2 and cy < image.shape[0] / 2:
        quadrant = "Top-right"
    elif cx < image.shape[1] / 2 and cy >= image.shape[0] / 2:
        quadrant = "Bottom-left"
    else:
        quadrant = "Bottom-right"

    # Draw the contour and quadrant on the image
    cv2.drawContours(image, [landing_pad_contour], -1, (0, 255, 0), 2)
    cv2.putText(image, quadrant, (cx - 50, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # Save quadrant information to a text file
    output_file_path = 'output.txt'
    with open('output.txt', 'w') as output_file:
        sys.stdout = output_file  # Redirect standard output to the file
        print(f"{quadrant}")
        sys.stdout = sys.__stdout__  # Reset standard output

    print(f"Landing pad quadrant information saved to {output_file_path}")

    # Display the result
    cv2.imshow("Landing Pad", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
else:
    print("No landing pad detected in the image.")
