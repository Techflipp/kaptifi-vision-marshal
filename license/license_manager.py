import os
import json
import shutil
import time
from datetime import datetime
from threading import Thread, Event
from dotenv import load_dotenv

# Import logging
from helper.logger import setup_logger

# Import existing validator
from license.license_validator import LicenseValidator

class LicenseService:
    def __init__(self, 
                 license_file=None, 
                 deployment_path=None):
        # Use environment variables if not provided
        self.license_file = license_file or os.getenv('LICENSE_FILE', './license.lic')
        self.deployment_path = deployment_path or os.getenv('DEPLOYMENT_PATH', '/home/kaptifi-vision')
        
        # Setup logger
        self.logger = setup_logger(name='license_service')
        
        # Initialize validator and other attributes
        self.validator = LicenseValidator()
        self.stop_event = Event()

    def load_license_data(self):
        """Load license data from the license file."""
        try:
            with open(self.license_file, 'r') as f:
                license_package = json.load(f)
            return license_package['license']
        except Exception as e:
            self.logger.error(f"Error loading license: {e}")
            return None

    def check_license_status(self):
        """Periodically check license status."""
        valid, message = self.validator.validate_license()
        self.logger.info(f"License Status: {message}")
        
        if not valid:
            self.handle_expired_license()
        
        return valid

    def handle_expired_license(self):
        """Handle actions when license is expired."""
        license_data = self.load_license_data()
        if not license_data:
            return

        expiration_date = datetime.strptime(license_data['expiration'], '%d-%m-%Y')
        days_since_expiry = (datetime.utcnow() - expiration_date).days

        if days_since_expiry >= 7:
            self.cleanup_deployment()

    def cleanup_deployment(self):
        """Cleanup deployment folder after 7 days of license expiry."""
        try:
            # Backup database (customize based on your database type)
            backup_path = os.path.join(self.deployment_path, 'backup')
            os.makedirs(backup_path, exist_ok=True)
            
            # Example: Backup SQLite database
            db_path = os.path.join(self.deployment_path, 'data.db')
            if os.path.exists(db_path):
                backup_db_path = os.path.join(backup_path, f'data_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
                shutil.copy2(db_path, backup_db_path)
            
            # Remove everything except marshal service
            for item in os.listdir(self.deployment_path):
                item_path = os.path.join(self.deployment_path, item)
                if item != 'marshal':  # Keep marshal service
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.unlink(item_path)
            
            self.logger.info("Deployment cleanup completed.")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")

    def run_license_check(self):
        """Run license checks periodically."""
        while not self.stop_event.is_set():
            try:
                self.check_license_status()
                time.sleep(3600)  # Check every hour
            except Exception as e:
                self.logger.error(f"Error in license check: {e}")
                time.sleep(3600)

    def start(self):
        """Start the license service."""
        # Start license checking in a separate thread
        license_thread = Thread(target=self.run_license_check)
        license_thread.start()
        
        return license_thread

    def stop(self):
        """Stop the license service."""
        self.stop_event.set()
        self.logger.info("License service stopped.") 