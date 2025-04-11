import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from ..models.startup import Startup

class DatabaseService:
    def __init__(self, db_path: str = "startups.db"):
        self.db_path = db_path
        self._create_tables()
    
    def _create_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS startups (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            data TEXT NOT NULL,
            last_updated TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_startup(self, startup: Startup) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if not startup.id:
            startup.id = startup.name.lower().replace(" ", "-")
        
        try:
            cursor.execute(
                "INSERT OR REPLACE INTO startups (id, name, data, last_updated) VALUES (?, ?, ?, ?)",
                (
                    startup.id,
                    startup.name,
                    startup.model_dump_json(),
                    datetime.now().isoformat()
                )
            )
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving startup: {e}")
            return False
        finally:
            conn.close()
    
    def get_startup(self, startup_id: str) -> Optional[Startup]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT data FROM startups WHERE id = ? OR name = ?", (startup_id, startup_id))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return Startup.model_validate_json(result[0])
        return None
    
    def get_all_startups(self) -> List[Startup]:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT data FROM startups")
        results = cursor.fetchall()
        
        conn.close()
        
        return [Startup.model_validate_json(row[0]) for row in results]
    
    def search_startups(self, query: str) -> List[Startup]:
        query = query.lower()
        startups = self.get_all_startups()
        
        results = []
        for startup in startups:
            if any([
                # nsame
                query in startup.name.lower(),
                
                # description
                startup.description and query in startup.description.lower(),
                
                # industry
                startup.industry and any(query in industry.lower() for industry in startup.industry),
                
                # products
                startup.products and any(query in product.lower() for product in startup.products),
                
                # founders
                startup.founders and any(query in founder.lower() for founder in startup.founders),
                
                # headquarters
                startup.headquarters and query in startup.headquarters.lower(),
            ]):
                results.append(startup)
                
        return results
    
    def run_analytics(self, query_type: str) -> Dict[str, Any]:
        startups = self.get_all_startups()
        
        if query_type == "industry_count":
            industry_counts = {}
            for startup in startups:
                if startup.industry:
                    for industry in startup.industry:
                        industry_counts[industry] = industry_counts.get(industry, 0) + 1
            return {"type": "industry_count", "data": industry_counts}
        
        elif query_type == "funding_stats":
            total_funding = 0
            valid_startups = 0
            
            for startup in startups:
                if startup.funding and isinstance(startup.funding, dict):
                    try:
                        funding_sum = sum(
                            float(value) for value in startup.funding.values() 
                            if value and (isinstance(value, (int, float)) or 
                                         (isinstance(value, str) and value.replace('.', '', 1).isdigit()))
                        )
                        total_funding += funding_sum
                        valid_startups += 1
                    except (ValueError, TypeError):
                        pass
            
            avg_funding = total_funding / valid_startups if valid_startups else 0
            return {
                "type": "funding_stats", 
                "data": {"total": total_funding, "average": avg_funding}
            }
        
        return {
            "type": "startup_count",
            "data": {"total": len(startups)}
        }