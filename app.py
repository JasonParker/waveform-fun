from datetime import datetime
import os
import schedule
import time


def playlist():
    schedule.every(1).second.do(liveness)

    schedule.every(10).seconds.do(print_message)

    ## This conditional keeps the function running
    while True:
        schedule.run_pending()
        time.sleep(1)


def print_message():
    print(f"{os.environ['NAME']}, it's working!")


def liveness():
    """
    Prints a message letting you know that the app is still running.
    """
    print(f"Running as of {datetime.now()}")

if __name__ == "__main__":
    liveness()
    playlist()