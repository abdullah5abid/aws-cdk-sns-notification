import requests
import json
from datetime import datetime
import os
import boto3

sns = boto3.client('sns')
sender_id = os.getenv('SENDER_ID')
message_type = os.getenv('MESSAGE_TYPE')
def send_sns_message(phone_number, message):
    params = {
        'Message': message,
        'PhoneNumber': phone_number,
        'MessageAttributes': {
            'AWS.SNS.SMS.SenderID': {
                'DataType': 'String',
                'StringValue': sender_id
            },
            'AWS.SNS.SMS.SMSType': {
                'DataType': 'String',
                'StringValue': message_type
            }
        }
    }
    response = sns.publish(**params)

def handler(date, school_slug, menu_type):
    """
    Fetches the menu data of a specific type for a given date and school.

    Args:
        date (str): The date for which menu data is to be fetched. 
        school_slug (str): The identifier for the school.
        menu_type (str): The type of menu (e.g., 'breakfast' or 'lunch').

    Returns:
        dict: A dictionary containing menu data for the specified menu type.
    """
    NUTRIENT_KEYS = {
        'calories': 'Calories', 
        'g_fat': 'Total Fat (g)', 
        'g_saturated_fat': 'Saturated Fat (g)', 
        'g_trans_fat': 'Trans Fat (g)', 
        'mg_cholesterol': 'Cholesterol (mg)', 
        'g_carbs': 'Total Carbs (g)', 
        'g_sugar': 'Sugar (g)', 
        'mg_sodium': 'Sodium (mg)', 
        'mg_potassium': 'Potassium (mg)', 
        'g_protein': 'Protein (g)',
        'g_fiber': 'Dietary Fiber (g)', 
        'mg_iron': 'Iron (mg)', 
        'mg_calcium': 'Calcium (mg)', 
        'iu_vitamin_a': 'Vitamin A (mg)', 
        'mg_vitamin_c': 'Vitamin C (mg)', 
        'mg_vitamin_d': 'Vitamin D (mg)'
    }
    SERVING_SIZE_KEYS = {'serving_size_amount': 'Serving Size Amount', 'serving_size_unit': 'Serving Size Unit'}
    MENU_TYPE = ['breakfast', 'lunch']  # You need to define MENU_TYPE somewhere

    if menu_type not in MENU_TYPE:
        return {
            "statusCode": 500,
            "body": json.dumps("Menu type is not available! Please provide a valid menu type")
        }

    try:
        formatted_date = datetime.strptime(date, "%Y/%m/%d").strftime("%Y-%m-%d")
    except ValueError:
        print("Date should be in format 'YYYY/MM/DD', e.g. '2023/05/17'.")
        return

    url = f"https://lindberghschools.api.nutrislice.com/menu/api/weeks/school/{school_slug}/menu-type/{menu_type}/{date}"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return

    json_data = response.json()

    menu_items = []
    for day in json_data['days']:
        if day['date'] == formatted_date:
            for item in day['menu_items']:
                if item['food']:
                    food_item = item['food']
                    nutrition_info = food_item.get('rounded_nutrition_info', {})
                    serving_size_info = food_item.get('serving_size_info', {})
                    image_url = food_item.get('image_url', '')
                    menu_item = {"name": food_item['name']}
                    for api_key, readable_key in NUTRIENT_KEYS.items():
                        value = nutrition_info.get(api_key, 0)
                        menu_item[readable_key] = value if value is not None else 0
                    serving_size_amount = serving_size_info.get('serving_size_amount', " ")
                    serving_size_unit = serving_size_info.get('serving_size_unit', " ")
                    menu_item['Serving Size'] = serving_size_amount + ' ' + serving_size_unit
                    menu_item['image_url'] = image_url
                    menu_items.append(menu_item)

    dummy_data_message = ""
    if not menu_items:
        dummy_data_message = "Due to an absence of data for today on the website, the following is a dummy dataset."
        menu_items = [{'name': 'Double chocolate', 'image_url': '', 
                        'Calories': '10', 'Total Fat (g)': '10', 'Saturated Fat (g)': '20', 
                        'Trans Fat (g)': '10', 'Cholesterol (mg)': '20', 'Total Carbs (g)': '10', 
                        'Sugar (g)': '20', 'Sodium (mg)': '10', 'Potassium (mg)': '20', 
                        'Protein (g)': '10', 'Dietary Fiber (g)': '20', 'Iron (mg)': '10', 
                        'Calcium (mg)': '20', 'Vitamin A (mg)': '10', 'Vitamin C (mg)': '20', 
                        'Vitamin D (mg)': '10', 'serving_size_amount': '10', 'serving_size_unit': 'g'}]

    menu_data = {
        'date': date,
        'message': dummy_data_message,
        'menu': menu_items
    }
    send_sns_message('+923178157449', str(menu_data))

    return menu_data
