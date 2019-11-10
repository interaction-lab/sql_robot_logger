import robot_inspector.robot_inspector as ri

# create the inspector
inspector = ri.SQLInspector("config.yml")

# print everything in all the tables
print(inspector.get_query("log", "1=1"))
print(inspector.get_query("local_log", "1=1"))
print(inspector.get_query("topics", "1=1"))
print(inspector.get_query("robots", "1=1"))

# print the pandas data frames of the log table
print(inspector.get_query("log", "1=1").get())
