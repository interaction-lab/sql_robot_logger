import robot_logger.robot_logger as rl
import threading

# create the logger object with the config file specifying the database information
logger = rl.RobotLogger("config.yml")

# add topic with name and type
logger.add_topic("num", int)


# callback functions for threading
def func1():
    for i in range(10):
        logger.write("num", str(i), "func1.py", True)


def func2():

    for i in range(10):
        logger.write("num", str(i), "func2.py", True)


# create threads that will write to the db
thread = threading.Thread(target=func1())
thread1 = threading.Thread(target=func2())

# run the threads
thread.start()
thread1.start()
thread.join()
thread1.join()
