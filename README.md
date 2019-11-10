# README

Creates and updates a robot state logging database.

This program allows you to log information to different topics stored in a database file, extract subsets based on certain condition, as well as converting such selections into pandas dataframes.

## Example 

1. Create a config.yml file in the home directory that mirrors the following

         log_info:
            database_name:
            robot_id: 
         sql_database:
            host: 
            password: 
            port: 
            user:
            
     * if robot_id is left blank, then one is assigned based on the next available robot_id in the database

1. Create the state logger object and give it a unique id and a database to write to (if left blank, one will automatically be created)

             import robot_logger.robot_logger as rl
             robot_logger = rl.RobotLogger()

1. Add a topic and its respective data type
             
            robot_logger.add_topic("test_topic", int)
2. Add integer message with the topic and allow for local backup
            
            robot_logger.write("test_topic", 1234, str(__file__), True)
3. Create the database inspector

            import robot_inspector.robot_inspector as ri
            robot_inspector = ri.SQLInspector()
    
4. Generate a query from the log table that match a custom condition
    
            query = robot_inspector.get_query("log","topic_id = 1")
    
5. Display the list of matches

            print(query)
6. Generate a pandas data frame from the query

            df = q.get()
            
## Run instructions
> Note, only tested with Python 3

0. Clone the repository

       git clone git@github.com:adamhamden/aws-sql-logger-interface.git
       
1. Go in the cloned directory

		cd aws-sql-logger-interface

1. Start a virtual environment

		virtualenv -p python3 venv
		source venv/bin/activate

1. Install the requirements

		pip install -r requirements.txt
		
1. Check that the tests run

		python -m unittest test.py

1. Import and use the module!
		