from ninja import Schema

class TripAdvisorQuery(Schema):
    query: str

class Yelp(Schema):
    query: str

    
class ValidCheck(Schema):
    valid: str

class GoogleMapsQuery(Schema):
    query: str

