import csv
import random
from datetime import datetime, timedelta

def generate_mock_data(filename: str, num_records: int = 15000):
    print(f"Generating {num_records} records in {filename}...")
    statuses = ['pending', 'completed', 'failed']
    
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'name', 'email', 'amount', 'status', 'created_at'])
        
        for i in range(1, num_records + 1):
            name = f"User {i}"
            email = f"user{i}@example.com"
            amount = round(random.uniform(10.0, 5000.0), 2)
            status = random.choice(statuses)
            created_at = (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat()
            
            # Inject bad data roughly 3% of the time to demonstrate validation handling
            if random.random() < 0.01:
                email = "invalid-email" # will fail validation
            if random.random() < 0.01:
                amount = -10.0 # will fail validation
            if random.random() < 0.01:
                status = "unknown" # will fail validation
                
            writer.writerow([i, name, email, amount, status, created_at])
            
    print("Data generation complete.")

if __name__ == "__main__":
    generate_mock_data("mock_data.csv")
