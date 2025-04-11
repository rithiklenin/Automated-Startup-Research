import asyncio
from typing import List, Dict, Any
import logging
import traceback
from ..models.startup import Startup
from .scraper_service import ScraperService
from .database import DatabaseService

logger = logging.getLogger(__name__)

class ResearchService:
    
    def __init__(self, db_service: DatabaseService):
        self.scraper = ScraperService()
        self.db_service = db_service
    
    async def research_startup(self, company_name: str) -> Startup:
        logger.info(f"Starting research for: {company_name}")
        
        try:
            
            await self.scraper.init_session()
            
            logger.info(f"Searching for {company_name} website...")
            try:
                website_url = await self.scraper.search_company_website(company_name)
                logger.info(f"Found website URL: {website_url}")
            except Exception as e:
                logger.error(f"Error searching company website: {str(e)}")
                logger.error(traceback.format_exc())
                website_url = None
            
            website_data = {}
            if website_url:
                logger.info(f"Scraping website data from {website_url}...")
                try:
                    website_data = await self.scraper.scrape_company_website(website_url)
                    logger.info(f"Website data: {website_data}")
                except Exception as e:
                    logger.error(f"Error scraping website: {str(e)}")
                    logger.error(traceback.format_exc())
            
            logger.info(f"Searching for {company_name} info...")
            try:
                company_data = await self.scraper.search_crunchbase(company_name)
                logger.info(f"Company data: {company_data}")
            except Exception as e:
                logger.error(f"Error getting company info: {str(e)}")
                logger.error(traceback.format_exc())
                company_data = {}
            
            logger.info(f"Searching news for {company_name}...")
            try:
                news_data = await self.scraper.search_news(company_name)
                logger.info(f"News data count: {len(news_data)}")
            except Exception as e:
                logger.error(f"Error searching news: {str(e)}")
                logger.error(traceback.format_exc())
                news_data = []
            
            await self.scraper.close_session()
            
            combined_data = {
                "website": website_url or website_data.get("website") or f"https://{company_name.lower().replace(' ', '')}.com",
                "description": website_data.get("description") or f"{company_name} is a company in the technology sector.",
                "founded_year": company_data.get("founded_year") or "N/A",
                "headquarters": company_data.get("headquarters") or "N/A",
                "industry": company_data.get("industry") or ["Technology"],
                "funding": company_data.get("funding") or {"Estimated": "Unknown"},
                "founders": company_data.get("founders") or [],
                "employees_count": company_data.get("employees_count"),
                "products": website_data.get("products") or [],
                "social_media": website_data.get("social_media") or {},
                "news": news_data
            }
            
            logger.info(f"Combined data for {company_name}: {combined_data}")
            
            startup = Startup(
                id=company_name.lower().replace(" ", "-"),
                name=company_name,
                website=combined_data.get("website"),
                description=combined_data.get("description"),
                founded_year=combined_data.get("founded_year"),
                headquarters=combined_data.get("headquarters"),
                industry=combined_data.get("industry"),
                funding=combined_data.get("funding"),
                founders=combined_data.get("founders"),
                employees_count=combined_data.get("employees_count"),
                products=combined_data.get("products"),
                social_media=combined_data.get("social_media"),
                news=combined_data.get("news")
            )
            self.db_service.save_startup(startup)
            
            logger.info(f"Completed research for: {company_name}")
            return startup
        
        except Exception as e:
            logger.error(f"Error researching {company_name}: {str(e)}")
            logger.error(traceback.format_exc())
            
            return Startup(name=company_name)
    
    async def research_startups(self, company_names: List[str]) -> List[Startup]:
        logger.info(f"Starting batch research for {len(company_names)} startups")
        tasks = [self.research_startup(name) for name in company_names]
        results = await asyncio.gather(*tasks)
        logger.info("Completed batch research")
        return results 