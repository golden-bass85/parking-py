import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import time
import re
import sqlite3

class ParkingApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Parking Slot")
        self.window.geometry('1920x1200')

        # Connect to the SQLite database
        self.conn = sqlite3.connect('parking.db')
        self.cursor = self.conn.cursor()

        # Create table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS parking_slots (
                slot TEXT PRIMARY KEY,
                vehicle_number TEXT,
                time_of_parking REAL,
                slot_type TEXT
            )
        """)

        # Load parking slots from the database
        self.parking_slots = {f"Slot {i+1}": (None, None, "Car" if i < 90 else "Motorcycle") for i in range(100)}
        self.cursor.execute("SELECT * FROM parking_slots")
        for slot, vehicle_number, time_of_parking, slot_type in self.cursor.fetchall():
            self.parking_slots[slot] = (vehicle_number, time_of_parking, slot_type)

        # Define parking slots
        self.parking_slots = {f"Slot {i+1}": (None, None, "Car" if i < 90 else "Motorcycle") for i in range(100)}

        # Create listboxes for the parking slots
        self.parking_listboxes = [self.create_listbox({key: value for key, value in list(self.parking_slots.items())[i*10:(i+1)*10]}, 2, i) for i in range(10)]

        # Create entries for vehicle number
        tk.Label(self.window, text="Vehicle Number").grid(row=3, column=0)
        self.vehicle_number_entry = tk.Entry(self.window)
        self.vehicle_number_entry.grid(row=3, column=1)
        # Add clear all button
        tk.Button(self.window, text="Clear All", command=self.clear_all).grid(row=13, column=2, columnspan=2)

        # Create dropdown for vehicle type
        self.vehicle_type = tk.StringVar()
        self.vehicle_type.set("Car")
        tk.OptionMenu(self.window, self.vehicle_type, "Car", "Motorcycle").grid(row=3, column=3)

        # Create title label
        title_label = tk.Label(self.window, text="safe parking", font=("Helvetica", 24, "bold"), fg="green")
        title_label.grid(row=0, column=4, columnspan=2)

        # Create button to park vehicle
        tk.Button(self.window, text="Park", command=self.park_vehicle).grid(row=3, column=2, columnspan=2)

        # Create entries for vehicle number
        tk.Label(self.window, text="Vehicle Number").grid(row=4, column=0)
        self.vehicle_number_leave_entry = tk.Entry(self.window)
        self.vehicle_number_leave_entry.grid(row=4, column=1)

        # Create button to unpark vehicle
        tk.Button(self.window, text="Unpark", command=self.unpark_vehicle).grid(row=4, column=2, columnspan=2)

        # Create button to find free slot for cars
        tk.Button(self.window, text="Find Free Car Slot", command=self.find_free_car_slot).grid(row=9, column=0, columnspan=2)

        # Create button to find free slot for motorcycles
        tk.Button(self.window, text="Find Free Motorcycle Slot", command=self.find_free_motorcycle_slot).grid(row=9, column=2, columnspan=2)

        # Create entries for vehicle number reservation
        tk.Label(self.window, text="Vehicle Number").grid(row=5, column=0)
        self.vehicle_number_reserve_entry = tk.Entry(self.window)
        self.vehicle_number_reserve_entry.grid(row=5, column=1)

        # Create button to reserve slot
        tk.Button(self.window, text="Reserve Slot", command=self.reserve_slot).grid(row=5, column=2, columnspan=2)

        # Create entries for vehicle number for confirming reserved slot
        tk.Label(self.window, text="Vehicle Number").grid(row=7, column=0)
        self.reserved_vehicle_number_entry = tk.Entry(self.window)
        self.reserved_vehicle_number_entry.grid(row=7, column=1)

        # Create button for confirming reserved slot
        tk.Button(self.window, text="I have a Reserved Slot", command=self.confirm_reserved_slot).grid(row=7, column=2, columnspan=2)

        # Create label to display total time and price
        self.total_time_label = tk.Label(self.window, text="Total Time: 0 minutes")
        self.total_time_label.grid(row=11, column=0, columnspan=2)

        self.total_price_label = tk.Label(self.window, text="Total Price: 0 birr")
        self.total_price_label.grid(row=12, column=0, columnspan=2)

        # Schedule updates and checks
        self.window.after(60000, self.check_parking_time)

        # Create the reviews listbox
        self.reviews_listbox = tk.Listbox(self.window, height=15, width=30)
        self.reviews_listbox.grid(row=24, column=8)

        # Create button to update reviews
        tk.Button(self.window, text="Update Reviews", command=self.update_reviews_listbox).grid(row=25, column=8)

        # Create button to clear reviews
        tk.Button(self.window, text="Clear Reviews", command=self.clear_reviews).grid(row=26, column=8)

        # Schedule updates and checks
        self.window.after(60000, self.check_parking_time)

    def update_reviews_listbox(self):
        # Calculate total cars parked and total money gained
        total_cars_parked = sum(1 for _, (vehicle_number, _, _) in self.parking_slots.items() if vehicle_number is not None)
    
        total_money_gained = 0
        current_time = time.time()
        for _, (vehicle_number, time_of_parking, _) in self.parking_slots.items():
            if vehicle_number is not None:
                if time_of_parking is not None:
                    duration_seconds = current_time - time_of_parking
                    duration_minutes = duration_seconds / 60  # Convert to minutes
                    rounded_duration_minutes = int(duration_minutes)  # Rounded to the nearest minute
                    if duration_seconds % 60 >= 1:  # If there are seconds left, round up
                        rounded_duration_minutes += 1
                    money_gained = rounded_duration_minutes * 10  # Assuming 10 birr per minute
                    total_money_gained += money_gained

        # Clear previous contents
        self.reviews_listbox.delete(0, tk.END)

        # Add new contents
        self.reviews_listbox.insert(tk.END, f"Total Cars Parked: {total_cars_parked}")
        self.reviews_listbox.insert(tk.END, f"Total Money Gained: {total_money_gained:.2f} birr")



    def clear_reviews(self):
        # Clear the contents of the reviews listbox
        self.reviews_listbox.delete(0, tk.END)
    
        
    def create_listbox(self, items, row, column):
        listbox = tk.Listbox(self.window, width=20)
        for item, (vehicle_number, time_of_parking, slot_type) in items.items():
            listbox.insert(tk.END, f"{item}: {vehicle_number if vehicle_number else 'Free'}")
        listbox.grid(row=row, column=column)
        return listbox
    



    def park_vehicle(self):
        vehicle_number = self.vehicle_number_entry.get()
        if not vehicle_number:
            messagebox.showerror("Error", "Please enter a valid vehicle number which contains a number between 1 and 90 for car and between 1 and 10 for .")
            return
        if not vehicle_number.isdigit():
            messagebox.showerror("Error", "Vehicle number can only contain digits.")
            return
        vehicle_type = self.vehicle_type.get()
        if vehicle_type == "Car":
            vehicle_number = str(vehicle_number).zfill(3)  # Ensure 3 digits for car numbers
        elif vehicle_type == "Motorcycle":
            vehicle_number = "1" + str(vehicle_number).zfill(2)  # Ensure 2 digits for motorcycle numbers

        # Check if the vehicle is already parked
        for slot, (parked_vehicle_number, _, _) in self.parking_slots.items():
            if parked_vehicle_number == vehicle_number:
                messagebox.showerror("Error", "This vehicle is already parked.")
                return

        for listbox in self.parking_listboxes:
            selected_slot = listbox.curselection()
            if selected_slot:
                slot = listbox.get(selected_slot).split(':')[0].strip()
                time_of_parking = time.time()  # Get current time
                if self.parking_slots[slot][0] is not None and self.parking_slots[slot][0] != "Reserved":
                    messagebox.showerror("Error", "This slot is already occupied.")
                elif self.parking_slots[slot][2] != vehicle_type:
                    messagebox.showerror("Error", "This slot is not suitable for your vehicle type.")
                else:
                    self.parking_slots[slot] = (vehicle_number, time_of_parking, vehicle_type)
                    listbox.delete(selected_slot)
                    listbox.insert(selected_slot, f"{slot}: {vehicle_number}")
                    messagebox.showinfo("Parking Successful", "The vehicle has been parked successfully.")
                    self.vehicle_number_entry.delete(0, tk.END)
                break
        else:
            messagebox.showerror("Error", "Please select a parking slot.")

        # Update the database
        self.cursor.execute("INSERT OR REPLACE INTO parking_slots VALUES (?, ?, ?, ?)",
                            (slot, vehicle_number, time_of_parking, vehicle_type))
        self.conn.commit()

    
    def reserve_slot(self):
        vehicle_number = self.vehicle_number_reserve_entry.get()
        if not vehicle_number:
            messagebox.showerror("Error", "Please enter a vehicle number.")
            return
        if not vehicle_number.isdigit():
            messagebox.showerror("Error", "Vehicle number can only contain digits.")
            return
    
        padded_vehicle_number = vehicle_number.zfill(3) if self.vehicle_type.get() == "Car" else vehicle_number.zfill(2)
    
        # Check if the vehicle number is already parked
        for _, (parked_vehicle_number, _, _) in self.parking_slots.items():
            if parked_vehicle_number is not None:
                # Adjust the comparison to handle padding zeros
                if int(parked_vehicle_number) == int(padded_vehicle_number):
                    messagebox.showerror("Error", "This vehicle is already parked.")
                    return

        for slot, (parked_vehicle_number, _, _) in self.parking_slots.items():
            if parked_vehicle_number is None:
                if slot.startswith("Slot "):
                    self.parking_slots[slot] = (padded_vehicle_number, None, self.parking_slots[slot][2])
                    messagebox.showinfo("Info", f"Slot {slot} reserved for vehicle {padded_vehicle_number}")
                    self.vehicle_number_reserve_entry.delete(0, tk.END)
                    return
        messagebox.showerror("Error", "No free slot available for reservation.")

        # Update the database
        self.cursor.execute("INSERT OR REPLACE INTO parking_slots VALUES (?, ?, ?, ?)",
                            (slot, padded_vehicle_number, None, self.parking_slots[slot][2]))
        self.conn.commit()




    
    def clear_all(self):
    # Clear all entry fields
        self.vehicle_number_entry.delete(0, tk.END)
        self.vehicle_number_leave_entry.delete(0, tk.END)
        self.vehicle_number_reserve_entry.delete(0, tk.END)
        self.reserved_vehicle_number_entry.delete(0, tk.END)
    # Reset parking slots to default values
        self.parking_slots = {f"Slot {i+1}": (None, None, "Car" if i < 90 else "Motorcycle") for i in range(100)}
    # Update listboxes
        for listbox in self.parking_listboxes:
            listbox.delete(0, tk.END)
            for item, (vehicle_number, _, _) in self.parking_slots.items():
                listbox.insert(tk.END, f"{item}: {vehicle_number if vehicle_number else 'Free'}")



    def find_free_car_slot(self):
        for i, (slot, (vehicle_number, _, _)) in enumerate(self.parking_slots.items()):
            if vehicle_number is None and i < 90:
                self.parking_listboxes[i//10].selection_clear(0, tk.END)
                self.parking_listboxes[i//10].selection_set(i%10)
                messagebox.showinfo("Info", f"Free car slot found: {slot}")
                break
        else:
            messagebox.showinfo("Info", "No free car slots available.")

    def find_free_motorcycle_slot(self):
        for i, (slot, (vehicle_number, _, _)) in enumerate(self.parking_slots.items()):
            if vehicle_number is None and i >= 90:
                self.parking_listboxes[i//10].selection_clear(0, tk.END)
                self.parking_listboxes[i//10].selection_set(i%10)
                messagebox.showinfo("Info", f"Free motorcycle slot found: {slot}")
                break
        else:
            messagebox.showinfo("Info", "No free motorcycle slots available.")

    def check_parking_time(self):
        current_time = time.time()
        for slot, (vehicle_number, time_of_parking, _) in self.parking_slots.items():
            if vehicle_number is not None and time_of_parking is not None:
                if current_time - time_of_parking > 3600:  # 1 hour
                    messagebox.showwarning("Warning", f"Vehicle {vehicle_number} has been parked for more than 1 hour")
        self.window.after(60000, self.check_parking_time)  # Check every minute

    def unpark_vehicle(self):
        vehicle_number = self.vehicle_number_leave_entry.get()
        if not vehicle_number:
            messagebox.showerror("Error", "Please enter a vehicle number.")
            return
        if not vehicle_number.isdigit():
            messagebox.showerror("Error", "Vehicle number can only contain digits.")
            return

        time_of_leaving = time.time()  # Get current time
        for i, (slot, (parked_vehicle_number, time_of_parking, _)) in enumerate(self.parking_slots.items()):
            # Adjust the comparison to handle padded zeros
            if parked_vehicle_number == vehicle_number.zfill(3):
                if time_of_parking is None:
                    messagebox.showerror("Error", "Vehicle not parked.")
                    return
            
                time_parked_minutes = (time_of_leaving - time_of_parking) / 60  # Convert to minutes
                time_parked_seconds = (time_parked_minutes % 1) * 60  # Extract seconds from remaining minutes
                total_time = f"{int(time_parked_minutes)} minutes, {int(time_parked_seconds)} seconds"
                total_price = int(time_parked_minutes) * 10  # 10 birr per minute
            
                self.total_time_label.config(text=f"Total Time: {total_time}")
                self.total_price_label.config(text=f"Total Price: {total_price} birr")
                self.parking_slots[slot] = (None, None, self.parking_slots[slot][2])
                self.parking_listboxes[i//10].delete(i%10)
                self.parking_listboxes[i//10].insert(i%10, f"{slot}: Free")
                messagebox.showinfo("Unparking Successful", "The vehicle has been unparked successfully.")
                self.vehicle_number_leave_entry.delete(0, tk.END)
                break
        else:
            messagebox.showerror("Error", "Vehicle number not found.")

        # Update the database
        self.cursor.execute("DELETE FROM parking_slots WHERE slot = ?", (slot,))
        self.conn.commit()


    def confirm_reserved_slot(self):
        vehicle_number = self.reserved_vehicle_number_entry.get()
        if not vehicle_number:
            messagebox.showerror("Error", "Please enter a vehicle number.")
            return
        if not vehicle_number.isdigit():
            messagebox.showerror("Error", "Vehicle number can only contain digits.")
            return

        # Adjust the comparison to handle padded zeros
        vehicle_number_padded = vehicle_number.zfill(3)
        reserved_slot = None
        for slot, (parked_vehicle_number, _, _) in self.parking_slots.items():
            if parked_vehicle_number == vehicle_number_padded:
                reserved_slot = slot
                break
        if reserved_slot:
            messagebox.showinfo("Info", f"Slot {reserved_slot} is reserved for vehicle {vehicle_number_padded}")
            self.parking_slots[reserved_slot] = (None, None, self.parking_slots[reserved_slot][2])  # Change slot status to free
            self.reserved_vehicle_number_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", f"No reserved slot found for vehicle {vehicle_number_padded}.")

        # Update the database
        self.cursor.execute("DELETE FROM parking_slots WHERE slot = ?", (reserved_slot,))
        self.conn.commit()


if __name__ == "__main__":
    window = tk.Tk()
    ParkingApp(window)
    window.mainloop()
