
import datetime
import random

def generate_data(num_rows):
    header = ["Date", "Product", "Category", "Quantity", "Price", "Total"]
    data = [header]
    start_date = datetime.date(2023, 1, 1)

    for i in range(num_rows):
        current_date = start_date + datetime.timedelta(days=i)
        product = f"Product {i+1}"
        category = random.choice(["Category A", "Category B", "Category C"])
        quantity = random.randint(1, 10)
        price = round(random.uniform(1.00, 10.00), 2)
        # The total will be calculated by the excel formula
        data.append([current_date.strftime("%Y-%m-%d"), product, category, quantity, price, ""]) 
    return data

if __name__ == "__main__":
    num_rows = 123
    sales_data = generate_data(num_rows)
    
    # Print the data so the agent can read it
    for row in sales_data:
        print(row)
