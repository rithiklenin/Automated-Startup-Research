import os
import asyncio
import logging
from app.services.database import DatabaseService
from app.services.research_service import ResearchService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def reset_database():
    print("Resetting database...")
    
    try:
        if os.path.exists("startups.db"):
            os.remove("startups.db")
            print("Deleted existing database file")
    except Exception as e:
        print(f"Error deleting database file: {e}")
    
    db_service = DatabaseService()
    research_service = ResearchService(db_service)
    
    startups = [
        "Apple Inc.",
        "Microsoft Corporation",
        "Tesla, Inc.",
        "Netflix, Inc.",
        "Airbnb, Inc.",
        "OpenAI LP",
        "Stripe, Inc."
    ]
    
    print(f"Researching {len(startups)} startups...")
    
    results = await research_service.research_startups(startups)
    
    print("Database reset complete. Results:")
    for startup in results:
        print(f"- {startup.name} ({startup.id})")
        if startup.industry:
            print(f"  Industry: {', '.join(startup.industry)}")
        if startup.funding:
            try:
                total_funding = 0
                for key, val in startup.funding.items():
                    try:
                        if isinstance(val, (int, float)):
                            total_funding += float(val)
                        elif isinstance(val, str) and val.replace('.', '', 1).isdigit():
                            total_funding += float(val)
                        elif isinstance(val, str) and val.startswith('$'):
                            num_str = val.replace('$', '').replace(',', '')
                            if num_str.endswith('M'):
                                total_funding += float(num_str[:-1]) * 1000000
                            elif num_str.endswith('B'):
                                total_funding += float(num_str[:-1]) * 1000000000
                            else:
                                total_funding += float(num_str)
                    except (ValueError, TypeError):
                        print(f"  Note: Skipped non-numeric funding value '{val}' for {key}")
                        
                print(f"  Total funding: ${total_funding:,.2f}")
            except Exception as e:
                print(f"  Unable to calculate total funding: {e}")
                print(f"  Funding data: {startup.funding}")
    
    print("\nDatabase is now populated with default startup information")

if __name__ == "__main__":
    asyncio.run(reset_database()) 