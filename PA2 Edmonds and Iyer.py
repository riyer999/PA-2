# -*- coding: utf-8 -*-
"""
Created on Wed Feb 19 09:36:09 2025

@author: RIyer
"""

import random 
import time 
import datetime

#edit to commit

# define constants in seconds
SECONDS_PER_ITEM = 2 # (from 4)
OVERHEAD_SECONDS = 1 # (from 45)
CUSTOMER_ARRIVAL_RATE = 4 # (from 30)
MIN_ITEMS = 6
MAX_ITEMS = 20 
SIMULATE_DURATION = 100 # 2 hours in seconds (from 7200)
STATUS_UPDATE_RATE = 1 # (from 50)
NUM_SIMULATIONS = 2 # (from 12)

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
    # Store statistics for analysis
    total_customers_served = []
    total_items_processed = []
    total_idle_time = []
    total_wait_time = []
    
    print("Starting grocery store simulation...\n")

    for _ in range(NUM_SIMULATIONS):
        registers = simulation()  # Run a simulation and collect register data
        
        # Collect statistics from all registers
        total_customers_served.append(sum(r.total_customers_served for r in registers))
        total_items_processed.append(sum(r.total_items_served for r in registers))
        total_idle_time.append(sum(r.idle_time for r in registers))
        total_wait_time.append(sum(r.wait_time for r in registers))
    
    # Calculate averages
    avg_customers_served = sum(total_customers_served) / NUM_SIMULATIONS
    avg_items_processed = sum(total_items_processed) / NUM_SIMULATIONS
    avg_idle_time = sum(total_idle_time) / NUM_SIMULATIONS
    avg_wait_time = sum(total_wait_time) / NUM_SIMULATIONS
    
    # Display results
    print("\nSimulation Summary (Averages over 12 runs):")
    print(f"Average Customers Served: {avg_customers_served:.2f}")
    print(f"Average Items Processed: {avg_items_processed:.2f}")
    print(f"Average Idle Time: {avg_idle_time:.2f} seconds")
    print(f"Average Wait Time: {avg_wait_time:.2f} seconds")
    
    # Final results table
    print("\nFinal Simulation Results:")
    print(f"{'Register':<10}{'Total Customers':<18}{'Total Items':<15}{'Idle Time (min)':<18}{'Avg Wait Time (sec)':<20}")
    print("-" * 80)
    
    total_customers = 0
    total_items = 0
    total_idle_time = 0
    total_wait_time = 0

    for i, register in enumerate(registers):
        register_name = "Express" if i == len(registers) - 1 else str(i + 1)
        idle_time_min = register.idle_time / 60
        avg_wait_time = register.wait_time / max(1, register.total_customers_served)  # Avoid division by zero
        
        print(f"{register_name:<10}{register.total_customers_served:<18}{register.total_items_served:<15}{idle_time_min:<18.2f}{avg_wait_time:<20.2f}")
        
        total_customers += register.total_customers_served
        total_items += register.total_items_served
        total_idle_time += register.idle_time
        total_wait_time += register.wait_time

    total_idle_time_min = total_idle_time / 60
    avg_total_wait_time = total_wait_time / max(1, total_customers)  # Avoid division by zero
    
    print("-" * 80)
    print(f"{'Total':<10}{total_customers:<18}{total_items:<15}{total_idle_time_min:<18.2f}{avg_total_wait_time:<20.2f}")
    
    # Compare results with a 6th non-express register
    print("\nRunning Simulation with 6th Non-Express Register...")
    registers = simulation(extra_register=True)  # Modify simulation to handle extra register
    
    extra_customers_served = sum(r.total_customers_served for r in registers)
    extra_items_processed = sum(r.total_items_served for r in registers)
    extra_idle_time = sum(r.idle_time for r in registers)
    extra_wait_time = sum(r.wait_time for r in registers)
    
    print("\nComparison with 6 Registers:")
    print(f"Total Customers Served: {extra_customers_served} (vs {avg_customers_served:.2f})")
    print(f"Total Items Processed: {extra_items_processed} (vs {avg_items_processed:.2f})")
    print(f"Total Idle Time: {extra_idle_time} seconds (vs {avg_idle_time:.2f})")
    print(f"Total Wait Time: {extra_wait_time} seconds (vs {avg_wait_time:.2f})")
    
    print("\nSimulation complete.")
    
# Ensure the script runs when executed directly
if __name__ == "__main__":
    main()



            