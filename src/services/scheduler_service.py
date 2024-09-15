import json
import urllib.parse

import googlemaps
from loguru import logger

from src.schemas.requests import GenerateScheduleQueryParams
from src.services.ai_service import AIService


class SchedulerService:

    def __init__(self, ai_service: AIService, gmaps: googlemaps.Client):
        self._ai_service = ai_service
        self._gmaps = gmaps

    def run(self, query_params: GenerateScheduleQueryParams):
        self._ai_service.initialize_system_prompt(
            """
            You are an expert virtual travel planner. Your primary function is to provide an itinerary featuring the most popular and must-visit places. 
            You will be given a list of guidelines to strictly follow. 
            You will respond in JSON format with the key being the date formatted in Month day and the values would be the list of locations with details stored in a key named locations.
            You will only return the JSON response without additional text.

            Location details:
            1. Name - Location name
            2. Description - Short description of the location
            3. from - star time of the location
            4. to - end time  of the location
            5. Country - Location country
            """
        )
        self._ai_service.add_user_prompt(
            f"""
            Here are the list of guidelines:
            - The travel location is in {query_params.travel_location}
            - The travel dates would be {query_params.from_date} to {query_params.to_date}
            - The user is interested in {query_params.tags}
            - The day would start at around 10:00 AM
            - Each day should have at least 4 places to visit.
            - Ensure that the distance between stops does not exceed 1 kilometer.
            
            Make sure all these guidelines are followed.
            """
        )
        response = self._ai_service.ai_model.invoke(input=self._ai_service.prompts)
        self._ai_service.add_assistant_prompt(response.content)
        response_data = json.loads(response.content)
        logger.info(response_data)

        day_locations = []

        for date, plan_details in response_data.items():
            day_location = []
            for location in plan_details.get("locations"):
                day_location.append(
                    f"{location.get("Name")}, {location.get("Country")}"
                )
            day_locations.append(day_location)

        optimized_day_locations = []

        for day_stops in day_locations:
            directions_result = self._gmaps.directions(
                origin=query_params.home_location,
                destination=query_params.home_location,
                waypoints=day_stops,
                optimize_waypoints=True,
                mode="walking",
            )
            waypoint_order = directions_result[0].get("waypoint_order")
            sorted_stops = []

            for stop_idx in waypoint_order:
                sorted_stops.append(day_stops[stop_idx])

            optimized_day_locations.append(sorted_stops)

        self._ai_service.add_user_prompt(
            f"""
            You will be given a list that contains list of locations indexed per day.
            Reschedule the activities on the last travel plan you have sent based on the list provided below.
            Consider the timeslots.

            {optimized_day_locations}
            """
        )

        response = self._ai_service.ai_model.invoke(input=self._ai_service.prompts)
        response_data = json.loads(response.content)
        logger.info(response_data)

        for idx, key in enumerate(response_data):
            url = "https://www.google.com/maps/dir/?"
            params = {
                "api": 1,
                "origin": query_params.home_location,
                "destination": query_params.home_location,
                "waypoints": "|".join(optimized_day_locations[idx]),
                "travelmode": "walking",
            }
            gmap_url = url + urllib.parse.urlencode(params)
            response_data[key]["gmaps_url"] = gmap_url

        return response_data
