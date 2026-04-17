"""
Land Form Submission using Requests Library
This script submits the land release form using the requests library.
Pulls configuration from config.py
"""

import requests
import sys
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import config
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_config():
    """Validate that required config fields are filled."""
    required_fields = [
        'URL',
        'PREFERRED_CONTACT_NUMBER',
        'BUYER_TYPE',
        'FIRST_LOT_PREFERENCE'
    ]
    
    missing = []
    for field in required_fields:
        value = getattr(config, field, "").strip()
        if not value:
            missing.append(field)
    
    if missing:
        logger.error(f"Missing required config fields: {', '.join(missing)}")
        return False
    return True


def create_session_with_retries():
    """Create a requests session with retry strategy."""
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


def build_form_data():
    """Build form data from config.
    
    Note: First Name and Last Name are prefilled and readonly on the form,
    so they're included but as empty strings (server retrieves from session).
    """
    form_data = {
        'j_id0:j_id377': 'j_id0:j_id377',  # Form ID (may vary)
        'dc__Registered_First_Name__c': '',  # Readonly - server fills from session
        'dc__Registered_Last_Name__c': '',   # Readonly - server fills from session
        'Mobile_Phone__c': config.PREFERRED_CONTACT_NUMBER,
        'Buyer_Type__c': config.BUYER_TYPE,
        'X1st_Lot_Preference__c': config.FIRST_LOT_PREFERENCE,
        'Terms_and_Conditions__c': '1',  # Checkbox - checked (required)
    }
    
    # Add optional fields if provided
    if config.SECOND_LOT_PREFERENCE:
        form_data['X2nd_Lot_Preference__c'] = config.SECOND_LOT_PREFERENCE
    
    if config.THIRD_LOT_PREFERENCE:
        form_data['X3rd_Lot_Preference__c'] = config.THIRD_LOT_PREFERENCE
    
    if config.CONTRACT_CONDITION:
        form_data['dc__Multi_Picklist__c'] = config.CONTRACT_CONDITION
    
    return form_data


def get_form_page(session):
    """Fetch the form page first to capture any hidden fields."""
    try:
        logger.info(f"Fetching form page: {config.URL}")
        response = session.get(
            config.URL,
            timeout=config.TIMEOUT,
            verify=config.VERIFY_SSL
        )
        response.raise_for_status()
        logger.info(f"Form page fetched successfully. Status: {response.status_code}")
        return response
    except requests.RequestException as e:
        logger.error(f"Failed to fetch form page: {e}")
        return None


def submit_form(session, form_data):
    """Submit the form to the server."""
    try:
        logger.info("Submitting form...")
        
        # First, get the form page to ensure we have the right session
        form_page = get_form_page(session)
        if not form_page:
            return False
        
        # Submit the form
        response = session.post(
            config.URL,
            data=form_data,
            timeout=config.TIMEOUT,
            verify=config.VERIFY_SSL,
            allow_redirects=True
        )
        
        response.raise_for_status()
        
        # Check for success indicators in response
        if 'success' in response.text.lower() or 'confirmation' in response.text.lower():
            logger.info("Form submitted successfully!")
            logger.info(f"Response status: {response.status_code}")
            return True
        elif 'error' in response.text.lower():
            logger.warning("Form submission returned error message")
            logger.info(f"Response: {response.text[:500]}")
            return False
        else:
            logger.info(f"Form submitted. Status code: {response.status_code}")
            logger.info(f"Response preview: {response.text[:500]}")
            return True
            
    except requests.RequestException as e:
        logger.error(f"Failed to submit form: {e}")
        return False


def main():
    """Main execution function."""
    logger.info("Starting land form submission (requests method)...")
    
    # Validate config
    if not validate_config():
        logger.error("Configuration validation failed. Please fill in all required fields in config.py")
        sys.exit(1)
    
    # Create session
    session = create_session_with_retries()
    
    # Build form data
    form_data = build_form_data()
    logger.info(f"Form data prepared: {len(form_data)} fields")
    
    # Submit form
    success = submit_form(session, form_data)
    
    # Clean up
    session.close()
    
    if success:
        logger.info("✓ Form submission completed successfully!")
        sys.exit(0)
    else:
        logger.error("✗ Form submission failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
