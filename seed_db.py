from app.models import prisma
import json
import os

def seed_database():
    """Seed the database with initial data"""
    try:
        # Check if destinations table is empty
        count = prisma.destination.count()
        if count > 0:
            print(f"Database already has {count} destinations. Skipping seeding.")
            return
        
        print("Seeding database with initial destinations...")
        
        # Load initial destinations from JSON file
        data_path = os.path.join(os.path.dirname(__file__), 'data', 'initial_destinations.json')
        with open(data_path, 'r') as f:
            destinations_data = json.load(f)
        
        for dest in destinations_data:
            name = f"{dest['city']}, {dest['country']}"
            fun_facts = dest.get('fun_fact', dest.get('fun_facts', []))
            
            print(f"Adding destination: {name}")
            prisma.destination.create(
                data={
                    "name": name,
                    "clues": dest["clues"],
                    "funFacts": fun_facts,
                    "trivia": dest["trivia"]
                }
            )
        
        print("Database seeding completed successfully")
    except Exception as e:
        print(f"Error seeding database: {str(e)}")

if __name__ == "__main__":
    seed_database() 