import os
import sys

sys.path.append(os.path.abspath("../TiDB"))
from TiDB import TiDB

sys.path.append(os.path.abspath("../Colorize"))
from Colorize import Colorize

"""Load a text file containing SQL statements. Execute them and print a report."""


class SQLFileExecutor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.db = TiDB()

    def execute_sql_file(self):
        if not os.path.exists(self.file_path):
            print(f"Error: File '{self.file_path}' not found.")
            return

        with open(self.file_path, "r") as file:
            sql_statements = file.read().split(";")

        total_statements = 0
        successful_statements = 0
        failed_statements = 0

        for index, statement in enumerate(sql_statements, start=1):
            statement = statement.strip()
            if not statement:  # Skip empty statements
                continue
            total_statements += 1
            try:
                self.db.execute_query(statement)
                # print(f"{self.OKGREEN}{self.CHECK} {index}\t{statement}{self.ENDC}")
                print(Colorize.info(f"{Colorize.CHECK} {index}\t{statement}"))
                successful_statements += 1
            except Exception as e:
                print(
                    # f"{self.FAIL}{self.CROSS} {index}\t{statement}\nERROR: {str(e)}{self.ENDC}"
                    Colorize.error(
                        f"{Colorize.CROSS} {index}\t{statement}\nERROR: {str(e)}"
                    )
                )
                failed_statements += 1

        # print(f"\n{self.UNDERLINE}Execution Summary:{self.ENDC}")
        # print(f"{self.HEADER}Total statements: {total_statements}{self.ENDC}")
        # print(f"{self.OKGREEN}{self.CHECK}: {successful_statements}{self.ENDC}")
        # print(f"{self.FAIL}{self.CROSS}: {failed_statements}{self.ENDC}")

    def close_connection(self):
        self.db.close()


if __name__ == "__main__":
    executor = SQLFileExecutor(sys.argv[1])
    executor.execute_sql_file()
    executor.close_connection()
