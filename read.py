# Specify the path to your text file
file_path = 'output.txt'

try:
    # Open the file in read mode
    with open(file_path, 'r') as file:
        # Read the content of the file
        file_content = file.read()

        if file_content == "Top-right":
            print("move top right")
        if file_content == "Top-left":
            print("move top left")
        if file_content == "Bottom-right":
            print("move bottom right")
        if file_content == "Bottom-left":
            print("move bottom")
        if file_content == "Top-right":
            print("move top right")

except FileNotFoundError:
    print(f"File not found: {file_path}")
except Exception as e:
    print(f"Error occurred: {e}")
