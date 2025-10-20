# eCourt Cause List Scraper

This project is a Flask-based web application that scrapes cause lists from the Indian eCourts services website. It provides a user-friendly dashboard to select a specific court and date, and then generates and downloads a PDF of the corresponding cause list.

## Features

- **Interactive Dashboard**: A clean, responsive web interface built with Bootstrap.
- **Dynamic Dropdowns**: Sequentially dependent dropdowns for State, District, Court Complex, Court Establishment, and Court Name.
- **Automated Scraping**: Fetches data dynamically from the eCourts portal.
- **CAPTCHA Handling**: Includes a mechanism to handle and solve the CAPTCHA required by the eCourts website.
- **Session Management**: Manages and updates session cookies and tokens required for scraping.
- **PDF Generation**: Converts the scraped cause list HTML into a well-formatted PDF.
- **Automatic Download**: The generated PDF is automatically downloaded by the user's browser.

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, JavaScript, Bootstrap 5
- **Web Scraping**: `requests`, `BeautifulSoup4`
- **OCR for CAPTCHA**: `pytesseract`
- **PDF Generation**: `WeasyPrint`

## Setup and Installation

Follow these steps to set up and run the project locally.

### 1. Prerequisites

- **Python 3.x**: Make sure you have Python installed.
- **Tesseract OCR**: This is required for solving the CAPTCHA.
  - **Windows**: Download and install from the official [Tesseract repository](https://github.com/tesseract-ocr/tesseract). Make sure to add the installation directory to your system's `PATH`.
  - **macOS**: `brew install tesseract`
  - **Linux (Debian/Ubuntu)**: `sudo apt-get install tesseract-ocr`

### 2. Clone the Repository

```bash
git clone https://github.com/adhiraj-ranjan/eCourt_Scarper_Intern_Task.git
cd eCourt_Scarper_Intern_Task
```

### 3. Create a Virtual Environment

It's recommended to use a virtual environment to manage dependencies.

```bash
# Create the virtual environment
python -m venv venv

# Activate it
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

### 4. Install Dependencies

Install tesseract-ocr to path
```bash
apt install tesseract-ocr
```

Install all the required Python packages from `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 5. Configure Session Keys

The scraper requires initial session tokens to work. There is a file already present `keys.json` in the root directory of the project.


You can obtain these initial values by inspecting the network requests on the [eCourts website](https://services.ecourts.gov.in/) in your browser's developer tools. The application will automatically update these tokens as it runs.

### 6. Run the Application

Start the Flask development server.

```bash
python app.py
```

The application will be running at `http://127.0.0.1:5000`.

## Usage

1.  Open your web browser and navigate to `http://127.0.0.1:5000`.
2.  Use the dropdown menus to make your selections in the following order:
    - Select State
    - Select District
    - Select Court Complex
    - Select Court Establishment
    - Select Court Name
3.  Choose a date from the date picker.
4.  Click the **"Generate PDF"** button.
5.  The application will scrape the data, generate a PDF, and your browser will automatically download the file.

## File Structure

```
.
├── app.py                  # Main Flask application file with API routes.
├── scraper.py              # Functions for scraping dropdown data.
├── final_scraper.py        # Core logic for scraping the cause list and generating the PDF.
├── requirements.txt        # Python dependencies.
├── keys.json               # Configuration for session tokens (must be created manually).
├── templates/
│   └── index.html          # Frontend HTML dashboard.
├── static/                 # For CSS, JS, and other static assets (if any).
└── README.md               # This file.
```

## API Endpoints

The Flask application exposes the following API endpoints:

-   `GET /`: Renders the main dashboard (`index.html`).
-   `POST /api/districts`: Fetches the list of districts for a given state.
-   `POST /api/complexes`: Fetches court complexes for a given state and district.
-   `POST /api/establishments`: Fetches court establishments for a given complex.
-   `POST /api/court_names`: Fetches court names for a given establishment.
-   `POST /api/download_cause_list`: Triggers the final scraping process to generate and serve the cause list PDF.
-   `GET /case_data.pdf`: Serves the generated PDF file for download.
