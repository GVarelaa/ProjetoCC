from datetime import datetime


def add_log(file_path, message):
    f = open(file_path, "a")

    dt = datetime.now().strftime("%d:%m:%Y.%H:%M:%S:%f")

    f.write(dt + " " + message + "\n")

    f.close()

add_log("log.txt", "erro")
