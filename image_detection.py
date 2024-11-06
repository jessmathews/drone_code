import cv2
import numpy as np

# Load the template image
template = cv2.imread('testimage.jpg', cv2.IMREAD_COLOR)

# Open video capture from the default camera (change index if needed)
cap = cv2.VideoCapture(0)
# Get the template dimensions
template_height, template_width, _ = template.shape

while cap.isOpened():
    ret, frame = cap.read()

    if not ret:
        print("Failed to capture frame. Exiting...")
        break

    # Convert the frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Perform template matching
    result = cv2.matchTemplate(gray_frame, cv2.cvtColor(template, cv2.COLOR_BGR2GRAY), cv2.TM_CCOEFF_NORMED)
    _, _, _, max_loc = cv2.minMaxLoc(result)

    # Set a threshold for matching
    threshold = 0.8

    if np.max(result) > threshold:
        # Draw a rectangle around the detected template
        top_left = max_loc
        bottom_right = (top_left[0] + template_width, top_left[1] + template_height)
        cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)

        # Determine quadrant
        cx = (top_left[0] + bottom_right[0]) // 2
        cy = (top_left[1] + bottom_right[1]) // 2

        height, width, _ = frame.shape

        if cx < width / 2 and cy < height / 2:
            quadrant = "Top-left"
        elif cx >= width / 2 and cy < height / 2:
            quadrant = "Top-right"
        elif cx < width / 2 and cy >= height / 2:
            quadrant = "Bottom-left"
        else:
            quadrant = "Bottom-right"

        # Print the result
        print(f"Template found in quadrant: {quadrant}")

    # Display the result
    cv2.imshow("Template Matching", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
        break

# Release video capture and close all windows
cap.release()
cv2.destroyAllWindows()
