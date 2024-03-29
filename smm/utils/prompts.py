def read_system():
    with open("system.txt", "r", encoding="utf-8") as file:
        system = file.read()
    return system
