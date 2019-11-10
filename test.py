import unittest
import threading
import time
import robot_inspector.robot_inspector as ri
import robot_logger.robot_logger as rl


class TestLogger(unittest.TestCase):

    def testTopics(self):
        ins = ri.SQLInspector("config.yml")
        log = rl.RobotLogger("config.yml")
        log._clear_tables()
        log._create_tables()

        for i in range(0, 5):
            log.add_topic("test_topic" + str(i), int)

        time.sleep(5)
        query = str(ins.get_query("topics", "1=1"))
        self.assertEqual(9, int(len(query.split('\n'))))

    def testThread(self):
        ins = ri.SQLInspector("config.yml")
        log = rl.RobotLogger("config.yml")
        log._clear_tables()
        log._create_tables()

        log.add_topic("test_topic", int)
        for i in range(0, 5):
            log.write("test_topic", 10+i, "this.py", True)

        time.sleep(5)
        query = str(ins.get_query("log", "1=1"))
        self.assertEqual(9, int(len(query.split('\n'))))

    def testAddInvalidTopic(self):
        log = rl.RobotLogger("config.yml")
        log._clear_tables()
        log._create_tables()

        log.add_topic("test_topic", int)

        try:
            log.add_topic("test_topic", int)
        except ValueError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def testWriteToInvalidTopic(self):
        log = rl.RobotLogger("config.yml")
        log._clear_tables()
        log._create_tables()

        log.add_topic("test_topic", int)

        try:
            log.write("test_topic1", 111, "this.py", True)
        except ValueError:
            self.assertTrue(True)
        else:
            self.assertTrue(False)

    def testMultipleWrites(self):

        ins = ri.SQLInspector("config.yml")

        log = rl.RobotLogger("config.yml")
        log._clear_tables()
        log._create_tables()

        log1 = rl.RobotLogger("config.yml")
        log1._clear_tables()
        log1._create_tables()

        log.add_topic("test_thread_1", int)
        log.add_topic("test_thread_2", int)

        x = threading.Thread(target=log.write, args=("test_thread_1", 1, str(__file__), True))
        y = threading.Thread(target=log.write, args=("test_thread_2", 2, str(__file__), True))
        z = threading.Thread(target=log1.write, args=("test_thread_1", 1, str(__file__), True))
        k = threading.Thread(target=log1.write, args=("test_thread_2", 2, str(__file__), True))

        x.start()
        z.start()
        y.start()
        k.start()

        time.sleep(5)
        query = str(ins.get_query("log", "1=1"))
        self.assertEqual(8, int(len(query.split('\n'))))
