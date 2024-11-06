import cv2
import numpy as np

# Open video capture from the default camera (change index if needed)
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        print("Failed to capture frame. Exiting...")
        break

    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define the color range for blue
    lower_color = np.array([100, 100, 100])
    upper_color = np.array([150, 255, 255])

    # Create a mask using the color range
    mask = cv2.inRange(hsv, lower_color, upper_color)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Choose the largest contour (assumed to be the landing pad)
        landing_pad_contour = max(contours, key=cv2.contourArea)

        # Calculate the centroid of the landing pad
        M = cv2.moments(landing_pad_contour)

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
            cv2.drawContours(frame, [landing_pad_contour], -1, (0, 255, 0), 2)
            cv2.putText(frame, quadrant, (cx - 50, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            # Print the result
            print(f"Landing pad quadrant: {quadrant}")

    # Display the result
    cv2.imshow("Landing Pad", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
        break

# Release video capture and close all windows
cap.release()
cv2.destroyAllWindows()
