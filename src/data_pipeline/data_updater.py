"""
Module tu dong cap nhat du lieu theo lich
Copy vao: src/data_pipeline/data_updater.py
"""
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from src.data_pipeline.price_data import PriceDataCrawler
from src.data_pipeline.fundamental_data import FundamentalDataCrawler
from config.settings import WATCHLIST

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataUpdater:
    """Tu dong cap nhat du lieu theo lich"""
    
    def __init__(self, watchlist=None):
        self.watchlist = watchlist or WATCHLIST
        self.price_crawler = PriceDataCrawler()
        self.fundamental_crawler = FundamentalDataCrawler()
        self.scheduler = BackgroundScheduler()
    
    def update_price_data(self):
        """Cap nhat du lieu gia"""
        logger.info("=== Starting price data update ===")
        
        success_count = 0
        fail_count = 0
        
        for symbol in self.watchlist:
            try:
                df = self.price_crawler.update_data(symbol)
                if not df.empty:
                    logger.info(f"[OK] Updated {symbol}: {len(df)} records")
                    success_count += 1
                else:
                    logger.warning(f"[SKIP] No new data for {symbol}")
                    fail_count += 1
            except Exception as e:
                logger.error(f"[ERROR] {symbol}: {str(e)}")
                fail_count += 1
        
        logger.info(f"=== Complete: {success_count} OK, {fail_count} failed ===")
    
    def update_fundamental_data(self):
        """Cap nhat du lieu co ban"""
        logger.info("=== Starting fundamental data update ===")
        
        success_count = 0
        fail_count = 0
        
        for symbol in self.watchlist:
            try:
                data = self.fundamental_crawler.get_complete_fundamentals(symbol)
                if data['ratios']:
                    logger.info(f"[OK] Updated {symbol}")
                    success_count += 1
                else:
                    logger.warning(f"[SKIP] No data for {symbol}")
                    fail_count += 1
            except Exception as e:
                logger.error(f"[ERROR] {symbol}: {str(e)}")
                fail_count += 1
        
        logger.info(f"=== Complete: {success_count} OK, {fail_count} failed ===")
    
    def setup_schedule(self):
        """Thiet lap lich cap nhat tu dong"""
        
        # Cap nhat gia hang ngay sau gio dong cua (15:30)
        self.scheduler.add_job(
            self.update_price_data,
            CronTrigger(hour=15, minute=30, day_of_week='mon-fri'),
            id='daily_price_update',
            name='Update price data daily',
            replace_existing=True
        )
        logger.info("[OK] Scheduled daily price update at 15:30")
        
        # Cap nhat co ban hang tuan (Thu 7 9:00 AM)
        self.scheduler.add_job(
            self.update_fundamental_data,
            CronTrigger(day_of_week='sat', hour=9, minute=0),
            id='weekly_fundamental_update',
            name='Update fundamental data weekly',
            replace_existing=True
        )
        logger.info("[OK] Scheduled weekly fundamental update on Saturday 9:00 AM")
    
    def start(self):
        """Khoi dong scheduler"""
        self.setup_schedule()
        self.scheduler.start()
        logger.info("[START] Data updater started!")
        logger.info(f"Next price update: {self.scheduler.get_job('daily_price_update').next_run_time}")
        logger.info(f"Next fundamental update: {self.scheduler.get_job('weekly_fundamental_update').next_run_time}")
    
    def stop(self):
        """Dung scheduler"""
        self.scheduler.shutdown()
        logger.info("[STOP] Data updater stopped")
    
    def run_now(self, update_type='both'):
        """Chay update ngay lap tuc"""
        if update_type in ['both', 'price']:
            self.update_price_data()
        
        if update_type in ['both', 'fundamental']:
            self.update_fundamental_data()


# Example usage
if __name__ == "__main__":
    updater = DataUpdater(watchlist=['VNM', 'VCB', 'HPG'])
    
    # Run update ngay
    print("Running immediate update...")
    updater.run_now(update_type='price')