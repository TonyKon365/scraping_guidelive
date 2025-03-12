import os
from openai import AsyncOpenAI
import ast
from dotenv import load_dotenv
import json

load_dotenv()

key: str = os.getenv("OPENAI_API_KEY")

client = AsyncOpenAI(
    api_key=key,
)

import os
from openai import AsyncOpenAI
import ast
from dotenv import load_dotenv
import json

load_dotenv()

key: str = os.getenv("OPENAI_API_KEY")

client = AsyncOpenAI(
    api_key=key,
)

EVENT_TEMPLATE = {
    'target_id': 'rotoruanui',
    'target_url': 'https://www.rotoruanui.nz',
    "event_title": "Government Gardens Guided Tours (2024)",
    "start_date": "2024-06-25",
    "start_time": "19:00:00",
    "end_date": "2024-06-25",
    "end_time": "21:00:00",
    "event_category": ["Culture"],
    "event_description": "Description of the event",
    "add_to_cart_url": "https://www.rotoruanui.nz/wp/Rotorua",
    "event_location_title":'Chris Parker',
     'event_street':"Government Gardens 9 Queens Driv",
    "event_region":"Rotorua",
    "event_country":"New Zealand",
    "event_location": {
        "title": "Chris Parker",
        "street": "Government Gardens 9 Queens Drive",
        "region": "Rotorua",
        "country": "New Zealand"
    },
    "event_imgurl": "https://www.rotoruanui.nz/wp-content/uploads/2021/07/Rotorua-Government-Gardens-Tours-370x211.jpg",
}

EVENT_TEMPLATE_news = {
    "target_id": "eventfindaNews",
    "target_url": "https://www.eventfinda.co.nz/news",
    "title": "Government Gardens Guided Tours (2024)",
    "news_url": "https://www.eventfinda.co.nz/news",
    "content": "Description of the news",
    "imageUrl": "https://www.rotoruanui.nz/wp-content/uploads/2021/07/Rotorua-Government-Gardens-Tours-370x211.jpg",
    "date": "2024-06-25",
}



async def customize(object) -> dict:
    try:
        chat_completion = await client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "If you provide an object, it will update its fields according to the provided template's format. "
                        "Only follow the template format; do not copy the template's data. {} "
                        "`start_date` and `end_date` must be updated to the date format `YYYY-MM-DD` (e.g., `2024-01-02`). "
                        "`start_time` and `end_time` must be updated to the time format `HH:MM:SS` (e.g., `19:00:00`). "
                        "You have to find `end_date`, `start_time`, and `end_time` using the `start_date` value. "
                        "For example, if `start_date` is `08 Aug 2024 3:pm-08 Sep 2024 5:pm`: "
                        "- `start_date` should be `2024-08-08` "
                        "- `start_time` should be `15:00:00` "
                        "- `end_date` should be `2024-09-08` "
                        "- `end_time` should be `17:00:00`. "
                        "if start_date and start_time have Timezone info, plz ignore"
                        "if start_date=Thursday, 22 August 2024 7:30 pm it should update to start_date='2024-08-22' start_time='19:30:00' and end_date , end_time have to '' "
                        "You can't know `start_time`, 'end_time' or 'end_date' from start_Date, unknown  filed should remain unset or be an empty string. "
                        "if start_date='Date:  Saturday Mar 29 Doors open at 8:00pm 2024' you have to update start_date='2024-03-29' and start_time is '20:00:00' because you can know start_date and start_time with start_date value"
                        "if start_date=Fri, 28 Nov 2025, 9am - 6pm start_date have to '2025-11-28' start_time='11:00:00' end_time='18:00:00'"
                        "for example like this case Fri 25 - Sat 26 October 2024 7:00 pm you can't know start_time, plz set empty value don't create fake data, try for get date from start_date, but you can't get, plz set empty"
                        "event_location_title represents location data and includes details such as title, region, street, and country. If the input only provides a value for event_location_title, you must use reliable and contextual information to determine the corresponding region, street, and country accurately. Ensure that the region field (event_region) is always filled, as it is mandatory. Use the title to identify the correct street, region, and country based on accurate and verified data sources. If no verified data is available for the street, leave the event_street field empty.For example: If event_location_title is 'Wolfbrook Arena', use reliable information to update:- event_street to '55 Jack Hinton Drive' (ensure this is accurate and verified),- event_region to 'Addington, Christchurch' (mandatory to fill),- event_country to 'New Zealand'.Only populate fields with verified information. Do not guess or fabricate values. If any part of the location cannot be determined, leave it empty."
                        "- event_description` is a description of the event, so it is the same as the description text. If `event_description` contains strange characters such as `/n`, please remove them. - In case of duplicates, fields inside `json_data` take precedence over top-level fields.- Fields not mentioned in the Exclude All template object.- If the response is too long, send keys with omitted values. No further explanation needed, just use updated objects. In particular, there is no need for data assumed in time. If the value of a particular key is null or unknown, fill in an empty string.").format(EVENT_TEMPLATE)
                },
                {
                    "role": "user",
                    "content": "{}".format(object)
                }
            ],
            model="gpt-4o-mini",
            max_tokens=4096,
            response_format={"type": "json_object"}
        )

        # Check if the response contains a message and extract its content
        if chat_completion.choices:
            message_content = chat_completion.choices[0].message.content
            # Try to parse the message content as JSON
            object_dict = json.loads(message_content)
            return object_dict
        else:
            print("No response from the API.")
            return None

    except Exception as e:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("Error:", e)
        return None

def customizable(temp):
    dict1 = {}
    for key, value in temp.items():
        if key in EVENT_TEMPLATE:
            dict1[key] = value
        else: continue
        
    return dict1

async def customizeNews(object) -> None:

    chat_completion = await client.chat.completions.create(
        messages=[
            {
            "role": "system",
           "content": "If you provide an object, it will update its fields according to the provided template.{} - `start_date` and `start_time` must be in template format, and `start_date` must only use a date format such as `2024-06- 24` and `start_time` must be in the following time format as 19:00:00:If you can know the start_date and end_date with the .'start_date' information, you must fill them in. If start_time and end_time can be known with 'start_time' information, you must fill them in. For example, 'start_time' is 'Friday, July 5 to Sunday, July 28, 2024'. 'Start_Date' is 2024-07-05 and 'End_Date' is 2024-07-28.`event_location` is JSON data and includes title, region, street, and country.If the input value is only a title, you must use the information in the title to find out the region, street, and country where the title is located, and update all empty items with those values.- event_description` is a description of the event, so it is the same as the description text. If `event_description` contains strange characters such as `/n`, please remove them. - In case of duplicates, fields inside `json_data` take precedence over top-level fields.- Fields not mentioned in the Exclude All template object.- If the response is too long, send keys with omitted values. No further explanation needed, just use updated objects. In particular, there is no need for data assumed in time. If the value of a particular key is null or unknown, fill in an empty string.".format(EVENT_TEMPLATE) 
            },
            {
                "role": "user",
                "content": "{}".format(object)
            }
            ],
        model="gpt-4o",
        max_tokens=4096,
        response_format={ "type": "json_object" }
    )
    temp = chat_completion.choices[0].message.content
    
    try:
        object_dict = ast.literal_eval(chat_completion.choices[0].message.content[temp.find('{'): temp.rfind('}')+1])
        return object_dict
    except ValueError as e:
        print('----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')
        print("Error converting the string to dictionary:", e)
        return None
# asyncio.run(call())

def customizableNews(temp):
    dict1 = {}
    for key, value in temp.items():
        if key in EVENT_TEMPLATE_news:
            dict1[key] = value
        else: continue
        
    return dict1

