import requests
from bs4 import BeautifulSoup
import re

# to solve captchas
# def extract_text_from_image(image_path):
#     #Extracts text from an image using Tesseract OCR.
#     img = Image.open(image_path)
#     text = pytesseract.image_to_string(img)
    
#     return text

# print(extract_text_from_image('securimage_show.png'))


cookies = {
    'SERVICES_SESSID': 'jlhaoulvhkcg9ors29fmjuf1qo',
    'JSESSION': '57009508',
}

headers = {
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://services.ecourts.gov.in',
    'priority': 'u=0, i',
    'referer': 'https://services.ecourts.gov.in/',
    'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
    # 'cookie': 'SERVICES_SESSID=jlhaoulvhkcg9ors29fmjuf1qo; JSESSION=57009508',
}


def reformat_response_districts(response_json):
    print("[INFO] Reformatting districts response")
    try:
        # Extract the 'dist_list' HTML
        html_options = response_json["dist_list"]

        # Parse it using BeautifulSoup
        soup = BeautifulSoup(html_options, "html.parser")

        # Build dictionary
        districts = {}
        for option in soup.find_all("option"):
            value = option.get("value")
            name = option.text.strip()
            if value and name.lower() != "select district":
                districts[value] = name
                print(f"[DEBUG] Found district: {name} (code: {value})")

        return districts
    except Exception as e:
        print(f"[ERROR] Failed to reformat districts response: {str(e)}")
        raise

def reformat_response_complexes(response_json):
    print("[INFO] Reformatting court complexes response")
    try:
        html_options = response_json["complex_list"]
        soup = BeautifulSoup(html_options, "html.parser")

        complexes = {}
        for option in soup.find_all("option"):
            raw_value = option.get("value")
            name = option.text.strip()
            if raw_value and name.lower() != "select court complex":
                # Take only part before "@"
                value = raw_value.split("@")[0]
                complexes[value] = name
                print(f"[DEBUG] Found complex: {name} (code: {value})")

        return complexes
    except Exception as e:
        print(f"[ERROR] Failed to reformat complexes response: {str(e)}")
        raise

def reformat_response_establishments(response_json):
    html_options = response_json["establishment_list"]
    soup = BeautifulSoup(html_options, "html.parser")

    establishments = {}
    for option in soup.find_all("option"):
        value = option.get("value")
        name = option.text.strip()
        if value and name.lower() != "select court establishment":
            establishments[value] = name

    return establishments



def reformat_court_names(data):
    cause_list_html = data.get("cause_list", "")
    
    # Regex to extract value and display text (ignores disabled ones)
    matches = re.findall(r"<option value=([^ >]+)>([^<]+)</option>", cause_list_html)
    
    formatted_dict = {}
    for value, name in matches:
        # Skip empty or disabled options
        if value.strip() in ("''", "'D'", "D", ""):
            continue
        # Remove extra quotes and spaces
        value = value.strip("'").strip()
        name = name.strip()
        formatted_dict[value] = name
    
    return formatted_dict

def get_districts(state_code):
    print(f"[INFO] Fetching districts for state code: {state_code}")
    data = {
        'state_code': state_code,
        'ajax_req': 'true',
        'app_token': 'ac8aef13f9dd9ca8261a3536a91ec256acbbe4e266257da9acd22dee2e46d8a8',
    }

    try:
        response = requests.post(
            'https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/fillDistrict',
            cookies=cookies,
            headers=headers,
            data=data,
            verify=True,
        )
        response_json = response.json()
        districts = reformat_response_districts(response_json)
        print(f"[SUCCESS] Found {len(districts)} districts")
        return districts
    except Exception as e:
        print(f"[ERROR] Failed to fetch districts: {str(e)}")
        raise

# print(get_districts('8'))

def get_court_complexes(state_code, district_code):
    print(f"[INFO] Fetching court complexes for state: {state_code}, district: {district_code}")
    data = {
        'state_code': state_code,
        'dist_code': district_code,
        'ajax_req': 'true',
        'app_token': '25217b251cea8f5fd83afaf7bda5a40c66a5ef05bb9d89a057cd2e167bd656ec',
    }

    try:
        response = requests.post(
            'https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/fillcomplex',
            cookies=cookies,
            headers=headers,
            data=data,
            verify=True,
        )
        response_json = response.json()
        complexes = reformat_response_complexes(response_json)
        print(f"[SUCCESS] Found {len(complexes)} court complexes")
        return complexes
    except Exception as e:
        print(f"[ERROR] Failed to fetch court complexes: {str(e)}")
        raise
    
# print(get_court_complexes('8', '1'))

def get_court_establishments(state_code, district_code, complex_code):
    print(f"[INFO] Fetching establishments for state: {state_code}, district: {district_code}, complex: {complex_code}")
    data = {
        'state_code': state_code,
        'dist_code': district_code,
        'court_complex_code': complex_code,
        'ajax_req': 'true',
        'app_token': '6c31c83d1cc0eb3681c3aeaa22e1bab1f9913e567e339121bef0c27d08b9c8cb',
    }

    try:
        response = requests.post(
            'https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/fillCourtEstablishment',
            cookies=cookies,
            headers=headers,
            data=data,
            verify=True,
        )
        response_json = response.json()
        establishments = reformat_response_establishments(response_json)
        print(f"[SUCCESS] Found {len(establishments)} court establishments")
        return establishments
    except Exception as e:
        print(f"[ERROR] Failed to fetch court establishments: {str(e)}")
        raise

# print(get_court_establishments('8', '1', '1080009'))

def get_court_names(state_code, district_code, complex_code, establishment_code):
    print(f"[INFO] Fetching court names for state: {state_code}, district: {district_code}, complex: {complex_code}, establishment: {establishment_code}")
    data = {
        'state_code': state_code,
        'dist_code': district_code,
        'court_complex_code': complex_code,
        'est_code': establishment_code,
        'search_act': 'undefined',
        'ajax_req': 'true',
        'app_token': '737aecf3a748f3d0d20afde153022324709d18c6dc733a1eb868fe4ad393ea57',
    }

    try:
        response = requests.post(
            'https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/fillCauseList',
            cookies=cookies,
            headers=headers,
            data=data,
            verify=True,
        )
        response_json = response.json()
        court_names = reformat_court_names(response_json)
        print(f"[SUCCESS] Found {len(court_names)} court names")
        return court_names
    except Exception as e:
        print(f"[ERROR] Failed to fetch court names: {str(e)}")
        raise

# print(get_court_names('8', '1', '1080009', '7i'))


# def fetch_cause_list():
#     s = requests.Session()
#     main_page_html = s.get(
#         'https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/',
#         cookies=cookies,
#         headers=headers,
#         verify=False,
    # )
    # print(main_page_html.text)
    # print(s.cookies)
    # s.headers.update(headers)
    # data = {
    #     'state_code': '8',
    #     'dist_code': '1',
    #     'court_complex_code': '1080009',
    #     'est_code': '7',
    #     'search_act': 'undefined',
    #     'ajax_req': 'true',
    #     'app_token': 'c7edf2469319843b32bb39d6c9456eb7eba232907c7b19e880e009b9955dc4b6',
    # }

    # app_token = requests.post(
    #     'https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/fillCauseList',
    #     cookies=cookies,
    #     headers=headers,
    #     data=data,
    # )
    # print(app_token.json())
    # while True:
    #     token = input("Enter app token: ")
    #     code = input("Enter captcha code: ")
    #     data = f'CL_court_no=5%5E1&causelist_date=18-10-2025&cause_list_captcha_code={code}&court_name_txt=1-Sri Bhupendra Singh-District and Additional Session Judge-I&state_code=8&dist_code=1&court_complex_code=1080009&est_code=7&cicri=civ&selprevdays=0&ajax_req=true&app_token={token}'

    #     response = s.post(
    #         'https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/submitCauseList',
    #         data=data,
    #     )

    #     print(response.json())
# fetch_cause_list()