import cv2
import torch

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'custom', path='path_to_your_custom_model.pt')  # Replace with your custom model path

def detection():

    # Open video capture from the default camera (change index if needed)
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            print("Failed to capture frame. Exiting...")
            break

        # Perform YOLOv5 detection
        results = model(frame)

        # Extract the bounding box and class name
        for det in results.xyxy[0].cpu().numpy():
            xmin, ymin, xmax, ymax, conf, cls = det
            if cls == 0:  # Assuming class 0 is the landing pad in your custom model
                cx = int((xmin + xmax) / 2)
                cy = int((ymin + ymax) / 2)
                cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 255, 0), 2)

                # Determine quadrant
                if cx < frame.shape[1] / 2 and cy < frame.shape[0] / 2:
                    quadrant = "Top-left"
                elif cx >= frame.shape[1] / 2 and cy < frame.shape[0] / 2:
                    quadrant = "Top-right"
                elif cx < frame.shape[1] / 2 and cy >= frame.shape[0] / 2:
                    quadrant = "Bottom-left"
                else:
                    quadrant = "Bottom-right"

                # Check if the object is within the reduced square region
                region_top_left = (frame.shape[1] // 3, frame.shape[0] // 3)
                region_bottom_right = (2 * frame.shape[1] // 3, 2 * frame.shape[0] // 3)

                if region_top_left[0] <= cx <= region_bottom_right[0] and \
                        region_top_left[1] <= cy <= region_bottom_right[1]:
                    cv2.rectangle(frame, region_top_left, region_bottom_right, (0, 0, 255), 2)
                    region_status = "Bounded"
                else:
                    region_status = "Not Bounded"

                cv2.putText(frame, quadrant, (cx - 50, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                drone_movement(quadrant, region_status)

        # Display the result
        cv2.imshow("Landing Pad", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
            break

    # Release video capture and close all windows
    cap.release()
    cv2.destroyAllWindows()

def drone_movement(quadrant, region):
    if region == "Not Bounded":
        if quadrant == "Top-right":
            print("move left then bottom")
        elif quadrant == "Top-left":
            print("move right then bottom")
        elif quadrant == "Bottom-right":
            print("move left then top")
        elif quadrant == "Bottom-left":
            print("move right then top")
    else:
        print("land drone")

detection()
