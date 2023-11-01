import Beer  # Import the Beer module

if __name__ == "__main__":
    while True:
        inText = input("Beer: ")
        result, error = Beer.run('<stdin>', inText)

        if error:
            print(error.as_string())
        else:
            print(result)
