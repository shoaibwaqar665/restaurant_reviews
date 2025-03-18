from ninja import Schema

class TripAdvisorQuery(Schema):
    query: str

    
class ValidCheck(Schema):
    valid: str