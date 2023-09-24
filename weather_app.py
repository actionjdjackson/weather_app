import json
import requests
from datetime import datetime, timedelta
from tkinter import *
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

API_KEY = "04cefdc70dc64f37bf001213232309"
N_DAYS_FORECAST = 10 # Make this into a 7 day forecast - Karan

class WeatherApp(Tk):
    def __init__(self):
        super().__init__()
        self.title("Weather App")
        self.geometry("640x480")
        self.create_widgets()

    def create_widgets(self):
        Label(self, text="Enter City, State or Country: ").grid(row = 0, column = 0, sticky="nsew")
        self.location_entry = Entry(self, width = 20)
        self.location_entry.grid(row = 0, column = 1, sticky="nsew")
        Button(self, text = "Get Weather", command = self.get_weather).grid(row = 0, column = 2, sticky = "nsew")

        ##### This is the popup menu for forecast day selection ######
        self.n = StringVar()
        self.n.trace('w', self.get_forecast_change) #This is for detecting a change in popup menu
        self.forecast_day_chooser = ttk.Combobox(self, width = 18, textvariable = self.n)
        self.forecast_day_chooser["values"] = self.create_forecast_options()
        self.forecast_day_chooser.grid(column = 0, row = 1, sticky="nsew")
        self.forecast_day_chooser.current(0)
        ##############################################################

        # Remove below code once tested - Karan
        # self.weather_icon = Label(self)
        # self.weather_icon.grid(row=4,column=0) 
        # self.forecast_icon = Label(self)

        self.weather_labels = []
        self.create_weather_labels(row = 2, column = 0, columnspan = 3)

##### This reloads the weather entirely, because the forecast day was changed in the popup menu #####
    def get_forecast_change(self, index, value, op): # what is the purpose for passing values - Karan
        if self.location_entry.get(): #setting the current value triggers the change, so we check to make sure there's a location
            self.get_weather()

##### This creates day names for future forecast days, starting with today and tomorrow
    def create_forecast_options(self):
        try:
            dt = datetime.now()
            day_chooser_values = [" Today's Forecast", " Tomorrow's Forecast"]
            dt += timedelta(days = 1)
            for i in range( 2, N_DAYS_FORECAST ):
                dt += timedelta(days = 1)
                if i >= 7:  #if it's a week away or more
                    day_chooser_values.append(f" Next {dt.strftime('%A')}'s Forecast") # say "next day"
                else:
                    day_chooser_values.append(f" {dt.strftime('%A')}'s Forecast") # otherwise just day
            return tuple(day_chooser_values)
        except Exception as e:
            messagebox.showerror("Error", f"Error creating forecast options: {e}")

    def create_weather_labels(self, row, column, columnspan): # Updated function - Karan
        labels = [ # List of dictionaries of labels with its respective values
            {"current_label" : "", # current label
            "row" : row, "column" : column, "columnspan" : columnspan}, 

            {"current_weather_icon" : "", # current weather icon
            "row" : row + 1, "column" : column, "columnspan" : columnspan}, 

            {"current_condition" : "", # current condition 
            "row" : row + 2,  "column" : column, "columnspan" : columnspan}, 

            {"current_temperature" : "", # current temperature 
            "row" : row + 3,  "column" : column, "columnspan" : columnspan}, 

            {"current_wind_speed" : "", # current wind speed 
            "row" : row + 4,  "column" : column, "columnspan" : columnspan}, 

            {"current_humidity" : "", # current humidity 
            "row" : row + 5,  "column" : column, "columnspan" : columnspan}, 

            {"spacer_1" : "", # Spacer label to create a gap between today's cast and forecast 
            "row" : row + 6,  "column" : column, "columnspan" : columnspan}, 

            {"forecast_icon" : "", # forecast icon 
            "row" : row + 7,  "column" : column, "columnspan" : columnspan}, 

            {"forecast_condition" : "", # forecast condition 
            "row" : row + 8,  "column" : column, "columnspan" : columnspan},

            {"forecast_max_temperature" : "", # forecast max temperature 
            "row" : row + 9,  "column" : column, "columnspan" : columnspan}, 

            {"forecast_min_temperature" : "", # forecast min temperature 
            "row" : row + 10, "column" : column, "columnspan" : columnspan}, 

            {"forecast_max_wind_speed" : "", # forecast wind speed 
            "row" : row + 11, "column" : column, "columnspan" : columnspan}, 

            {"forecast_avg_humidity" : "", # forecast humidity 
            "row" : row + 12, "column" : column, "columnspan" : columnspan}, 

            {"forecast_rain_chance" : "", # forecast rain chance 
            "row" : row + 13, "column" : column, "columnspan" : columnspan},  

            {"forecast_total_precipitation" : "", # forecast total precipitation 
            "row" : row + 14, "column" : column, "columnspan" : columnspan}
        ]

        for label_info in labels:
            label_name = list(label_info.keys())[0]
            label_text = label_info[label_name]
            label_row = label_info["row"]
            label_column = label_info["column"]
            label_columnspan = label_info["columnspan"]

            label = Label(self, text = label_text)
            label.grid(row = label_row, column = label_column, columnspan = label_columnspan, sticky = "nsew")
            print(f"{label_name} : {label}")
            self.weather_labels.append({label_name : label})

    def get_weather(self):
        try:
            location = self.location_entry.get()

            if not location:
                raise ValueError("Location Cannot be empty!")

            weather_data = WeatherData(API_KEY, N_DAYS_FORECAST, location)
            weather_data.fetch_data(self.forecast_day_chooser.current())

            current_weather = weather_data.get_current_weather()
            forecast_weather = weather_data.get_forecast_weather()

            self.update_all_labels(current_weather, forecast_weather)
        except ValueError as e:
            messagebox.showerror("Error", f"{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error geting weather: {e}")

    def update_all_labels(self, current_weather, forecast_weather):
        label_commands = [
            {"current_label"                : f"Current Weather"}, 
            {"current_weather_icon"         : f"http:{current_weather['condition']['icon']}"}, 
            {"current_condition"            : f"Current Condition: {current_weather['condition']['text']}"},
            {"current_temperature"          : f"Current Temperature: {current_weather['temp_f']}°F | {current_weather['temp_c']}°C"},
            {"current_wind_speed"           : f"Current Wind: {current_weather['wind_mph']}mph | {current_weather['wind_kph']}kph {current_weather['wind_dir']}"},
            {"current_humidity"             : f"Current Humidity: {current_weather['humidity']}%"},
            {"spacer_1"                     : f" "},
            {"forecast_icon"                : f"http:{forecast_weather['condition']['icon']}"},
            {"forecast_condition"           : f"Forecasted Condition: {forecast_weather['condition']['text']}"},
            {"forecast_max_temperature"     : f"Max Temperature: {forecast_weather['maxtemp_f']}°F | {forecast_weather['maxtemp_c']}°C"},
            {"forecast_min_temperature"     : f"Min Temperature: {forecast_weather['mintemp_f']}°F | {forecast_weather['mintemp_c']}°C"},
            {"forecast_max_wind_speed"      : f"Max Wind: {forecast_weather['maxwind_mph']}mph | {forecast_weather['maxwind_kph']}kph"},
            {"forecast_avg_humidity"        : f"Average Humidity: {forecast_weather['avghumidity']}%"},
            {"forecast_rain_chance"         : f"Chance of Rain: {forecast_weather['daily_chance_of_rain']}%"},
            {"forecast_total_precipitation" : f"Total Precipitation: {forecast_weather['totalprecip_in']}in | {forecast_weather['totalprecip_mm']}mm"}
        ]

        for label_info, update_command in zip(self.weather_labels, label_commands):
            label_name = list(label_info.keys())[0]
            label = label_info[label_name]
            update_command = update_command[label_name]

            if "http:" in update_command:
                self.update_icon_label(label, update_command)
            else:
                self.update_label(label, update_command) 

    def update_label(self, label, text):
        label.config(text = text)

    def update_icon_label(self, label, icon_url): # *Please check if this function is working as intended
        self.download_icon(icon_url, "temp_icon.png")
        icon = ImageTk.PhotoImage(file = "temp_icon.png")
        label.config(image = icon)
        label.image = icon

    def download_icon(self, url, filename):
        try:
            response = requests.get(url, stream = True)
            if response.status_code == 200:
                with open(filename, "wb") as f:
                    for chunk in response.iter_content(1024):
                        f.write(chunk)
            else:
                raise ValueError(f"Icon download request failed with status code {response.status_code}")
        except Exception as e:
            messagebox.showerror("Error", f"Error occurred downloading icon: {e}")

class WeatherData:
    def __init__(self, API_KEY, N_DAYS_FORECAST, location):
        self.API_KEY = API_KEY
        self.N_DAYS_FORECAST = N_DAYS_FORECAST
        self.location = location
        self.current_weather = []
        self.forecast_weather = []

    def fetch_data(self, day):
        try:
            url = f"http://api.weatherapi.com/v1/forecast.json?key={self.API_KEY}&q={self.location}&days={self.N_DAYS_FORECAST}&aqi=no&alerts=no"
            response = requests.get(url)
            if response.status_code == 200:
                weather_data = json.loads(response.content)
                self.current_weather = weather_data["current"]
                self.forecast_weather = weather_data["forecast"]["forecastday"][day]["day"]
            else:
                raise Exception(f"API request failed with status code {response.status_code}")
        except Exception as e:
            messagebox.showerror("Error", f"Error fetching weather data: {e}")

    def get_current_weather(self):
        return self.current_weather

    def get_forecast_weather(self):
        return self.forecast_weather

if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()
