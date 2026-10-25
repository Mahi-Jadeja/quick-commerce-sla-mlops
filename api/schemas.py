from pydantic import BaseModel, Field
from typing import Optional, List


class DeliveryInput(BaseModel):
    Delivery_person_Age: float = Field(..., example=28.0, description="Age of delivery rider")
    Delivery_person_Ratings: float = Field(..., example=4.7, description="Rating of delivery rider (1.0 - 5.0)")
    distance_km: float = Field(..., example=5.2, description="Haversine distance in km from restaurant to customer")
    Weatherconditions: str = Field(..., example="Sunny", description="Weather condition (Sunny, Stormy, Sandstorms, Windy, Fog, Cloudy)")
    Road_traffic_density: str = Field(..., example="Medium", description="Traffic level (Low, Medium, High, Jam)")
    Vehicle_condition: int = Field(..., example=2, description="Vehicle condition index (0, 1, 2)")
    Type_of_order: str = Field(..., example="Snack", description="Order category (Snack, Meal, Drinks, Buffet)")
    Type_of_vehicle: str = Field(..., example="motorcycle", description="Vehicle type (motorcycle, scooter, electric_scooter, bicycle)")
    multiple_deliveries: float = Field(..., example=0.0, description="Number of concurrent orders assigned")
    Festival: str = Field(..., example="No", description="Festival period (No, Yes)")
    City: str = Field(..., example="Metropolitian", description="City type (Metropolitian, Urban, Semi-Urban)")


class PredictionOutput(BaseModel):
    will_breach_sla: int = Field(..., description="1 if SLA breach predicted (>30 mins), 0 otherwise")
    sla_breach_probability: float = Field(..., description="Probability of exceeding 30-minute delivery SLA")
    risk_level: str = Field(..., description="SLA Breach Risk Category (LOW, MEDIUM, HIGH)")
    recommendation: str = Field(..., description="Actionable recommendation for delivery dispatch")


class BatchDeliveryInput(BaseModel):
    orders: List[DeliveryInput]


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_source: str
    version: str
