import csv
import tkinter as tk
import webbrowser
from datetime import datetime
from tkinter import messagebox, ttk
from tkinter import scrolledtext  # For displaying flight information

import folium
import folium.plugins
from PIL import ImageTk, Image
from folium.plugins import TagFilterButton, AntPath

from astar import Astar
from bfs import BFS
from graph import Graph


class Interface:

    def __init__(self):
        self.dataset = 'dataset.csv' #20 = distance 24 = cost
        #initialise classes
        self.graph = Graph()
        self.a_star = Astar()
        self.bfs = BFS()

        self.source_country_var = None
        self.source_city_var = None
        self.source_airport_var = None
        self.destination_country_var = None
        self.destinationcity_var = None
        self.destination_airport_var = None
        self.path_info = []
        self.path1_info_button = None
        self.path2_info_button = None
        self.path3_info_button = None

    # Function to create a Folium map with connections between countries
    def create_country_map(self, graph, country_coordinates, highlighted_countries):
        # Check if highlighted countries are available in the graph
        if not all(country in graph for country in highlighted_countries):
            print("Error: One or more highlighted countries not found in the graph.")
            return

        path_tags = {'Path 1': 'Path 1', 'Path 2': 'Path 2', 'Path 3': 'Path 3'}  # Define path tags

        # Create a Folium map centered on the first highlighted country's coordinates
        center_country = highlighted_countries[0]
        center_coords = country_coordinates.get(center_country)
        if center_coords is None:
            print(f"Error: Coordinates not found for country '{center_country}'.")
            return
        my_map = folium.Map(location=center_coords, zoom_start=4)

        # Extract countries from path_info
        path_countries = set()
        if self.path_info:
            for path, _ in self.path_info:
                path_countries.update(path)

        # Draw nodes for each country
        for country, coords in country_coordinates.items():
            if country in path_countries:  # Check if the country is in any of the paths
                marker_color = 'red'  # Set marker color to red for countries in the path
            else:
                marker_color = 'gray'  # Set marker color to gray for other countries
            my_map.add_child(folium.CircleMarker(
                location=coords,
                radius=5,
                color=marker_color,
                fill=True,
                fill_color=marker_color,
                fill_opacity=0.7,
                popup=folium.Popup(country, max_width=1000)  # Set maximum width for popup
            ))

        # Draw edges for each path
        if self.path_info:
            colors = ['blue', 'green', 'orange', 'purple', 'pink']  # Define colors for different paths
            for i, (path, distance) in enumerate(self.path_info, start=1):
                path_name = f"Path {i}"
                path_tag = path_tags[path_name]
                color = colors[i % len(colors)]  # Select color based on index
                ant_path = AntPath(
                    locations=[country_coordinates[country] for country in path],
                    color=color,
                    tooltip=f"<b>{path_name}:</b><br>The flight from {path[0]} to {path[-1]} is {distance:.2f} km",
                    delay=1000,
                    tags=[path_tag]  # Assign tag to the path
                ).add_to(my_map)  # Delay between animation steps in milliseconds

        # Add tag filter button
        pathCategories = list(path_tags.values())
        filter_button = TagFilterButton(pathCategories, position='topright')
        my_map.add_child(filter_button)

        my_map.save("country_connection_map.html")

        self.path1_info_button.grid(row=0, column=0, padx=5, pady=5)
        self.path2_info_button.grid(row=0, column=1, padx=5, pady=5)
        self.path3_info_button.grid(row=0, column=2, padx=5, pady=5)

    # Function to get the airport based on airport IATA code
    def get_airport_from_iata(self,iata_code, csv_file):
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row if present
            for row in csv_reader:
                if iata_code == row[0]:
                    return row[2]  # airport name corresponding to the IATA code
        return None  # Return None if IATA code is not found

    # Function to get the IATA based on airport
    def get_iata_from_airport(self, airport, csv_file):
        with open(csv_file, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row if present
            for row in csv_reader:
                if airport == row[2]:
                    return row[0]  # airport name corresponding to the IATA code
        return None  # Return None if IATA code is not found

    # Function to retrieve flight information based on source and destination airport codes
    def retrieve_flight_information(self, source_entry, destination_entry, flight_info_text):
        self.path_info = []
        flight_info_text.config(state=tk.NORMAL)
        
        source_airport_code = self.get_iata_from_airport(source_entry.get(), self.dataset)
        destination_airport_code = self.get_iata_from_airport(destination_entry.get(), self.dataset)

        source_airport = None
        destination_airport = None

        if source_airport_code is None or destination_airport_code is None:
            messagebox.showerror("Error", f"Source and Destination Airport cannot empty")

        elif source_airport_code == destination_airport_code and source_airport_code is not None and destination_airport_code is not None:
            messagebox.showerror("Error", f"Source and Destination Airport cannot be the same")

        else:
            source_airport = source_airport_code.upper()  # Get source airport code
            destination_airport = destination_airport_code.upper()  # Get source airport code
            cost_graph = self.graph.construct_adjacency(0,11,24)
            flight_graph = self.graph.construct_adjacency(0,11,20)

            if source_airport not in flight_graph:
                messagebox.showerror("Error", f"Source airport '{source_airport}' not found in the graph.")
                return

            if destination_airport not in flight_graph:
                messagebox.showerror("Error", f"Destination airport '{destination_airport}' not found in the graph.")
                return

            # Find cheapest route using A* algo
            path, cost = self.a_star.run_a_star(cost_graph, source_airport, destination_airport)
            # Find the three shortest paths using BFS
            bfs_paths = self.bfs.run_bfs(flight_graph, source_airport, destination_airport, 3)

            # Display flight information
            flight_info_text.delete(1.0, tk.END)  # Clear previous text
            self.path1_info_button.config(state=tk.NORMAL)
            self.path2_info_button.config(state=tk.NORMAL)
            self.path3_info_button.config(state=tk.NORMAL)
            # Convert IATA codes to airport names
            formatted_path = [self.get_airport_from_iata(code, self.dataset) for code in path]
            flight_info_text.insert(tk.END, f"Cheapest path: ")

            for i, airport_name in enumerate(formatted_path):
                flight_info_text.insert(tk.END, airport_name)
                if i < len(formatted_path) - 1:
                    flight_info_text.insert(tk.END, ", ")

            flight_info_text.insert(tk.END, f"\nCost: ${round(cost,2)}\n")

            if bfs_paths:
                # Sort the shortest paths based on their distances
                bfs_paths.sort(key=lambda path: self.bfs.calculate_path_distance(flight_graph, path))

                flight_info_text.insert(tk.END, f"\n3 shortest paths (in ascending order of distance):\n")
                for i, path in enumerate (bfs_paths):
                    distance = self.bfs.calculate_path_distance(flight_graph, path)
                    # Convert IATA codes to airport names
                    formatted_path = [self.get_airport_from_iata(code, self.dataset) for code in path]
                    flight_info_text.insert(tk.END, f"Path {i+1}:\n")

                    for i, airport_name in enumerate(formatted_path):
                        flight_info_text.insert(tk.END, airport_name)
                        if i < len(formatted_path) - 1:
                            flight_info_text.insert(tk.END, " -> ")

                    flight_info_text.insert(tk.END, f"\nDistance: {distance:.2f}km\n\n")
                    if i >= 1:
                        if (len(path) == 2):
                            source = self.get_airport_from_iata(path[0], self.dataset)
                            destination = self.get_airport_from_iata(path[1], self.dataset)
                            path[0] = source
                            path[1] = destination

                        elif (len(path) == 3):
                            source = self.get_airport_from_iata(path[0], self.dataset)
                            middle = self.get_airport_from_iata(path[1], self.dataset)
                            destination = self.get_airport_from_iata(path[2], self.dataset)
                            path[0] = source
                            path[1] = middle
                            path[2] = destination

                        elif (len(path) == 4):
                            source = self.get_airport_from_iata(path[0], self.dataset)
                            middle1 = self.get_airport_from_iata(path[1], self.dataset)
                            middle2 = self.get_airport_from_iata(path[2], self.dataset)
                            destination = self.get_airport_from_iata(path[3], self.dataset)
                            path[0] = source
                            path[1] = middle1
                            path[2] = middle2
                            path[3] = destination

                        elif (len(path) == 5):
                            source = self.get_airport_from_iata(path[0], self.dataset)
                            middle1 = self.get_airport_from_iata(path[1], self.dataset)
                            middle2 = self.get_airport_from_iata(path[2], self.dataset)
                            middle3 = self.get_airport_from_iata(path[3], self.dataset)
                            destination = self.get_airport_from_iata(path[4], self.dataset)
                            path[0] = source
                            path[1] = middle1
                            path[2] = middle2
                            path[3] = middle3
                            path[4] = destination

                        elif (len(path) == 6):
                            source = self.get_airport_from_iata(path[0], self.dataset)
                            middle1 = self.get_airport_from_iata(path[1], self.dataset)
                            middle2 = self.get_airport_from_iata(path[2], self.dataset)
                            middle3 = self.get_airport_from_iata(path[3], self.dataset)
                            middle4 = self.get_airport_from_iata(path[4], self.dataset)
                            destination = self.get_airport_from_iata(path[5], self.dataset)
                            path[0] = source
                            path[1] = middle1
                            path[2] = middle2
                            path[3] = middle3
                            path[4] = middle4
                            path[5] = destination

                        self.path_info.append([path, distance])

                self.open_map_window_with_airports(source_airport, destination_airport)
            else:
                flight_info_text.insert(tk.END, f"No paths found between the source and destination.\n")
        flight_info_text.config(state=tk.DISABLED)

    # Function to display time in UI
    def update_current_time(self, root, current_time_label):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        current_time_label.config(text="Current Time: " + current_time)
        root.after(1000, self.update_current_time, root , current_time_label)  # Update every 1 second (1000 milliseconds)

    def open_map_window_with_airports(self, source_iata, destination_iata):
        # Read the CSV file to extract latitude and longitude coordinates
        # print(source_iata, destination_iata)
        airport_coordinates = {}
        airport_graph = self.graph.construct_adjacency(2,13,-1)

        with open(self.dataset, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row if present
            for row in csv_reader:
                country = row[2]  # Country name
                latitude = float(row[5])  # Latitude
                longitude = float(row[6])  # Longitude
                airport_coordinates[country] = (latitude, longitude)

        # Get the corresponding countries for the source and destination airport IATA codes
        source_country = self.get_airport_from_iata(source_iata, self.dataset)
        destination_country = self.get_airport_from_iata(destination_iata, self.dataset)

        # Check if countries are found for the provided IATA codes
        if source_country is None:
            print(f"Error: Country not found for source airport '{source_iata}'.")
            return
        if destination_country is None:
            print(f"Error: Country not found for destination airport '{destination_iata}'.")
            return

        # Create a Folium map with connections between countries
        self.create_country_map(airport_graph, airport_coordinates, [source_country, destination_country])

        #webrowser to open html file
        webbrowser.open_new_tab("country_connection_map.html")

    def update_cities(self, *args, is_source=True):
        cities_data, city_menu = args[3], args[4]
        selected_country = self.source_country_var.get() if is_source else self.destination_country_var.get()

        # Check if selected_country exists in cities_data
        if selected_country not in cities_data:
            print(f"Error: '{selected_country}' not found in cities_data.")
            return

        # Get cities based on the selected country
        cities = cities_data[selected_country]

        city_var = self.source_city_var if is_source else self.destination_city_var
        city_var.set(cities[0])

        # Clear previous options and set new options
        city_menu['values'] = cities

    def update_airports(self, *args, is_source=True):
        airports_data, airport_menu = args[3], args[4]
        selected_city = self.source_city_var.get() if is_source else self.destination_city_var.get()

        # Get airports based on the selected city
        airports = airports_data[selected_city]

        airports_var = self.source_airport_var if is_source else self.destination_airport_var
        airports_var.set(airports[0])  # Set default airport

        # Clear previous options and set new options
        airport_menu['values'] = airports

    def get_airlines(self,airport_iata_1,airpot_iata_2):
        with open(self.dataset, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row if present
            airlines = []
            for row in csv_reader:
                if row[0] == airport_iata_1 and row[11] == airpot_iata_2:
                    airlines.append(row[10])
        return airlines
                

    def display_path_info(self, button_pressed):
        if button_pressed == self.path1_info_button:
            path_index = 0
        elif button_pressed == self.path2_info_button:
            path_index = 1
        elif button_pressed == self.path3_info_button:
            path_index = 2
        else:
            print("Error: Invalid button pressed")
            return
        path_info_message = f"Path {path_index + 1} Info:\n\n"
        if path_index < len(self.path_info):
            path, distance= self.path_info[path_index]
            cost_graph = self.graph.construct_adjacency(0,11,24)
            cost = 0
            airlines_list = []
            for i in range(len(path)-1):
                airport1 = self.get_iata_from_airport(path[i],self.dataset)
                airport2 = self.get_iata_from_airport(path[i+1],self.dataset)
                cost += cost_graph[airport1][airport2]
                path_info_message += f"Path: \n{path[i]} -> {path[i+1]}\n"
                airlines = self.get_airlines(airport1,airport2)
                airlines_list.append(airlines)
                path_info_message += f"Airlines: {', '.join(airlines)}\n\n"
            
            path_info_message += f"Total Distance: {distance:.2f} km\n"
            path_info_message += f"Approximate Cost entire flight: ${cost:.2f} \n"
            messagebox.showinfo("More path Information", path_info_message)


        else:
            messagebox.showerror("Error", f"No information available for Path {path_index + 1}.")

    def howToPopup(self):
        with open("HowTo.txt", "r") as f:
            help_msg = f.read()

        messagebox.showinfo(title="Guide for Graphical User Interface Interaction", message=help_msg)

    def logout(self,root):
        # Close the login window
        root.destroy()
        self.open_login_window()

    def login(self,master,username_entry,password_entry):
        account = {}
        with open('account.csv', 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row if present
            for row in csv_reader:
                account[row[1]] = row[2]

        username = username_entry.get()
        password = password_entry.get()

        # Check if username and password are valid
        if username != "" and password != "":
            if username in account:
                if password == account[username]:
                    # Close the login window
                    master.destroy()
                    # Open the main application window
                    root = tk.Tk()
                    self.open_main_window(root,username)
                    root.mainloop()
                else:
                    messagebox.showerror("Login Failed", "Incorrect password, please try again")
            else:
                messagebox.showerror("Login Failed", "Invalid username, please try again")
        else:
            messagebox.showerror("Login Failed", "Username and Password cannot be empty")

    def open_login_window(self):
        master = tk.Tk()
        master.resizable(False, False)
        master.title("World Air Routes")

        # Calculate the position to center the entire window
        window_width = 900
        window_height = 750
        screen_width = master.winfo_screenwidth()
        screen_height = master.winfo_screenheight()
        x_coordinate = (screen_width - window_width) // 2
        y_coordinate = (screen_height - window_height) // 2

        # Set the window position
        master.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        frame = tk.Frame(master)
        frame.pack(padx=10, pady=10)

        # Load the image of airplane.png
        image_path = "airplane_bw.png"
        image = Image.open(image_path)
        image = image.resize((200, 200))  # Resize the image
        photo = ImageTk.PhotoImage(image)

        # Add an image label
        image_label = tk.Label(frame, image=photo)
        image_label.grid(row=0, column=0, columnspan=4, padx=10, pady=(80, 40))

        # Username label and entry field
        username_label = tk.Label(frame, text="Username:")
        username_label.grid(row=1, column=1, padx=10, pady=5, sticky='e')
        username_entry = tk.Entry(frame)
        username_entry.grid(row=1, column=2, padx=10, pady=5, sticky='w')

        # Password label and entry field
        password_label = tk.Label(frame, text="Password:")
        password_label.grid(row=2, column=1, padx=10, pady=5, sticky='e')
        password_entry = tk.Entry(frame, show="*")
        password_entry.grid(row=2, column=2, padx=10, pady=5, sticky='w')

        # Login button
        self.login_button = tk.Button(frame, text="Login",
                                 command=lambda: self.login(master, username_entry, password_entry), bg="lightblue")
        self.login_button.grid(row=3, column=1, columnspan=2, padx=10, pady=(20, 5), sticky='we')

        # Add button to display How To guide
        self.howTo_btn = tk.Button(frame, text="How to guide", command=lambda: self.howToPopup(), bg="lightgreen")
        # Add button to display How To guide
        self.howTo_btn.grid(row=5, column=1, columnspan=2, padx=10, pady=5, sticky='we')  # Centralized between columns 1 and 2

        # Signup button
        self.signup_button = tk.Button(frame, text="Sign up", command=self.signup_dialog, bg="lightpink")
        self.signup_button.grid(row=4, column=1, columnspan=2, padx=10, pady=5, sticky='we')

        master.mainloop()

    def signup_dialog(self):

        # Disable the sign-up button in the main window
        self.signup_button.config(state="disabled")
        self.login_button.config(state="disabled")

        # Create a custom styled pop-up dialog for sign up
        signup_dialog = tk.Toplevel()
        signup_dialog.title("Sign Up")
        signup_dialog.geometry("300x150")
        signup_dialog.configure(bg="#f0f0f0")  # Set background color

        # Create a frame to hold the signup components
        frame = tk.Frame(signup_dialog, bg="#f0f0f0")
        frame.pack(padx=10, pady=10)

        # Username label and entry field
        username_label = tk.Label(frame, text="Username:", bg="#f0f0f0", fg="black")
        username_label.grid(row=0, column=0, padx=10, pady=5, sticky='e')
        username_entry = tk.Entry(frame)
        username_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')

        # Password label and entry field
        password_label = tk.Label(frame, text="Password:", bg="#f0f0f0", fg="black")
        password_label.grid(row=1, column=0, padx=10, pady=5, sticky='e')
        password_entry = tk.Entry(frame, show="*")
        password_entry.grid(row=1, column=1, padx=10, pady=5, sticky='w')

        # Function to handle sign up button click
        def handle_signup():
            username = username_entry.get()
            password = password_entry.get()

            # Check if username and password are not empty
            if username.strip() == "" or password.strip() == "":
                messagebox.showerror("Sign Up Failed", "Username and password cannot be empty!")
                return

            # Update the CSV file with the new account information
            with open('account.csv', 'a', newline='', encoding='utf-8') as file:
                csv_writer = csv.writer(file)  # Specify newline character
                # Get the current number of accounts
                with open('account.csv', 'r', encoding='utf-8') as read_file:
                    reader = csv.reader(read_file)
                    next(reader)
                    rows = list(reader)
                    # Check if this username has been created before
                    for row in rows:
                        if username == row[1]:
                            messagebox.showerror("Sign Up Failed", "Username has already been used")
                            return

                    if len(rows) > 0:
                        if not rows[len(rows) - 1]:
                            last_row = rows[len(rows) - 2]
                        else:
                            last_row = rows[len(rows) - 1]

                        last_account_no = int(last_row[0])  # Get the account number of the last row
                    else:
                        last_account_no = 1000000
                    account_no = last_account_no + 1  # Get the number of rows
                csv_writer.writerow([account_no, username, password])

            messagebox.showinfo("Sign Up Successful", "Account created successfully!")
            self.signup_button.config(state="normal")
            self.login_button.config(state="normal")
            signup_dialog.destroy()  # Close the sign-up dialog

        def cancel_signup():
            # Re-enable the sign-up button in the main window
            self.signup_button.config(state="normal")
            self.login_button.config(state="normal")
            signup_dialog.destroy()

        # Sign up button
        signup_button = tk.Button(frame, text="Create Account", command=handle_signup, bg="lightblue")
        signup_button.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky='we')

        # Cancel button
        cancel_button = tk.Button(frame, text="Cancel", command=cancel_signup, bg="lightpink")
        cancel_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky='we')


        signup_dialog.mainloop()

    def open_main_window(self,root,username):
        root.resizable(False, False)
        root.title("World Air Routes")

        # Set column weights to centralize fields
        root.grid_columnconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)
        root.grid_columnconfigure(2, weight=1)
        root.grid_columnconfigure(3, weight=1)
        root.grid_rowconfigure(0,weight=0)
        root.grid_rowconfigure(1,weight=0)
        root.grid_rowconfigure(2,weight=0)
        root.grid_rowconfigure(3,weight=0)

        # Calculate the position to center the entire window
        window_width = 900
        window_height = 700
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_coordinate = (screen_width - window_width) // 2
        y_coordinate = (screen_height - window_height) // 2

        # Set the window position
        root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        # Create a frame for the navigation bar
        nav_frame = tk.Frame(root)
        nav_frame.grid(row=0, column=0, sticky="ew")

        # Add buttons to the navigation bar
        logout_button = tk.Button(nav_frame, text="Logout" , command=lambda:self.logout(root))
        logout_button.grid(row=0, column=0, padx=5, pady=5)

        #welcome login user
        welcome_label = tk.Label(nav_frame, text=f"Welcome, {username}!", font=("Arial", 8))
        welcome_label.grid(row=0, column=1,padx=5, pady=5, sticky='w')
        #welcome_label.pack()

        # Load the image of airplane.png
        image_path = "airplane.png"
        image = Image.open(image_path)
        image = image.resize((100, 100))  # Resize the image
        photo = ImageTk.PhotoImage(image)

        # Add an image label
        image_label = tk.Label(root, image=photo)
        image_label.image = photo
        image_label.grid(row=1, column=0, columnspan=6, padx=10, pady=5)

        # Add current time label
        current_time_label = tk.Label(root, text="Current Time: ", fg="red", font=('', 12, 'bold'))
        current_time_label.grid(row=2, column=0, columnspan=6, padx=10, pady=5)
        self.update_current_time(root, current_time_label)

        # Create variables to store selected values
        self.source_country_var = tk.StringVar(root)
        self.source_city_var = tk.StringVar(root)
        self.source_airport_var = tk.StringVar(root)
        self.destination_country_var = tk.StringVar(root)
        self.destination_city_var = tk.StringVar(root)
        self.destination_airport_var = tk.StringVar(root)

        # Create the dropdowns
        source_country_label = tk.Label(root, text="Source Country:")
        source_country_label.grid(row=3, column=0, padx=3, pady=5, sticky='e')
        source_country_menu = ttk.Combobox(root, textvariable=self.source_country_var, state="readonly", width=27)
        source_country_menu['values'] = sorted(self.graph.country_dropdown_list(4))
        source_country_menu.grid(row=3, column=1, padx=3, pady=5, sticky='w')
        source_country_menu.current(0)

        destination_country_label = tk.Label(root, text="Destination Country:")
        destination_country_label.grid(row=3, column=2, padx=3, pady=5, sticky='e')
        destination_country_menu = ttk.Combobox(root, textvariable=self.destination_country_var, state="readonly", width=27)
        destination_country_menu['values'] = sorted(self.graph.country_dropdown_list(4))
        destination_country_menu.grid(row=3, column=3, padx=3, pady=5, sticky='w')
        destination_country_menu.current(0)

        source_city_label = tk.Label(root, text="Source City:")
        source_city_label.grid(row=4, column=0, padx=3, pady=5, sticky='e')
        source_city_menu = ttk.Combobox(root, textvariable=self.source_city_var, state="readonly", width=27)
        source_city_menu['values'] = sorted(self.graph.country_dropdown_list(3))
        source_city_menu.grid(row=4, column=1, padx=3, pady=5, sticky='w')
        source_city_menu.set("Please select a country first")

        destination_city_label = tk.Label(root, text="Destination City:")
        destination_city_label.grid(row=4, column=2, padx=3, pady=5, sticky='e')
        destination_city_menu = ttk.Combobox(root, textvariable=self.destination_city_var, state="readonly", width=27)
        destination_city_menu['values'] = sorted(self.graph.country_dropdown_list(3))
        destination_city_menu.grid(row=4, column=3, padx=3, pady=5, sticky='w')
        destination_city_menu.set("Please select a country first")

        source_airport_label = tk.Label(root, text="Source Airport:")
        source_airport_label.grid(row=5, column=0, padx=3, pady=5, sticky='e')
        source_airport_menu = ttk.Combobox(root, textvariable=self.source_airport_var, state="readonly", width=27)
        source_airport_menu['values'] = sorted(self.graph.country_dropdown_list(2))
        source_airport_menu.grid(row=5, column=1, padx=3, pady=5, sticky='w')
        source_airport_menu.set("Please select a country first")

        destination_airport_label = tk.Label(root, text="Destination Airport:")
        destination_airport_label.grid(row=5, column=2, padx=3, pady=5, sticky='e')
        destination_airport_menu = ttk.Combobox(root, textvariable=self.destination_airport_var, state="readonly",width=27)
        destination_airport_menu['values'] = sorted(self.graph.country_dropdown_list(2))
        destination_airport_menu.grid(row=5, column=3, padx=3, pady=5, sticky='w')
        destination_airport_menu.set("Please select a country first")

        # Add text area to display flight information
        flight_info_text = scrolledtext.ScrolledText(root, width=130, height=18)
        flight_info_text.grid(row=9, column=0, columnspan=6, padx=10, pady=5)
        flight_info_text.config(state=tk.DISABLED)

        # Create a frame for path information buttons
        path_button_frame = tk.Frame(root)
        path_button_frame.grid(row=8, column=0, columnspan=6, padx=10, pady=5)

        # Add button to display information for Path 1
        self.path1_info_button = tk.Button(path_button_frame, text="Path 1 Info",command=lambda: self.display_path_info(self.path1_info_button), bg="lightpink")
        self.path1_info_button.grid(row=0, column=0, padx=5, pady=5)
        # Hide Path 1 Info button
        self.path1_info_button.grid_forget()

        # Add button to display information for Path 2
        self.path2_info_button = tk.Button(path_button_frame, text="Path 2 Info",command=lambda: self.display_path_info(self.path2_info_button), bg="lightpink")
        self.path2_info_button.grid(row=0, column=1, padx=20, pady=5)  # Centralized
        self.path2_info_button.grid_forget()

        # Add button to display information for Path 3
        self.path3_info_button = tk.Button(path_button_frame, text="Path 3 Info",command=lambda: self.display_path_info(self.path3_info_button), bg="lightpink")
        self.path3_info_button.grid(row=0, column=2, padx=5, pady=5)
        self.path3_info_button.grid_forget()

        # Add button to retrieve flight information
        retrieve_button = tk.Button(root, text="Retrieve Flight Information", command=lambda: self.retrieve_flight_information(self.source_airport_var, self.destination_airport_var, flight_info_text), bg="lightblue")
        retrieve_button.grid(row=6, column=0,  columnspan=6, padx=10, pady=5)

        # Set up trace callbacks to update the cities and airports
        self.source_country_var.trace_add('write', lambda *args, cities_data=self.graph.construct_adjacency(4,3,-1), city_menu=source_city_menu: self.update_cities(*args, cities_data, city_menu))
        self.source_city_var.trace_add('write', lambda *args, airports_data=self.graph.construct_adjacency(3,2,-1), airport_menu=source_airport_menu: self.update_airports(*args, airports_data, airport_menu))

        self.destination_country_var.trace_add('write', lambda *args, cities_data=self.graph.construct_adjacency(4,3,-1), city_menu=destination_city_menu: self.update_cities(*args, cities_data, city_menu, is_source=False))
        self.destination_city_var.trace_add('write', lambda *args, airports_data=self.graph.construct_adjacency(3,2,-1), airport_menu=destination_airport_menu: self.update_airports(*args, airports_data, airport_menu, is_source=False))
