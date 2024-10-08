import json
import urllib.parse
from datetime import datetime
from uuid import uuid4

import googlemaps
from loguru import logger

from api.schemas.requests import GenerateScheduleQueryParams
from api.schemas.response import ResponseSchema
from api.services.ai_service import AIService


class SchedulerService:

    def __init__(self, ai_service: AIService, gmaps: googlemaps.Client):
        self._ai_service = ai_service
        self._gmaps = gmaps
        self.sys_prompt = """
        You are an expert virtual travel planner. Your primary function is to provide an itinerary featuring the most popular and must-visit places. 
        You will be given a list of guidelines to strictly follow. 
        You will respond in JSON format with the key being the date formatted in Month day, year and the values would be the list of locations with details stored in a key named locations.
        You will only return the JSON response without additional text.

        Location details:
        1. Name - Location name
        2. Description - Short description of the location
        3. from - star time of the location
        4. to - end time  of the location
        5. Country - Location country
        """

    @staticmethod
    def extract_location_country(response_data):
        day_locations = []

        for date, plan_details in response_data.items():
            day_location = []
            for location in plan_details.get("locations"):
                day_location.append(
                    f"{location.get("Name")}, {location.get("Country")}"
                )
            day_locations.append(day_location)

        return day_locations

    def optimize_locations_gmap(self, query_params, day_locations):
        optimized_day_locations = []

        for day_stops in day_locations:
            directions_result = self._gmaps.directions(
                origin=query_params.home_location,
                destination=query_params.home_location,
                waypoints=day_stops,
                optimize_waypoints=True,
                mode="walking",
            )
            if not directions_result:
                return day_stops, False
            waypoint_order = directions_result[0].get("waypoint_order")
            sorted_stops = []

            for stop_idx in waypoint_order:
                sorted_stops.append(day_stops[stop_idx])

            optimized_day_locations.append(sorted_stops)

        return optimized_day_locations, True

    def reschedule_plan(self, optimized_day_locations):
        self._ai_service.add_user_prompt(
            f"""
            You will be given a list that contains list of locations indexed per day.
            Reschedule the activities on the last travel plan you have sent based on the list provided below.
            Consider the timeslots.

            {optimized_day_locations}
            """
        )

        response = self._ai_service.ai_model.invoke(input=self._ai_service.prompts)
        return json.loads(response.content)

    @staticmethod
    def integrate_gmaps_urls(query_params, optimized_day_locations, response_data):
        for idx, item_data in enumerate(response_data.items()):
            key, val = item_data
            url = "://www.google.com/maps/dir/?"
            params = {
                "api": 1,
                "origin": query_params.home_location,
                "destination": query_params.home_location,
                "waypoints": "|".join(optimized_day_locations[idx]),
                "travelmode": "walking",
            }
            for loc in val.get("locations"):
                loc["event_id"] = str(uuid4())
            gmap_url = url + urllib.parse.urlencode(params)
            response_data[key]["gmaps_url"] = gmap_url

    def run(self, query_params: GenerateScheduleQueryParams):
        self._ai_service.initialize_system_prompt(self.sys_prompt)

        from_date = datetime.strftime(query_params.from_date, "%Y-%m-%d")
        to_date = datetime.strftime(query_params.to_date, "%Y-%m-%d")
        tags = ",".join(query_params.tags)

        self._ai_service.add_user_prompt(
            f"""
            Here are the list of guidelines:
            - The travel location is in {query_params.travel_location}
            - The travel dates would be {from_date} to {to_date}
            - The user will be staying at {query_params.home_location}
            - The user is interested in {tags}
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

        day_locations = self.extract_location_country(response_data)
        is_success = False
        optimized_day_locations = []

        while not is_success:
            optimized_day_locations, is_success = self.optimize_locations_gmap(
                query_params, day_locations
            )
            if not is_success:
                self._ai_service.add_user_prompt(
                    f"""
                    Change the following locations - {optimized_day_locations}
                    """
                )
                response = self._ai_service.ai_model.invoke(
                    input=self._ai_service.prompts
                )
                self._ai_service.add_assistant_prompt(response.content)
                response_data = json.loads(response.content)
                day_locations = self.extract_location_country(response_data)

        if not optimized_day_locations:
            return {}

        response_data = self.reschedule_plan(optimized_day_locations)
        logger.info(response_data)

        self.integrate_gmaps_urls(query_params, optimized_day_locations, response_data)

        return ResponseSchema(data=response_data)

    def generate_tags(self):
        self._ai_service.initialize_system_prompt(self.sys_prompt)
        self._ai_service.add_user_prompt(
            """
            Generate a maximum of 32 random list of single word tags that will help you further give personalized results. 
            Return the list of tags in a JSON format with key named tags.
            """
        )
        response = self._ai_service.ai_model.invoke(input=self._ai_service.prompts)
        response_data = json.loads(response.content)

        return response_data
