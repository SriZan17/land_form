"""
Land Form Submission using Selenium
This script submits the land release form using Selenium WebDriver.
Pulls configuration from config.py
Supports Chrome, Firefox, and Edge browsers.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import config
import sys
import logging
import time

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


def setup_chrome_driver():
    """Setup and return Chrome WebDriver."""
    try:
        options = ChromeOptions()
        # Uncomment the line below to run headless (no browser window)
        # options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=options)
        logger.info("Chrome WebDriver initialized")
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize Chrome WebDriver: {e}")
        return None


def setup_firefox_driver():
    """Setup and return Firefox WebDriver."""
    try:
        options = FirefoxOptions()
        # Uncomment the line below to run headless (no browser window)
        # options.add_argument("--headless")
        
        driver = webdriver.Firefox(options=options)
        logger.info("Firefox WebDriver initialized")
        return driver
    except Exception as e:
        logger.error(f"Failed to initialize Firefox WebDriver: {e}")
        return None


def get_driver(browser='chrome'):
    """Get WebDriver for specified browser."""
    if browser.lower() == 'chrome':
        return setup_chrome_driver()
    elif browser.lower() == 'firefox':
        return setup_firefox_driver()
    else:
        logger.error(f"Unsupported browser: {browser}")
        return None


def wait_for_element(driver, locator, timeout=10):
    """Wait for element to be present and visible."""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
        return element
    except Exception as e:
        logger.warning(f"Timeout waiting for element {locator}: {e}")
        return None


def fill_form_field(driver, selector, value, field_name, is_select=False):
    """Fill a form field."""
    try:
        logger.info(f"Filling field: {field_name}")
        element = wait_for_element(driver, selector)
        
        if element is None:
            logger.warning(f"Could not find element for {field_name}")
            return False
        
        if is_select:
            select = Select(element)
            select.select_by_value(value)
            logger.info(f"Selected option for {field_name}")
        else:
            element.clear()
            element.send_keys(value)
            logger.info(f"Filled {field_name}")
        
        return True
    except Exception as e:
        logger.error(f"Error filling {field_name}: {e}")
        return False


def submit_form(driver):
    """Submit the form by clicking checkbox and submit button."""
    try:
        logger.info("Preparing to submit form...")
        
        # First, check and click the Terms and Conditions checkbox
        try:
            checkbox = wait_for_element(driver, (By.CLASS_NAME, "inputfield-Terms_and_Conditions__c"), timeout=5)
            if checkbox and not checkbox.is_selected():
                checkbox.click()
                logger.info("✓ Terms and Conditions checkbox clicked")
            elif checkbox and checkbox.is_selected():
                logger.info("✓ Terms and Conditions checkbox already selected")
            else:
                logger.warning("Could not find Terms and Conditions checkbox")
        except Exception as e:
            logger.error(f"Error handling Terms and Conditions checkbox: {e}")
            return False
        
        # Wait a moment for the checkbox action to complete
        time.sleep(1)
        
        # Look for submit button - try multiple selectors
        submit_selectors = [
            (By.CLASS_NAME, "subbtn"),  # Primary submit button class
            (By.XPATH, "//button[contains(text(), 'Submit') or contains(text(), 'submit')]"),
            (By.XPATH, "//input[@type='submit']"),
            (By.XPATH, "//button[@type='submit']"),
            (By.NAME, "submit"),
            (By.ID, "submit")
        ]
        
        submit_button = None
        for selector in submit_selectors:
            try:
                submit_button = driver.find_element(*selector)
                if submit_button.is_displayed() and submit_button.is_enabled():
                    logger.info(f"Found submit button with selector: {selector}")
                    break
            except:
                continue
        
        if submit_button is None:
            logger.error("Could not find submit button")
            return False
        
        logger.info("Clicking submit button...")
        submit_button.click()
        
        # Wait for form to process
        time.sleep(7)
        
        # Check for success/confirmation message
        try:
            WebDriverWait(driver, 15).until(
                lambda d: 'success' in d.page_source.lower() or 
                         'confirmation' in d.page_source.lower() or
                         'thank you' in d.page_source.lower() or
                         'submitted successfully' in d.page_source.lower()
            )
            logger.info("✓ Form submission appears successful!")
            return True
        except:
            # Check if we're on a success page or redirected
            current_url = driver.current_url
            if 'success' in current_url.lower() or 'confirmation' in current_url.lower():
                logger.info("✓ Form submission appears successful (redirected to success page)!")
                return True
            else:
                logger.info("Form submitted, but confirmation message not detected")
                logger.info(f"Current URL: {current_url}")
                return True
            
    except Exception as e:
        logger.error(f"Error submitting form: {e}")
        return False


def fill_form(driver):
    """Fill form with data from config."""
    try:
        logger.info("Starting form population...")
        
        # Wait for page to load
        wait_for_element(driver, (By.TAG_NAME, "form"))
        time.sleep(2)
        
        # Fill form fields - adjust selectors based on actual form structure
        # Note: First Name and Last Name are prefilled by the server (personalized link)
        # so we don't fill them here
        fields_to_fill = [
            (
                (By.CLASS_NAME, "inputfield-Mobile_Phone__c"),
                config.PREFERRED_CONTACT_NUMBER,
                "Phone Number",
                False
            ),
            (
                (By.CLASS_NAME, "inputfield-Buyer_Type__c"),
                config.BUYER_TYPE,
                "Buyer Type",
                True  # is_select
            ),
            (
                (By.CLASS_NAME, "inputfield-X1st_Lot_Preference__c"),
                config.FIRST_LOT_PREFERENCE,
                "First Lot Preference",
                False
            ),
        ]
        
        # Add optional fields if provided
        if config.SECOND_LOT_PREFERENCE:
            fields_to_fill.append((
                (By.CLASS_NAME, "inputfield-X2nd_Lot_Preference__c"),
                config.SECOND_LOT_PREFERENCE,
                "Second Lot Preference",
                False
            ))
        
        if config.THIRD_LOT_PREFERENCE:
            fields_to_fill.append((
                (By.CLASS_NAME, "inputfield-X3rd_Lot_Preference__c"),
                config.THIRD_LOT_PREFERENCE,
                "Third Lot Preference",
                False
            ))
        
        # Add contract condition if provided
        if config.CONTRACT_CONDITION:
            fields_to_fill.append((
                (By.CLASS_NAME, "inputfield-dc__Multi_Picklist__c"),
                config.CONTRACT_CONDITION,
                "Contract Condition",
                True
            ))
        
        # Fill each field
        successful_fills = 0
        for selector, value, field_name, is_select in fields_to_fill:
            if fill_form_field(driver, selector, value, field_name, is_select):
                successful_fills += 1
        
        logger.info(f"Successfully filled {successful_fills} out of {len(fields_to_fill)} fields")
        return successful_fills == len(fields_to_fill)
        
    except Exception as e:
        logger.error(f"Error filling form: {e}")
        return False


def main(browser='firefox'):
    """Main execution function."""
    logger.info("Starting land form submission (Selenium method)...")
    logger.info(f"Using browser: {browser}")
    
    # Validate config
    if not validate_config():
        logger.error("Configuration validation failed. Please fill in all required fields in config.py")
        sys.exit(1)
    
    # Initialize WebDriver
    driver = get_driver(browser)
    if driver is None:
        logger.error("Failed to initialize WebDriver")
        sys.exit(1)
    
    try:
        # Navigate to form
        logger.info(f"Navigating to: {config.URL}")
        driver.get(config.URL)
        
        # Wait for page to load
        time.sleep(2)
        
        # Fill form
        if not fill_form(driver):
            logger.warning("Some form fields could not be filled")
        
        # Submit form
        if not submit_form(driver):
            logger.error("Form submission failed")
            return False
        
        logger.info("✓ Form submission completed!")
        
        # Keep browser open for verification (optional)
        logger.info("Browser will stay open for 10 seconds for verification...")
        time.sleep(10)
        
        return True
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False
    finally:
        driver.quit()
        logger.info("WebDriver closed")


if __name__ == "__main__":
    # Use 'chrome' or 'firefox'
    browser_choice = 'firefox'
    success = main(browser_choice)
    sys.exit(0 if success else 1)
