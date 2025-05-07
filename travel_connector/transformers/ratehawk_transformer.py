"""
Transformer for the Ratehawk API responses and requests.
"""

import logging
from datetime import datetime, date, time
from typing import Dict, Any, List, Optional
from decimal import Decimal

from travel_connector.transformers.base_transformer import BaseTransformer
from travel_connector.models.hotel import Hotel, HotelAmenity
from travel_connector.models.room import Room, RoomAmenity, RoomRate
from travel_connector.models.booking import Booking, BookingStatus
from travel_connector.models.location import Location, Address, Coordinates
from travel_connector.utils.exceptions import TransformationError
from travel_connector.utils.mapping import amenity_mapping

logger = logging.getLogger(__name__)


class RatehawkTransformer(BaseTransformer):
    """Transformer for Ratehawk API data"""
    
    def transform_hotel_data(self, data: Dict[str, Any]) -> Hotel:
        """
        Transform hotel data from Ratehawk API response to standardized Hotel model
        
        Args:
            data: Hotel data from Ratehawk API response
            
        Returns:
            Standardized Hotel object
            
        Raises:
            TransformationError: If there's an issue with the data transformation
        """
        try:
            # Extract basic hotel information
            hotel_id = str(data.get("id"))
            if not hotel_id:
                raise TransformationError("Missing hotel ID in Ratehawk response")
            
            # Create location object
            location_data = data.get("location", {})
            address = Address(
                line1=location_data.get("address", ""),
                line2=None,
                city=location_data.get("city", {}).get("name", ""),
                postal_code=location_data.get("zip_code"),
                state=location_data.get("state", {}).get("name"),
                country=location_data.get("country", {}).get("name", ""),
                country_code=location_data.get("country", {}).get("code", ""),
                formatted_address=location_data.get("address")
            )
            
            coordinates = None
            if "geo" in location_data and "lat" in location_data["geo"] and "lon" in location_data["geo"]:
                coordinates = Coordinates(
                    latitude=float(location_data["geo"]["lat"]),
                    longitude=float(location_data["geo"]["lon"]),
                    source="ratehawk",
                    source_id=f"{hotel_id}_geo",
                    id=f"ratehawk_coordinates_{hotel_id}"
                )
            
            location = Location(
                address=address,
                coordinates=coordinates,
                neighborhood=location_data.get("neighborhood"),
                district=location_data.get("district"),
                nearby_attractions=[],
                distance_to_center=location_data.get("distance_to_center"),
                source="ratehawk",
                source_id=f"{hotel_id}_location",
                id=f"ratehawk_location_{hotel_id}"
            )
            
            # Map amenities to standardized format
            amenities = []
            for amenity in data.get("amenities", []):
                std_amenity = amenity_mapping.get(amenity.lower())
                if std_amenity:
                    amenities.append(std_amenity)
            
            # Create the hotel object
            hotel = Hotel(
                id=f"ratehawk_hotel_{hotel_id}",
                source="ratehawk",
                source_id=hotel_id,
                name=data.get("name", ""),
                description=data.get("description", ""),
                category=data.get("star_rating"),
                location=location,
                phone=data.get("phone"),
                email=data.get("email"),
                website=data.get("website"),
                amenities=amenities,
                images=data.get("images", []),
                properties={},
                raw_data=data
            )
            
            return hotel
            
        except Exception as e:
            logger.error(f"Error transforming hotel data: {str(e)}")
            raise TransformationError(f"Failed to transform Ratehawk hotel data: {str(e)}")
    
    def transform_hotel_details(self, data: Dict[str, Any]) -> Hotel:
        """
        Transform detailed hotel data from Ratehawk API to standardized Hotel model
        
        Args:
            data: Detailed hotel data from Ratehawk API response
            
        Returns:
            Standardized Hotel object with detailed information
            
        Raises:
            TransformationError: If there's an issue with the data transformation
        """
        try:
            # First transform the basic hotel data
            hotel = self.transform_hotel_data(data)
            
            # Add more detailed information
            detailed_data = data.get("details", {})
            
            # Add check-in/check-out times if available
            if "checkin_time" in detailed_data:
                try:
                    checkin_time_parts = detailed_data["checkin_time"].split(":")
                    hotel.check_in_time = time(int(checkin_time_parts[0]), int(checkin_time_parts[1]))
                except (ValueError, IndexError):
                    logger.warning(f"Invalid check-in time format: {detailed_data.get('checkin_time')}")
            
            if "checkout_time" in detailed_data:
                try:
                    checkout_time_parts = detailed_data["checkout_time"].split(":")
                    hotel.check_out_time = time(int(checkout_time_parts[0]), int(checkout_time_parts[1]))
                except (ValueError, IndexError):
                    logger.warning(f"Invalid check-out time format: {detailed_data.get('checkout_time')}")
            
            # Add policies
            hotel.cancellation_policy = detailed_data.get("cancellation_policy")
            hotel.children_policy = detailed_data.get("children_policy")
            hotel.pet_policy = detailed_data.get("pet_policy")
            
            # Add ratings
            if "rating" in data:
                hotel.rating = float(data["rating"]) if data["rating"] is not None else None
            
            if "review_count" in data:
                hotel.review_count = int(data["review_count"]) if data["review_count"] is not None else None
            
            return hotel
            
        except Exception as e:
            logger.error(f"Error transforming hotel details: {str(e)}")
            raise TransformationError(f"Failed to transform Ratehawk hotel details: {str(e)}")
    
    def transform_room_data(self, data: Dict[str, Any], hotel_id: str) -> Room:
        """
        Transform room data from Ratehawk API to standardized Room model
        
        Args:
            data: Room data from Ratehawk API response
            hotel_id: ID of the hotel this room belongs to
            
        Returns:
            Standardized Room object
            
        Raises:
            TransformationError: If there's an issue with the data transformation
        """
        try:
            room_id = str(data.get("id"))
            if not room_id:
                raise TransformationError("Missing room ID in Ratehawk response")
            
            # Map amenities to standardized format
            amenities = []
            for amenity in data.get("amenities", []):
                std_amenity = amenity_mapping.get(amenity.lower())
                if std_amenity:
                    amenities.append(std_amenity)
            
            # Create rate plans for the room
            rates = []
            for rate_data in data.get("rates", []):
                try:
                    rate_id = str(rate_data.get("id"))
                    if not rate_id:
                        logger.warning("Missing rate ID in Ratehawk room rate data")
                        continue
                    
                    # Parse dates
                    checkin_date = datetime.strptime(rate_data.get("checkin"), "%Y-%m-%d").date() if rate_data.get("checkin") else None
                    checkout_date = datetime.strptime(rate_data.get("checkout"), "%Y-%m-%d").date() if rate_data.get("checkout") else None
                    
                    if not checkin_date or not checkout_date:
                        logger.warning("Missing date information in Ratehawk room rate data")
                        continue
                    
                    rate = RoomRate(
                        id=f"ratehawk_rate_{rate_id}",
                        source="ratehawk",
                        source_id=rate_id,
                        rate_plan_id=rate_id,
                        rate_plan_name=rate_data.get("name"),
                        price_per_night=Decimal(str(rate_data.get("price_per_night", 0))),
                        total_price=Decimal(str(rate_data.get("total_price", 0))),
                        currency=rate_data.get("currency", "EUR"),
                        check_in_date=checkin_date,
                        check_out_date=checkout_date,
                        max_occupancy=int(rate_data.get("max_occupancy", 1)),
                        board_type=rate_data.get("board_type"),
                        is_refundable=rate_data.get("is_refundable", False),
                        cancellation_policy=rate_data.get("cancellation_policy"),
                        raw_data=rate_data
                    )
                    rates.append(rate)
                    
                except Exception as e:
                    logger.warning(f"Failed to transform rate data: {str(e)}")
                    continue
            
            # Create the room object
            room = Room(
                id=f"ratehawk_room_{room_id}",
                source="ratehawk",
                source_id=room_id,
                hotel_id=hotel_id,
                name=data.get("name", ""),
                description=data.get("description", ""),
                max_occupancy=int(data.get("max_occupancy", 1)),
                max_adults=int(data.get("max_adults", 1)),
                max_children=int(data.get("max_children", 0)) if data.get("max_children") is not None else None,
                size_sqm=float(data.get("size_sqm")) if data.get("size_sqm") is not None else None,
                bed_type=data.get("bed_type"),
                bed_count=int(data.get("bed_count")) if data.get("bed_count") is not None else None,
                amenities=amenities,
                images=data.get("images", []),
                available=data.get("available", True),
                rates=rates,
                raw_data=data
            )
            
            return room
            
        except Exception as e:
            logger.error(f"Error transforming room data: {str(e)}")
            raise TransformationError(f"Failed to transform Ratehawk room data: {str(e)}")
    
    def transform_booking_response(self, data: Dict[str, Any]) -> Booking:
        """
        Transform booking data from Ratehawk API to standardized Booking model
        
        Args:
            data: Booking data from Ratehawk API response
            
        Returns:
            Standardized Booking object
            
        Raises:
            TransformationError: If there's an issue with the data transformation
        """
        try:
            booking_id = str(data.get("id"))
            if not booking_id:
                raise TransformationError("Missing booking ID in Ratehawk response")
            
            # Map status to standardized booking status
            status_mapping = {
                "pending": BookingStatus.PENDING,
                "confirmed": BookingStatus.CONFIRMED,
                "cancelled": BookingStatus.CANCELLED,
                "completed": BookingStatus.COMPLETED,
                "failed": BookingStatus.FAILED
            }
            
            status = status_mapping.get(data.get("status", "").lower(), BookingStatus.PENDING)
            
            # Parse dates
            checkin_date = datetime.strptime(data.get("checkin"), "%Y-%m-%d").date() if data.get("checkin") else None
            checkout_date = datetime.strptime(data.get("checkout"), "%Y-%m-%d").date() if data.get("checkout") else None
            
            if not checkin_date or not checkout_date:
                raise TransformationError("Missing date information in Ratehawk booking response")
            
            # Parse timestamps
            booked_at = datetime.fromisoformat(data.get("created_at").replace("Z", "+00:00")) if data.get("created_at") else datetime.utcnow()
            cancelled_at = datetime.fromisoformat(data.get("cancelled_at").replace("Z", "+00:00")) if data.get("cancelled_at") else None
            
            # Create the booking object
            booking = Booking(
                id=f"ratehawk_booking_{booking_id}",
                source="ratehawk",
                source_id=booking_id,
                booking_number=data.get("reference_number", booking_id),
                status=status,
                hotel_id=str(data.get("hotel_id", "")),
                room_id=str(data.get("room_id", "")),
                rate_plan_id=str(data.get("rate_id", "")),
                guest_name=data.get("guest", {}).get("name", ""),
                guest_email=data.get("guest", {}).get("email"),
                guest_phone=data.get("guest", {}).get("phone"),
                number_of_guests=int(data.get("guests", 1)),
                number_of_adults=int(data.get("adults", 1)),
                number_of_children=int(data.get("children", 0)),
                check_in_date=checkin_date,
                check_out_date=checkout_date,
                special_requests=data.get("special_requests"),
                total_price=Decimal(str(data.get("total_price", 0))),
                currency=data.get("currency", "EUR"),
                payment_status=data.get("payment_status"),
                payment_method=data.get("payment_method"),
                booked_at=booked_at,
                cancelled_at=cancelled_at,
                raw_data=data
            )
            
            return booking
            
        except Exception as e:
            logger.error(f"Error transforming booking response: {str(e)}")
            raise TransformationError(f"Failed to transform Ratehawk booking response: {str(e)}")
    
    def transform_booking_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform booking request data to Ratehawk API format
        
        Args:
            data: Booking request data in standardized format
            
        Returns:
            Booking data in Ratehawk API format
            
        Raises:
            TransformationError: If there's an issue with the data transformation
        """
        try:
            # Extract source IDs if they contain prefixes
            hotel_id = data.get("hotel_id", "")
            room_id = data.get("room_id", "")
            rate_id = data.get("rate_id", "")
            
            if hotel_id.startswith("ratehawk_hotel_"):
                hotel_id = hotel_id.replace("ratehawk_hotel_", "")
            
            if room_id.startswith("ratehawk_room_"):
                room_id = room_id.replace("ratehawk_room_", "")
                
            if rate_id.startswith("ratehawk_rate_"):
                rate_id = rate_id.replace("ratehawk_rate_", "")
            
            # Format guest data
            guest_data = data.get("guest", {})
            if isinstance(guest_data, str):
                # If just a name is provided, split it into first/last name
                name_parts = guest_data.split(" ", 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ""
                guest = {
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": data.get("guest_email", ""),
                    "phone": data.get("guest_phone", "")
                }
            else:
                # If a dict is provided, use its values
                guest = {
                    "first_name": guest_data.get("first_name", ""),
                    "last_name": guest_data.get("last_name", ""),
                    "email": guest_data.get("email", data.get("guest_email", "")),
                    "phone": guest_data.get("phone", data.get("guest_phone", ""))
                }
            
            # Create the Ratehawk booking request
            ratehawk_request = {
                "hotel_id": hotel_id,
                "room_id": room_id,
                "rate_id": rate_id,
                "checkin": data.get("checkin", data.get("check_in_date")).isoformat() if isinstance(data.get("checkin", data.get("check_in_date")), date) else data.get("checkin", data.get("check_in_date")),
                "checkout": data.get("checkout", data.get("check_out_date")).isoformat() if isinstance(data.get("checkout", data.get("check_out_date")), date) else data.get("checkout", data.get("check_out_date")),
                "adults": data.get("adults", data.get("number_of_adults", 1)),
                "children": data.get("children", data.get("number_of_children", [])),
                "guest": guest,
                "special_requests": data.get("special_requests", ""),
                "currency": data.get("currency", "EUR")
            }
            
            return ratehawk_request
            
        except Exception as e:
            logger.error(f"Error transforming booking request: {str(e)}")
            raise TransformationError(f"Failed to transform booking request to Ratehawk format: {str(e)}")
    
    def transform_search_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform hotel search parameters to Ratehawk API format
        
        Args:
            params: Search parameters in standardized format
            
        Returns:
            Search parameters in Ratehawk API format
            
        Raises:
            TransformationError: If there's an issue with the data transformation
        """
        try:
            ratehawk_params = {}
            
            # Add location parameters
            location = params.get("location", {})
            if isinstance(location, dict):
                if "city_id" in location:
                    ratehawk_params["city_id"] = location["city_id"]
                elif "coords" in location:
                    ratehawk_params["latitude"] = location["coords"].get("lat")
                    ratehawk_params["longitude"] = location["coords"].get("lon")
                    ratehawk_params["radius"] = location.get("radius", 10)
            
            # Add date parameters
            checkin = params.get("checkin", params.get("check_in_date"))
            checkout = params.get("checkout", params.get("check_out_date"))
            
            if checkin:
                ratehawk_params["checkin"] = checkin.isoformat() if isinstance(checkin, date) else checkin
            
            if checkout:
                ratehawk_params["checkout"] = checkout.isoformat() if isinstance(checkout, date) else checkout
            
            # Add guest parameters
            ratehawk_params["adults"] = params.get("adults", 1)
            
            children = params.get("children", [])
            if children:
                if isinstance(children, list):
                    # Ratehawk expects a list of children's ages
                    ratehawk_params["children"] = children
                else:
                    # If just the number is provided, create a list with default ages (7)
                    ratehawk_params["children"] = [7] * int(children)
            
            # Add other parameters
            ratehawk_params["currency"] = params.get("currency", "EUR")
            ratehawk_params["language"] = params.get("language", "en")
            
            # Add optional filters
            if "star_rating" in params:
                ratehawk_params["star_rating"] = params["star_rating"]
            
            if "price_range" in params:
                price_range = params["price_range"]
                if "min" in price_range:
                    ratehawk_params["price_min"] = price_range["min"]
                if "max" in price_range:
                    ratehawk_params["price_max"] = price_range["max"]
            
            if "amenities" in params:
                ratehawk_params["amenities"] = params["amenities"]
            
            return ratehawk_params
            
        except Exception as e:
            logger.error(f"Error transforming search parameters: {str(e)}")
            raise TransformationError(f"Failed to transform search parameters to Ratehawk format: {str(e)}")
    
    def transform_room_search_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform room search parameters to Ratehawk API format
        
        Args:
            params: Room search parameters in standardized format
            
        Returns:
            Room search parameters in Ratehawk API format
            
        Raises:
            TransformationError: If there's an issue with the data transformation
        """
        try:
            # Room search is similar to hotel search parameters in Ratehawk
            return self.transform_search_params(params)
            
        except Exception as e:
            logger.error(f"Error transforming room search parameters: {str(e)}")
            raise TransformationError(f"Failed to transform room search parameters to Ratehawk format: {str(e)}")
