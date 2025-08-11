def readInput():
    try:
        with open('../testcase/testcase12.in', 'r',encoding="utf-8") as file:
            data = file.readlines()
            li = [line.strip() for line in data if (line[0] != '#' and line != '\n')]
            return li
    except FileNotFoundError:
        print("Input file not found.")
        return []
    except Exception as e:
        print(f"An error occurred while reading the input file: {e}")
        return []