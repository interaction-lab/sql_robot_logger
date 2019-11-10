from prettytable import PrettyTable
import pandas as pd


class Query:

    def __init__(self, list_of_matches, header=None):
        self.header = header
        self.data = list_of_matches

    def __repr__(self):

        x = PrettyTable()
        x.field_names = self.header

        self.new_data = []

        for row in self.data:
            new_row = []
            for value in row:
                if type(value).__name__ == "bytearray":
                    try:
                        new_row.append(value.decode())
                    except AttributeError:
                        new_row.append(value)
                else:
                    new_row.append(value)
            self.new_data.append(new_row)

        for match in self.new_data:
            x.add_row(list(match))

        self.new_header = []

        x.field_names = self.header

        return str(x)

    def get(self):
        return pd.DataFrame(self.data)
