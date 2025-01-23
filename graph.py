import csv

class Graph:
    def __init__(self):
        self.dataset = 'dataset.csv'

    #column 1 , column 2 , column 3 = -1 if there is no edge value
    def construct_adjacency(self,column1,column2,column3,directed=False):
        graph = {}
        with open(self.dataset, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row if present
            for row in csv_reader:
                source_airport = row[column1]  # Source airport code
                destination_airport = row[column2]# Destination airport code
                if column3 > -1:
                    edge_value = float(row[column3])  # Distance

                    # Add the source airport to the graph if not already present
                    if source_airport not in graph:
                        graph[source_airport] = {}

                    # Add the destination airport and distance to the source airport's connections
                    graph[source_airport][destination_airport] = edge_value

                else:
                    # Add the source country to the graph if not already present
                    if source_airport not in graph:
                        graph[source_airport] = []

                    # Add the destination country to the list of connections for the source country
                    if destination_airport not in graph[source_airport]:
                        graph[source_airport].append(destination_airport)


        return graph
    
    def country_dropdown_list(self,column1):
        constructed_list = []
        with open(self.dataset, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row if present
            for row in csv_reader:
                country = row[column1]  # Source airport code

                if country not in constructed_list:
                    constructed_list.append(country)
        return constructed_list


    