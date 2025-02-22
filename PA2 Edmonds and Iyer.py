# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 09:36:09 2025

@author: RIyer
"""

import random 

#edit to commit

# define constants in seconds
SECONDS_PER_ITEM = 1 # (from 4)
OVERHEAD_SECONDS = 10 # (from 45)
CUSTOMER_ARRIVAL_RATE = 4 # (from 30)
MIN_ITEMS = 6
MAX_ITEMS = 20 
SIMULATE_DURATION = 10 # 2 hours in seconds (from 7200)
STATUS_UPDATE_RATE = 1 # (from 50)
NUM_SIMULATIONS = 2 # (from 12)

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
            
def main():
    # Initialize lists to store per-register statistics across simulations
    num_registers = OG_NUMBER_REGISTERS  # Assume the first simulation gives the number of registers
    
    total_customers_per_register = [0] * num_registers
    total_items_per_register = [0] * num_registers
    total_idle_time_per_register = [0] * num_registers
    total_wait_time_per_register = [0] * num_registers
    
    print("Starting grocery store simulation...\n")
    
    # Run multiple simulations
    for _ in range(NUM_SIMULATIONS):
        registers = simulation()  # Run one simulation and get register data
        
        for i, register in enumerate(registers):
            total_customers_per_register[i] += register.total_customers_served
            total_items_per_register[i] += register.total_items_served
            total_idle_time_per_register[i] += register.idle_time
            total_wait_time_per_register[i] += register.wait_time
    
    # Compute averages for each register
    avg_customers_per_register = [total / NUM_SIMULATIONS for total in total_customers_per_register]
    avg_items_per_register = [total / NUM_SIMULATIONS for total in total_items_per_register]
    avg_idle_time_per_register = [total / NUM_SIMULATIONS for total in total_idle_time_per_register]
    avg_wait_time_per_register = [total / NUM_SIMULATIONS for total in total_wait_time_per_register]
    
    # Compute overall totals and averages
    total_customers = sum(total_customers_per_register)
    total_items = sum(total_items_per_register)
    total_idle_time = sum(total_idle_time_per_register)
    total_wait_time = sum(total_wait_time_per_register)
    
    avg_total_customers = total_customers / NUM_SIMULATIONS
    avg_total_items = total_items / NUM_SIMULATIONS
    avg_total_idle_time = total_idle_time / NUM_SIMULATIONS
    avg_total_wait_time = total_wait_time / max(1, total_customers)  # Avoid division by zero
    
    # Store results in a list
    results = []
    results.append(f"\nSimulation Summary with 5 Registers (Averages per Register over {NUM_SIMULATIONS} Simulations):")
    results.append(f"{'Register':<10}{'Avg Customers':<18}{'Avg Items':<15}{'Idle Time (min)':<18}{'Avg Wait Time (sec)':<20}")
    results.append("-" * 80)
    
    for i in range(num_registers):
        register_name = "Express" if i == num_registers - 1 else str(i + 1)
        idle_time_min = avg_idle_time_per_register[i] / 60
        avg_wait_time = avg_wait_time_per_register[i] / max(1, avg_customers_per_register[i])  # Avoid division by zero
        
        results.append(f"{register_name:<10}{avg_customers_per_register[i]:<18.2f}{avg_items_per_register[i]:<15.2f}{idle_time_min:<18.2f}{avg_wait_time:<20.2f}")
    
    # Print overall totals
    total_idle_time_min = avg_total_idle_time / 60
    results.append("-" * 80)
    results.append(f"{'Total':<10}{avg_total_customers:<18.2f}{avg_total_items:<15.2f}{total_idle_time_min:<18.2f}{avg_total_wait_time:<20.2f}")
    
    # Function to print the stored results
    def print_results():
        for line in results:
            print(line)
    
    
    




    
    ###############################################################################################################
    # Compare results with a 6th non-express register
    print("\nRunning Simulation with 6th Non-Express Register...")
    
    # Initialize lists to store per-register statistics across simulations
    num_registers_extra = EXTRA_NUMBER_REGISTERS  # Get number of registers with extra
    
    total_customers_per_register_extra = [0] * num_registers_extra
    total_items_per_register_extra = [0] * num_registers_extra
    total_idle_time_per_register_extra = [0] * num_registers_extra
    total_wait_time_per_register_extra = [0] * num_registers_extra
    
    # Run multiple simulations with the extra register
    for _ in range(NUM_SIMULATIONS):
        registers = simulation(extra_register=True)  # Run one simulation with 6 registers
    
        for i, register in enumerate(registers):
            total_customers_per_register_extra[i] += register.total_customers_served
            total_items_per_register_extra[i] += register.total_items_served
            total_idle_time_per_register_extra[i] += register.idle_time
            total_wait_time_per_register_extra[i] += register.wait_time
    
    # Compute averages for each register
    avg_customers_per_register_extra = [total / NUM_SIMULATIONS for total in total_customers_per_register_extra]
    avg_items_per_register_extra = [total / NUM_SIMULATIONS for total in total_items_per_register_extra]
    avg_idle_time_per_register_extra = [total / NUM_SIMULATIONS for total in total_idle_time_per_register_extra]
    avg_wait_time_per_register_extra = [total / NUM_SIMULATIONS for total in total_wait_time_per_register_extra]
    
    # Compute overall totals and averages
    total_customers_extra = sum(total_customers_per_register_extra)
    total_items_extra = sum(total_items_per_register_extra)
    total_idle_time_extra = sum(total_idle_time_per_register_extra)
    total_wait_time_extra = sum(total_wait_time_per_register_extra)
    
    avg_total_customers_extra = total_customers_extra / NUM_SIMULATIONS
    avg_total_items_extra = total_items_extra / NUM_SIMULATIONS
    avg_total_idle_time_extra = total_idle_time_extra / NUM_SIMULATIONS
    avg_total_wait_time_extra = total_wait_time_extra / max(1, total_customers_extra)  # Avoid division by zero
    
    # Print results
    print(f"\nSimulation Summary with 6 Registers (Averages per Register over {NUM_SIMULATIONS} Simulations):")
    print(f"{'Register':<10}{'Avg Customers':<18}{'Avg Items':<15}{'Idle Time (min)':<18}{'Avg Wait Time (sec)':<20}")
    print("-" * 85)
    
    for i in range(num_registers_extra):
        register_name = "Express" if i == num_registers_extra - 1 else str(i + 1)
        idle_time_min = avg_idle_time_per_register_extra[i] / 60
        avg_wait_time = avg_wait_time_per_register_extra[i] / max(1, avg_customers_per_register_extra[i])  # Avoid division by zero
    
        print(f"{register_name:<10}{avg_customers_per_register_extra[i]:<18.2f}{avg_items_per_register_extra[i]:<15.2f}{idle_time_min:<18.2f}{avg_wait_time:<20.2f}")
    
    # Print overall totals
    total_idle_time_min_extra = avg_total_idle_time_extra / 60
    
    print("-" * 85)
    print(f"{'Total':<10}{avg_total_customers_extra:<18.2f}{avg_total_items_extra:<15.2f}{total_idle_time_min_extra:<18.2f}{avg_total_wait_time_extra:<20.2f}")
    print_results()
    
    print("\nSimulation complete.")
    


# Ensure the script runs when executed directly
if __name__ == "__main__":
    main()



            