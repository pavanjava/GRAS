import base64
import os


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string


def main():
    print("Welcome to the Image to Base64 Converter!")

    while True:
        image_path = input("Enter the path to your image file (or 'q' to quit): ")

        if image_path.lower() == 'q':
            print("Thank you for using the Image to Base64 Converter. Goodbye!")
            break

        if not os.path.exists(image_path):
            print("Error: File does not exist. Please try again.")
            continue

        try:
            base64_string = image_to_base64(image_path)
            print("\nBase64 encoded string:")
            print(base64_string)

            save_option = input("\nDo you want to save this to a file? (y/n): ")
            if save_option.lower() == 'y':
                output_path = input("Enter the output file path: ")
                with open(output_path, 'w') as output_file:
                    output_file.write(base64_string)
                print(f"Base64 string saved to {output_path}")

            print("\n")
        except Exception as e:
            print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
