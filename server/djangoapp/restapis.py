import requests
import json
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features,SentimentOptions


# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
import requests
import json
from requests.auth import HTTPBasicAuth

def get_request(url, **kwargs):
    print(kwargs)
    api_key = kwargs.get("api_key")
    try:
        if api_key:
            params = dict()
            params["text"] = kwargs["text"]
            params["version"] = kwargs["version"]
            params["features"] = kwargs["features"]
            params["return_analyzed_text"] = kwargs["return_analyzed_text"]
            response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
                                    auth=HTTPBasicAuth('apikey', api_key))
        else:
        # Call get method of requests library with URL and parameters
            response = requests.get(url, headers={'Content-Type': 'application/json'},
                                        params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, payload, **kwargs):
    print("POST to {} ".format(url))
    print({"review": payload})
    response = requests.post(url, params=kwargs, json={"review": payload})
    status_code = response.status_code
    json_data = json.loads(response.text)
    return json_data

# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)

    return results

# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_by_id_from_cf(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url, id=dealerId)
    if json_result:
        # Get the row list in JSON as dealers
        dealers = json_result
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)

    return results


def get_dealers_reviews_from_cf(url, dealerId):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url,dealerId = dealerId)
    if json_result:
        # Get the row list in JSON as dealers
        reviews = json_result

        # For each dealer object
        for review in reviews:
            # Get its content in `doc` object
            # Create a CarDealer object with values in `doc` object
            review_obj = DealerReview(dealership=review["dealership"],
                                   name=review["name"],
                                   purchase=review["purchase"],
                                   review=review["review"])
            if "id" in review:
                review_obj.id = review["id"]
            if "purchase_date" in review:
                review_obj.purchase_date = review["purchase_date"]
            if "car_make" in review:
                review_obj.car_make = review["car_make"]
            if "car_model" in review:
                review_obj.car_model = review["car_model"]
            if "car_year" in review:
                review_obj.car_year = review["car_year"]

            sentiment = analyze_review_sentiments(review_obj.review)
            review_obj.sentiment = sentiment

            results.append(review_obj)

    return results


# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(text):
    url = "https://api.eu-gb.natural-language-understanding.watson.cloud.ibm.com/instances/b866b957-ab54-4b6f-bfb9-28a7f8ea1c63"
    api_key = "nQ8S_30wxXxDLbPI1QxAFpUO8VtDiBM2GAiyYqIubt3L"
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(version='2021-08-01',authenticator=authenticator)
    natural_language_understanding.set_service_url(url)
    response = natural_language_understanding.analyze( text=text+" hello hello hello",features=Features(sentiment=SentimentOptions(targets=[text+" hello hello hello"]))).get_result()
    label=json.dumps(response, indent=2)
    label = response['sentiment']['document']['label']
    
    
    return(label)