import cv2

def capture_image():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite('landing_pad.jpg', frame)
    cap.release()

def detect_landing_pad(image_path):
    image = cv2.imread(image_path)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Define range for landing pad color
    lower_color = (36, 25, 25)
    upper_color = (86, 255, 255)
    
    mask = cv2.inRange(hsv, lower_color, upper_color)
    result = cv2.bitwise_and(image, image, mask=mask)
    
    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        # Assume the largest contour is the landing pad
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.imshow('Detected Landing Pad', image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return (x + w/2, y + h/2)  # Return the center of the landing pad
    else:
        return None

detect_landing_pad()
capture_image()