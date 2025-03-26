from concurrent.futures import ThreadPoolExecutor
import json
from typing import Dict
from ninja_extra import api_controller, http_post, NinjaExtraAPI
from myapp.schema import GoogleMapsQuery

gmb_api = NinjaExtraAPI(urls_namespace='GoogleMaps')

def FetchAndStoreRestaurantData(query):
    print('query: ', query)

@api_controller("", tags=["GoogleMaps"])
class GoogleMapsController:
    
    
    @http_post('/restaurant_details', response={200: Dict, 400: Dict})
    def restaurant_details(self,request, data: GoogleMapsQuery):
        """Return restaurant details for a specific ID"""
        try:
           query = data.query
           print(query)
           executor = ThreadPoolExecutor()
           future = executor.submit(FetchAndStoreRestaurantData,query )
           return 200, {
               "message": "Success",
           }
        except (FileNotFoundError, json.JSONDecodeError):
            return {"error": "Restaurant not found"}
    

# Register controllers
gmb_api.register_controllers(GoogleMapsController)
