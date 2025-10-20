import requests
import json
import pytesseract
from PIL import Image
import re
from weasyprint import HTML
# from datetime import datetime

def load_config():
    """Load configuration from keys.json file"""
    print("[INFO] Loading configuration from keys.json...")
    try:
        with open('keys.json', 'r') as f:
            config = json.loads(f.read())
        # print("[SUCCESS] Configuration loaded successfully")
        return config
    except Exception as e:
        print(f"[ERROR] Failed to load configuration: {str(e)}")
        raise

def get_request_headers(config):
    """Prepare request headers and cookies"""
    print("[INFO] Preparing request headers...")
    
    cookies = {
        'JSESSION': config['JSESSION'],
        'SERVICES_SESSID': config['SERVICES_SESSID'],
    }

    headers = {
        'Host': 'services.ecourts.gov.in',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Sec-Ch-Ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Sec-Ch-Ua-Mobile': '?0',
        'Origin': 'https://services.ecourts.gov.in',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Dest': 'empty',
        'Referer': 'https://services.ecourts.gov.in/',
        'Accept-Language': 'en-US,en;q=0.9',
        'Priority': 'u=0, i',
    }
    
    return headers, cookies

def download_captcha(config, headers, cookies):
    """Download CAPTCHA image from the server"""
    print("[INFO] Downloading CAPTCHA image...")
    try:
        response = requests.get(
            f'https://services.ecourts.gov.in/ecourtindia_v6/vendor/securimage/securimage_show.php?{config["captcha_url_param"]}',
            cookies=cookies,
            headers=headers,
            verify=True,
        )
        
        with open("securimage_show.png", "wb") as f:
            f.write(response.content)
        # print("[SUCCESS] CAPTCHA image downloaded successfully")
    except Exception as e:
        print(f"[ERROR] Failed to download CAPTCHA: {str(e)}")
        raise

def extract_text_from_image(image_path):
    """Extract text from CAPTCHA image using Tesseract OCR"""
    # print("[INFO] Extracting text from CAPTCHA image...")
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        text = text.strip()
        print(f"[SUCCESS] CAPTCHA text extracted: {text}")
        return text
    except Exception as e:
        print(f"[ERROR] Failed to extract CAPTCHA text: {str(e)}")
        raise

def extract_captcha_id(response):
    """Extract CAPTCHA ID from response"""
    # print("[INFO] Extracting CAPTCHA ID from response...")
    try:
        if isinstance(response, str):
            response = json.loads(response)
        
        html = response.get('div_captcha', '')
        match = re.search(r'securimage_show\.php\?([a-f0-9]+)', html)
        captcha_id = match.group(1) if match else None
        
        if captcha_id:
            print(f"[SUCCESS] CAPTCHA ID extracted: {captcha_id}")
        else:
            print("[WARNING] No CAPTCHA ID found in response")
        return captcha_id
    except Exception as e:
        print(f"[ERROR] Failed to extract CAPTCHA ID: {str(e)}")
        raise

def submit_cause_list(headers, cookies, config, captcha_text, cl_court_no, court_name, 
                    causelist_date, state_code, dist_code, court_complex_code, est_code):
    """Submit cause list request to the server"""
    print("[INFO] Submitting cause list request...")
    
    res = []
    for case_type in ['civ', 'cri']:
        data = {
            'CL_court_no': cl_court_no,
            'causelist_date': causelist_date,
            'cause_list_captcha_code': captcha_text,
            'court_name_txt': court_name,
            'state_code': state_code,
            'dist_code': dist_code,
            'court_complex_code': court_complex_code,
            'est_code': est_code,
            'cicri': case_type,
            'selprevdays': '0',
            'ajax_req': 'true',
            'app_token': config['app_token']
        }

        while True:
            try:
                response = requests.post(
                    'https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/submitCauseList',
                    cookies=cookies,
                    headers=headers,
                    data='&'.join(f'{k}={v}' for k, v in data.items()),
                    verify=True,
                )
                response_json = response.json()
                
                if "errormsg" in response_json:
                    print(f"[WARNING] Server returned error: {response_json['errormsg']}. Retrying...")
                    
                    # Update configuration with new tokens
                    update_config(config, response)
                    
                    # Update cookies and headers with new values
                    headers, cookies = get_request_headers(config)
                    
                    # Download new CAPTCHA and get new text
                    download_captcha(config, headers, cookies)
                    new_captcha_text = extract_text_from_image("securimage_show.png")
                    
                    # Update the data with new captcha and app_token
                    data['cause_list_captcha_code'] = new_captcha_text
                    data['app_token'] = config['app_token']
                    
                    continue  # Retry the request
                    
                res.append(response)
                break  # Exit the while loop on success
            except Exception as e:
                print(f"[ERROR] Failed to submit cause list: {str(e)}")
                raise
    return res


def update_config(config, response):
    """Update configuration with new tokens"""
    print("[INFO] Updating configuration...")
    try:
        cookies_dict = response.cookies.get_dict()
        
        if "JSESSION" in cookies_dict:
            print(f"[INFO] New JSESSION: {cookies_dict['JSESSION']}")
            config["JSESSION"] = cookies_dict['JSESSION']
            
        if "SERVICES_SESSID" in cookies_dict:
            print(f"[INFO] New SERVICES_SESSID: {cookies_dict['SERVICES_SESSID']}")
            config["SERVICES_SESSID"] = cookies_dict['SERVICES_SESSID']
        
        response_json = response.json()
        config["app_token"] = response_json['app_token']
        config["captcha_url_param"] = extract_captcha_id(response_json)
        
        with open('keys.json', 'w') as f:
            json.dump(config, f, indent=4)
        # print("[SUCCESS] Configuration updated successfully")
    except Exception as e:
        print(f"[ERROR] Failed to update configuration: {str(e)}")
        raise

def generate_pdf(civ_case_data, cri_case_data):
    """Generate PDF from case data"""
    print("[INFO] Generating PDF from case data...")
    try:
        html_content = f"""
        <html>
        <head>
        <style>
        body {{ font-family: Arial, sans-serif; }}
        table {{ border-collapse: collapse; width: 100%; font-size: 12px; }}
        th, td {{ border: 1px solid #999; padding: 6px; }}
        th {{ background: #f0f0f0; }}
        </style>
        </head>
        <body>
        {civ_case_data}

        {cri_case_data}
        </body>
        </html>
        """
        
        HTML(string=html_content).write_pdf("static/case_data.pdf")
        print("[SUCCESS] PDF generated successfully as case_data.pdf")
    except Exception as e:
        print(f"[ERROR] Failed to generate PDF: {str(e)}")
        raise

def main(cl_court_no, court_name, causelist_date, state_code, 
         dist_code, court_complex_code, est_code):
    """Main function to orchestrate the scraping process"""
    # print("\n[START] Starting eCourt scraping process...")
    
    try:
        # Load configuration
        config = load_config()
        
        # Get headers and cookies
        headers, cookies = get_request_headers(config)
        
        # Download and process CAPTCHA
        download_captcha(config, headers, cookies)
        captcha_text = extract_text_from_image("securimage_show.png")
        
        # Submit cause list and get response
        res_cases = submit_cause_list(headers, cookies, config, captcha_text, cl_court_no, 
                                     court_name, causelist_date, state_code, dist_code, court_complex_code, est_code)
        # res_cases = response.json()
        # print(f"[INFO] Server Response: {json.dumps(response_json, indent=2)}")
        
        # Update configuration with new tokens
        update_config(config, res_cases[1])
        
        # Generate PDF from case data
        if res_cases:
            generate_pdf(res_cases[0].json()["case_data"], res_cases[1].json()["case_data"])
        else:
            print("[WARNING] No case data found in response")
        
        print("✅ PDF saved as case_data.pdf")

        return True
        # print("\n[END] eCourt scraping process completed successfully")
        
    except Exception as e:
        print(f"\n[FATAL] Scraping process failed: {str(e)}")
        return False
        # raise

if __name__ == "__main__":
    main()

