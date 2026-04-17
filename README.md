# Land Form Submission Scripts

This project contains two Python scripts for submitting a land release form: one using `requests` and another using `Selenium`.

## Overview

### `submit_form_requests.py`

- **Pros**: Fast, lightweight, minimal dependencies, no browser needed
- **Cons**: May fail if form requires JavaScript execution or complex session handling
- **Best for**: Simple forms, quick testing, server-side form validation

### `submit_form_selenium.py`

- **Pros**: Handles JavaScript, complex interactions, closer to real user behavior
- **Cons**: Slower, requires browser installation, more resources
- **Best for**: JavaScript-heavy forms, client-side validation, complex workflows

## Setup Instructions

### 1. Prerequisites

```bash
# Make sure you have Python 3.7+ installed
python --version
```

### 2. Install Dependencies

**For requests method (minimal):**

```bash
pip install requests urllib3
```

**For Selenium method:**

```bash
pip install selenium
```

**For both methods:**

```bash
pip install requests urllib3 selenium
```

### 3. Install WebDriver (Selenium only)

**Chrome:**

1. Download ChromeDriver from: https://chromedriver.chromium.org/
2. Extract and add to your PATH, or specify the path in the script

**Firefox:**

1. Download GeckoDriver from: https://github.com/mozilla/geckodriver/releases
2. Extract and add to your PATH

### 4. Configure Form Data

Edit `config.py` and fill in all required fields:

```python
# Form URL
URL = "https://your-form-url.com"

# Personal Details
# NOTE: First Name and Last Name are prefilled by the system (personalized link)
# Leave these empty - they will be auto-filled
REGISTERED_FIRST_NAME = ""  # Prefilled automatically
REGISTERED_LAST_NAME = ""   # Prefilled automatically
EMAIL_ADDRESS = "john@example.com"
PREFERRED_CONTACT_NUMBER = "0412345678"  # Must be format: 04XXXXXXXX

# Buyer Information
BUYER_TYPE = "First Home Buyer"

# Lot Preferences (at least one required)
FIRST_LOT_PREFERENCE = "725"
SECOND_LOT_PREFERENCE = ""
THIRD_LOT_PREFERENCE = ""

# Optional fields
REGISTRATION_QUESTION_1 = ""
CONTRACT_CONDITION = ""
```

## Usage

### Using Requests (Recommended to try first)

```bash
python submit_form_requests.py
```

**Expected output:**

```
2026-04-17 12:00:00 - INFO - Starting land form submission (requests method)...
2026-04-17 12:00:00 - INFO - Fetching form page: https://...
2026-04-17 12:00:01 - INFO - Form page fetched successfully. Status: 200
2026-04-17 12:00:01 - INFO - Form data prepared: 7 fields
2026-04-17 12:00:02 - INFO - ✓ Form submission completed successfully!
```

### Using Selenium

```bash
python submit_form_selenium.py
```

**Before running:**

- Open the script and check/modify the `browser_choice` variable at the bottom:
  ```python
  browser_choice = 'chrome'  # or 'firefox'
  ```

**Expected output:**

```
2026-04-17 12:00:00 - INFO - Starting land form submission (Selenium method)...
2026-04-17 12:00:00 - INFO - Using browser: chrome
2026-04-17 12:00:01 - INFO - Chrome WebDriver initialized
2026-04-17 12:00:02 - INFO - Navigating to: https://...
2026-04-17 12:00:04 - INFO - Starting form population...
2026-04-17 12:00:05 - INFO - Filling field: First Name
...
2026-04-17 12:00:08 - INFO - ✓ Form submission completed!
```

## Troubleshooting

### Requests Method Issues

**Problem: Form submission fails with 403/401 error**

- Solution: May need authentication; try Selenium instead

**Problem: "Missing required config fields"**

- Solution: Fill in all required fields in `config.py`

**Problem: Phone number validation error**

- Solution: Ensure phone number is in format `04XXXXXXXX` with no spaces

### Selenium Method Issues

**Problem: "ChromeDriver not found"**

- Solution: Download ChromeDriver and add to PATH or specify full path in script

**Problem: "Element not found" errors**

- Solution: The form selectors may need adjustment. Inspect the HTML and update the `fill_form()` function with correct class names

**Problem: Timeout waiting for element**

- Solution: Increase the timeout values in `wait_for_element()` calls

**Problem: Browser doesn't fill fields**

- Solution: Ensure fields are visible and not obscured by JavaScript; add waits between actions

## Field Mapping Reference

The scripts use these form field identifiers. Adjust if form structure is different:

| Field      | Requests Key             | Selenium Class                      | Config Variable            | Notes                         |
| ---------- | ------------------------ | ----------------------------------- | -------------------------- | ----------------------------- |
| First Name | N/A                      | N/A                                 | `REGISTERED_FIRST_NAME`    | **Prefilled** - not submitted |
| Last Name  | N/A                      | N/A                                 | `REGISTERED_LAST_NAME`     | **Prefilled** - not submitted |
| Email      | `Email_Address__c`       | `inputfield-Email_Address__c`       | `EMAIL_ADDRESS`            | Required                      |
| Phone      | `Mobile_Phone__c`        | `inputfield-Mobile_Phone__c`        | `PREFERRED_CONTACT_NUMBER` |
| Buyer Type | `Buyer_Type__c`          | `inputfield-Buyer_Type__c`          | `BUYER_TYPE`               |
| Lot 1      | `X1st_Lot_Preference__c` | `inputfield-X1st_Lot_Preference__c` | `FIRST_LOT_PREFERENCE`     |
| Lot 2      | `X2nd_Lot_Preference__c` | `inputfield-X2nd_Lot_Preference__c` | `SECOND_LOT_PREFERENCE`    |
| Lot 3      | `X3rd_Lot_Preference__c` | `inputfield-X3rd_Lot_Preference__c` | `THIRD_LOT_PREFERENCE`     |

## Which Method to Use?

### Try Requests First If:

- ✓ Form is relatively simple
- ✓ You want fastest execution
- ✓ You want minimal dependencies
- ✓ Form doesn't have heavy JavaScript

### Use Selenium If:

- ✓ Requests fails or returns errors
- ✓ Form requires JavaScript execution
- ✓ You need to handle popup dialogs
- ✓ Form has dynamic fields
- ✓ You want to verify visual output

## Security Notes

- **Never hardcode sensitive information** in config.py
- **Use environment variables** for production:
  ```python
  import os
  REGISTERED_FIRST_NAME = os.getenv('FORM_FIRST_NAME')
  ```
- **Keep config.py out of version control** - add to `.gitignore`
- **Be careful with phone numbers** - they can be personally identifiable

## Logging

Both scripts use Python's built-in `logging` module. View logs for debugging:

```python
# All messages shown by default
# To save logs to file, add to script:
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('form_submission.log'),
        logging.StreamHandler()
    ]
)
```

## Support

If forms fail:

1. Check the HTML of the actual form (`release.html`)
2. Update field selectors/names in the script
3. Add `time.sleep()` calls if page loads slowly
4. Try the alternative method (requests vs Selenium)
