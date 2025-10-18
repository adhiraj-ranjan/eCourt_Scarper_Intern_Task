from PIL import Image
import pytesseract
import requests
from bs4 import BeautifulSoup

# to solve captchas
def extract_text_from_image(image_path):
    #Extracts text from an image using Tesseract OCR.
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    
    return text

# print(extract_text_from_image('securimage_show.png'))


cookies = {
    'SERVICES_SESSID': 'b63oecfgc99uqom3k6q373bl4i',
    'JSESSION': '93198583',
}

headers = {
    'Host': 'services.ecourts.gov.in',
    # 'Content-Length': '102',
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
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Priority': 'u=0, i',
    # 'Cookie': 'SERVICES_SESSID=b63oecfgc99uqom3k6q373bl4i; JSESSION=93198583',
}



def reformat_response_districts(response_json):
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

    return districts


def get_districts(state_code):
    data = {
        'state_code': state_code,
        'ajax_req': 'true',
        'app_token': 'ac8aef13f9dd9ca8261a3536a91ec256acbbe4e266257da9acd22dee2e46d8a8',
    }

    response = requests.post(
        'https://services.ecourts.gov.in/ecourtindia_v6/?p=casestatus/fillDistrict',
        cookies=cookies,
        headers=headers,
        data=data,
        verify=False,
    )

    return reformat_response_districts(response.json())

# print(get_districts('8'))