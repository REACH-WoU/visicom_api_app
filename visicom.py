import requests

class VisicomAPI:
    def __init__(self, api_key, lang='uk', format='json'):
        """
        Initialize the VisicomAPI class with API key, language, and format.
        
        :param api_key: Your API key for Visicom.
        :param lang: Language for the API response. Default is 'uk'.
        :param format: Format of the API response. Default is 'json'.
        """
        self.geocode_url = f'https://api.visicom.ua/data-api/5.0/{lang}/geocode.{format}'
        self.api_key = api_key

    def get_geocode(self, categories=None, ci=None, text=None, word_text=None, 
                    near=None, intersect=None, contains=None, radius=None, 
                    limit=None, country="UA", boost_country=None, zoom=None):
        """
        Build and send a geocode request to the Visicom API.

        :param categories: Categories filter for the geocode request.
        :param ci: Custom identifier.
        :param text: Text for geocoding.
        :param word_text: Word text for geocoding.
        :param near: Near location for geocoding.
        :param intersect: Intersect location for geocoding.
        :param contains: Contains location for geocoding.
        :param radius: Radius for geocoding (in meters).
        :param limit: Limit for the number of results.
        :param country: Country filter for geocoding.
        :param boost_country: Boost country for geocoding.
        :param zoom: Zoom level for the geocode response.
        :return: JSON response from the API.
        """
        params = {
            'categories': categories,
            'ci': ci,
            'text': text,
            'word_text': word_text,
            'near': near,
            'intersect': intersect,
            'contains': contains,
            'radius': radius,
            'limit': limit,
            'country': country,
            'boost_country': boost_country,
            'zoom': zoom,
            'key': self.api_key
        }
        
        params = {k: v for k, v in params.items() if v is not None}
        
        try:
            response = requests.get(self.geocode_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 401:
                return {"error": "Unauthorized access - invalid API key."}
            else:
                return {"error": f"HTTP error occurred: {http_err}"}
        except requests.exceptions.RequestException as req_err:
            return {"error": f"Request error occurred: {req_err}"}

# Example usage:
# api = VisicomAPI(api_key='your_api_key_here')
# result = api.get_geocode(text='some_location')
# print(result)
