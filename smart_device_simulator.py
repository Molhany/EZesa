
import time
import threading
import random
import requests

class SmartDeviceSimulator:
    def __init__(self, user_id, device_id, device_name, device_type, initial_balance):
        self.user_id = user_id
        self.device_id = device_id
        self.device_name = device_name
        self.device_type = device_type
        self.status = "off"
        self.energy_consumption = 0.0  # kWh
        self.energy_balance = initial_balance
        self.base_url = 'http://127.0.0.1:8000'  # Update this to your Django server URL if different
        self.running = False

        # Initialize device with initial balance in the application
        self.initialize_device_balance()

    def start(self):
        self.running = True
        self.status = "on"
        threading.Thread(target=self.simulate).start()

    def stop(self):
        self.running = False
        self.status = "off"

    def recharge(self, amount):
        self.energy_balance += amount
        requests.post(f'{self.base_url}/api/update_device_balance/{self.user_id}/{self.device_id}/', data={'balance': self.energy_balance})

    def initialize_device_balance(self):
        # Initialize the energy balance in the application
        requests.post(f'{self.base_url}/api/update_device_balance/{self.user_id}/{self.device_id}/', data={'balance': self.energy_balance})

    def update_status(self):
        # Simulate updating energy balance from the server
        response = requests.get(f'{self.base_url}/api/get_device_balance_and_status/{self.user_id}/{self.device_id}/')
        if response.status_code == 200:
            data = response.json()
            self.status = data['status']
            self.energy_balance = data['balance']
    
    def simulate(self):
        while self.running:
            self.update_status()
            if self.energy_balance > 0 and self.status == 'on':
                consumption = random.uniform(0.1, 0.5)
                self.energy_consumption += consumption
                self.energy_balance -= consumption
                requests.post(f'{self.base_url}/api/update_device_balance/{self.user_id}/{self.device_id}/', data={'consumption': consumption, 'status': self.status})
                time.sleep(1)  # Simulate real-time, can be adjusted for accelerated time
            else:
                print(f"Device {self.device_name} stopped due to no energy balance or status off.")
                self.stop()

    def get_status(self):
        return {
            "device_name": self.device_name,
            "status": self.status,
            "energy_consumption": self.energy_consumption,
            "energy_balance": self.energy_balance,
        }

if __name__ == "__main__":
    # Input device details
    user_id = int(input("Enter User ID: "))
    device_id = int(input("Enter Device ID: "))
    device_name = input("Enter Device Name: ")
    device_type = input("Enter Device Type: ")
    initial_balance = float(input("Enter Initial Energy Balance (kWh): "))

    device = SmartDeviceSimulator(user_id, device_id, device_name, device_type, initial_balance)
    device.start()
    try:
        while True:
            status = device.get_status()
            print(f"Device: {status['device_name']}, Type: {device.device_type}, Status: {status['status']}, Energy Consumption: {status['energy_consumption']} kWh, Energy Balance: {status['energy_balance']} kWh")
            time.sleep(2)
    except KeyboardInterrupt:
        device.stop()
        print("Simulation stopped.")