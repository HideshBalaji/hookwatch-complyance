import csv
import random
import uuid
import os

filename = "datasets/large_upload.csv"
num_events = 2500 # Generate 2,500 unique events

endpoints = ["ep_001", "ep_002", "ep_003", "ep_004", "ep_005", "ep_006"]
customers = ["cust_010", "cust_020", "cust_030", "cust_040", "cust_050"]
event_types = ["invoice.paid", "user.created", "payment.failed", "subscription.canceled", "order.shipped"]

os.makedirs("datasets", exist_ok=True)

with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["event_id", "event_type", "customer_id", "endpoint_id", "attempt_number", "http_status", "response_time_ms", "timeout", "signature_valid"])
    
    total_rows = 0
    for i in range(num_events):
        event_id = f"evt_bulk_{uuid.uuid4().hex[:8]}"
        event_type = random.choice(event_types)
        customer_id = random.choice(customers)
        endpoint_id = random.choice(endpoints)
        
        # Determine how many attempts this event took (1 to 5)
        num_attempts = random.choices([1, 2, 3, 4, 5], weights=[60, 20, 10, 5, 5])[0]
        
        for attempt in range(1, num_attempts + 1):
            is_last = (attempt == num_attempts)
            
            # Simulate real-world failures and successes
            if is_last:
                # Last attempt mostly succeeds (80%), but sometimes permanently fails (20%)
                http_status = random.choice([200, 201, 200, 200, 500, 401]) 
            else:
                # Intermediate attempts are always failures
                http_status = random.choice([500, 502, 504, 429])
                
            timeout = str(http_status == 504).lower()
            sig_valid = str(http_status != 401).lower()
            resp_time = random.uniform(100, 400) if http_status in [200, 201] else random.uniform(1500, 6000)
            
            writer.writerow([
                event_id,
                event_type,
                customer_id,
                endpoint_id,
                attempt,
                http_status,
                round(resp_time, 2),
                timeout,
                sig_valid
            ])
            total_rows += 1

print(f"Generated {filename} successfully with {total_rows} rows!")
