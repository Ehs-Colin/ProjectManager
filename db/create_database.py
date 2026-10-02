import sqlite3 as sqlite


# Move to separate sql interaction file?
def execute_script(db_filename: str, script_filename: str):
    try:
        sql_connection = sqlite.connect(db_filename)
        cursor = sql_connection.cursor()
        with open(script_filename, "r") as scriptFile:
            script = scriptFile.read()

        cursor.executescript(script)

        sql_connection.commit()
    except Exception as e:
        print(f"Exception running script {script_filename}: {e}")
    finally:
        sql_connection.close()


def create_tables():
    # Loop through db/tables directory
    # Execute script for each table file
    pass
