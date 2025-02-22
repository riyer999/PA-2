# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 09:36:09 2025

@author: RIyer 
@author: LAEdmonds
"""

import random 

# define constants in seconds
SECONDS_PER_ITEM = 4 # (from 4)
OVERHEAD_SECONDS = 45 # (from 45)
CUSTOMER_ARRIVAL_RATE = 30 # (from 30)
MIN_ITEMS = 6
MAX_ITEMS = 20 
SIMULATE_DURATION = 7200 # 2 hours in seconds (from 7200)
STATUS_UPDATE_RATE = 50 # (from 50)
NUM_SIMULATIONS = 12 # (from 12)

OG_NUMBER_REGISTERS = 5
EXTRA_NUMBER_REGISTERS = 6

# Define classes
class Queue:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return self.items == []
    
    def enqueue(self, item):
        self.items.insert(0,item)

    def dequeue(self):
        return self.items.pop()

    def size(self):
        return len(self.items)
    
class Customer:
    def __init__(self, num_items, arrival_time):
        self.num_items = num_items
        self.arrival_time = arrival_time
        self.checkout_time = (num_items * SECONDS_PER_ITEM) + OVERHEAD_SECONDS
    
class Register:
    def __init__(self):
        self.queue = Queue() # Initialize an empty queue
        self.current_customer = None
        self.idle_time = 0
        self.wait_time = 0
        self.total_customers_served = 0
        self.total_items_served = 0
        
    def add_customer(self, customer): # Add customer to register queue if empty
        if self.current_customer is None:
            self.current_customer = customer
        else:
            self.queue.enqueue(customer)
        
    def serve_customer(self): # Increment down checkout time
        if self.current_customer:
            self.current_customer.checkout_time -= 1
        
            if self.current_customer.checkout_time <= 0: # When customer is done
                self.total_customers_served += 1 
                self.total_items_served += self.current_customer.num_items # Increment total num_items
                self.current_customer = None  # Register is free
                
                if not self.queue.isEmpty():
                    self.current_customer = self.queue.dequeue() 
            else:
                self.idle_time += 1 # Count idle time 
                
    def update_wait_time(self):
        if not self.queue.isEmpty():
            self.wait_time += self.queue.size() # Adjusting wait time depending on queue size
            
def simulation(extra_register=False): # Later be able to use the extra register
    NUM_REGISTERS = 4
    EXPRESS_REGISTER = 1
    if extra_register:
        NUM_REGISTERS += 1  # Add a 6th non-express register
    TOTAL_REGISTERS = NUM_REGISTERS + EXPRESS_REGISTER
    
    registers = [Register() for _ in range(TOTAL_REGISTERS)] # Create instances of the Register() class
    
    def find_shortest_register(registers):
        """Finds the best available register, prioritizing empty ones."""
        empty_registers = [r for r in registers if r.current_customer is None and r.queue.isEmpty()]
        if empty_registers:
            return random.choice(empty_registers)  # Prioritize empty registers
        
        # If no empty register, fall back to shortest queue
        min_size = min(r.queue.size() for r in registers)
        shortest_registers = [r for r in registers if r.queue.size() == min_size]
        return random.choice(shortest_registers)

    
    for current_time in range(SIMULATE_DURATION):
        for register in registers:
            register.serve_customer()
            register.update_wait_time()
            
        if current_time % CUSTOMER_ARRIVAL_RATE == 0:  # New customer every 30s
            num_items = random.randint(MIN_ITEMS, MAX_ITEMS)
            customer = Customer(num_items, arrival_time=current_time)
    
            if num_items < 10: # Customers eligible for the express line
                if registers[-1].current_customer is None:  # Express line empty
                    registers[-1].add_customer(customer)
                else:
                    find_shortest_register(registers).add_customer(customer)
            else: # Customers not eligible for the express line
                find_shortest_register(registers[:-1]).add_customer(customer)  # Exclude express
    
        

        if current_time % STATUS_UPDATE_RATE == 0: # Update every 50s
            print(f"Time: {current_time} seconds")
            for i, register in enumerate(registers): # Iterate through all the registers in registers list
                queue_status = " | " + " ".join(str(c.num_items) for c in register.queue.items) if not register.queue.isEmpty() else ""
                current = str(register.current_customer.num_items) if register.current_customer else "--"
                print(f"Register {i+1}: {current}{queue_status}")
            print("-" * 40) # Seperate every update with hyphens
    
    return registers
            
def run_simulation(num_registers, extra_register=False):
    total_customers = [0] * num_registers
    total_items = [0] * num_registers
    total_idle_time = [0] * num_registers
    total_wait_time = [0] * num_registers
    
    for _ in range(NUM_SIMULATIONS):
        registers = simulation(extra_register=extra_register)
        
        for i, register in enumerate(registers):
            total_customers[i] += register.total_customers_served
            total_items[i] += register.total_items_served
            total_idle_time[i] += register.idle_time
            total_wait_time[i] += register.wait_time
    
    avg_customers = [total / NUM_SIMULATIONS for total in total_customers]
    avg_items = [total / NUM_SIMULATIONS for total in total_items]
    avg_idle_time = [total / NUM_SIMULATIONS for total in total_idle_time]
    avg_wait_time = [total / NUM_SIMULATIONS for total in total_wait_time]
    
    total_customers_sum = sum(total_customers)
    total_items_sum = sum(total_items)
    total_idle_time_sum = sum(total_idle_time)
    total_wait_time_sum = sum(total_wait_time)
    
    avg_total_customers = total_customers_sum / NUM_SIMULATIONS
    avg_total_items = total_items_sum / NUM_SIMULATIONS
    avg_total_idle_time = total_idle_time_sum / NUM_SIMULATIONS
    #avg_total_wait_time = total_wait_time_sum / max(1, total_customers_sum)  # Avoid division by zero
    avg_total_wait_time = total_wait_time_sum / total_customers_sum  # Avoid division by zero
    
    return avg_customers, avg_items, avg_idle_time, avg_wait_time, avg_total_customers, avg_total_items, avg_total_idle_time, avg_total_wait_time, num_registers

def print_results(title, avg_customers, avg_items, avg_idle_time, avg_wait_time, avg_total_customers, avg_total_items, avg_total_idle_time, avg_total_wait_time, num_registers):
    print(f"\n{title} (Averages per Register over {NUM_SIMULATIONS} Simulations):")
    print(f"{'Register':<10}{'Avg Customers':<18}{'Avg Items':<15}{'Idle Time (min)':<18}{'Avg Wait Time (sec)':<20}")
    print("-" * 85)
    
    for i in range(num_registers):
        register_name = "Express" if i == num_registers - 1 else str(i + 1)
        idle_time_min = avg_idle_time[i] / 60
        avg_wait_time_per_customer = avg_wait_time[i] / max(1, avg_customers[i])
        print(f"{register_name:<10}{avg_customers[i]:<18.2f}{avg_items[i]:<15.2f}{idle_time_min:<18.2f}{avg_wait_time_per_customer:<20.2f}")
    
    total_idle_time_min = avg_total_idle_time / 60
    print("-" * 85)
    print(f"{'Total':<10}{avg_total_customers:<18.2f}{avg_total_items:<15.2f}{total_idle_time_min:<18.2f}{avg_total_wait_time:<20.2f}")

def main():
    print("Starting grocery store simulation...\n")
    
    # Run simulation with 5 registers
    results_5 = run_simulation(OG_NUMBER_REGISTERS)
    print_results("Simulation Summary with 5 Registers", *results_5)
    
    # Run simulation with 6 registers
    print("\nRunning Simulation with 6th Non-Express Register...")
    results_6 = run_simulation(EXTRA_NUMBER_REGISTERS, extra_register=True)
    print_results("Simulation Summary with 6 Registers", *results_6)
    print_results("Simulation Summary with 5 Registers", *results_5)

    
    print("\nSimulation complete.")

# Ensure the script runs when executed directly
if __name__ == "__main__":
    main()



            