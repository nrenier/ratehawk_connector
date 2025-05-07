# Field Mapping Documentation

This document outlines the mapping between external travel API fields and the standardized data model used in the Travel Connector. It serves as a reference for understanding how different APIs' data structures are normalized into our unified model.

## Table of Contents

1. [Hotel Mapping](#hotel-mapping)
2. [Room Mapping](#room-mapping)
3. [Booking Mapping](#booking-mapping)
4. [Location Mapping](#location-mapping)
5. [Amenities Mapping](#amenities-mapping)

## Hotel Mapping

| Standardized Model Field | Ratehawk API Field | Description | Transformation |
|--------------------------|-------------------|-------------|----------------|
| `id` | - | Unique identifier | Generated as `ratehawk_hotel_{id}` |
| `source` | - | Source API identifier | Set to `"ratehawk"` |
| `source_id` | `id` | Original ID in source system | Direct mapping |
| `name` | `name` | Hotel name | Direct mapping |
| `description` | `description` | Hotel description | Direct mapping |
| `category` | `star_rating` | Star rating (1-5) | Direct mapping |
| `location` | `location` | Location object | See [Location Mapping](#location-mapping) |
| `phone` | `phone` | Contact phone | Direct mapping |
| `email` | `email` | Contact email | Direct mapping |
| `website` | `website` | Hotel website | Direct mapping |
| `amenities` | `amenities` | List of amenities | Transformed using amenity mapping |
| `images` | `images` | List of image URLs | Direct mapping |
| `check_in_time` | `details.checkin_time` | Check-in time | Converted to time object |
| `check_out_time` | `details.checkout_time` | Check-out time | Converted to time object |
| `cancellation_policy` | `details.cancellation_policy` | Cancellation policy | Direct mapping |
| `children_policy` | `details.children_policy` | Children policy | Direct mapping |
| `pet_policy` | `details.pet_policy` | Pet policy | Direct mapping |
| `rating` | `rating` | Overall rating (0-10) | Direct mapping |
| `review_count` | `review_count` | Number of reviews | Direct mapping |
| `raw_data` | - | Original raw data | Set to entire response object |

## Room Mapping

| Standardized Model Field | Ratehawk API Field | Description | Transformation |
|--------------------------|-------------------|-------------|----------------|
| `id` | - | Unique identifier | Generated as `ratehawk_room_{id}` |
| `source` | - | Source API identifier | Set to `"ratehawk"` |
| `source_id` | `id` | Original ID in source system | Direct mapping |
| `hotel_id` | - | ID of the hotel | From parameter or API response |
| `name` | `name` | Room name/type | Direct mapping |
| `description` | `description` | Room description | Direct mapping |
| `max_occupancy` | `max_occupancy` | Maximum guests | Direct mapping |
| `max_adults` | `max_adults` | Maximum adults | Direct mapping |
| `max_children` | `max_children` | Maximum children | Direct mapping |
| `size_sqm` | `size_sqm` | Room size in m² | Direct mapping |
| `bed_type` | `bed_type` | Type of bed | Direct mapping |
| `bed_count` | `bed_count` | Number of beds | Direct mapping |
| `amenities` | `amenities` | List of amenities | Transformed using amenity mapping |
| `images` | `images` | List of image URLs | Direct mapping |
| `available` | `available` | Availability flag | Direct mapping |
| `rates` | `rates` | List of rate plans | See [Rate Mapping](#rate-mapping) |
| `raw_data` | - | Original raw data | Set to entire response object |

### Rate Mapping

| Standardized Model Field | Ratehawk API Field | Description | Transformation |
|--------------------------|-------------------|-------------|----------------|
| `id` | - | Unique identifier | Generated as `ratehawk_rate_{id}` |
| `source` | - | Source API identifier | Set to `"ratehawk"` |
| `source_id` | `id` | Original ID in source system | Direct mapping |
| `rate_plan_id` | `id` | Rate plan identifier | Direct mapping |
| `rate_plan_name` | `name` | Rate plan name | Direct mapping |
| `price_per_night` | `price_per_night` | Price per night | Converted to Decimal |
| `total_price` | `total_price` | Total price for stay | Converted to Decimal |
| `currency` | `currency` | Currency code | Direct mapping |
| `check_in_date` | `checkin` | Check-in date | Converted to date object |
| `check_out_date` | `checkout` | Check-out date | Converted to date object |
| `max_occupancy` | `max_occupancy` | Maximum occupancy | Direct mapping |
| `board_type` | `board_type` | Meal plan | Direct mapping |
| `is_refundable` | `is_refundable` | Refundable flag | Direct mapping |
| `cancellation_policy` | `cancellation_policy` | Cancellation policy | Direct mapping |
| `raw_data` | - | Original raw data | Set to entire response object |

## Booking Mapping

| Standardized Model Field | Ratehawk API Field | Description | Transformation |
|--------------------------|-------------------|-------------|----------------|
| `id` | - | Unique identifier | Generated as `ratehawk_booking_{id}` |
| `source` | - | Source API identifier | Set to `"ratehawk"` |
| `source_id` | `id` | Original ID in source system | Direct mapping |
| `booking_number` | `reference_number` | Booking reference | Direct mapping, falls back to `id` |
| `status` | `status` | Booking status | Mapped to BookingStatus enum |
| `hotel_id` | `hotel_id` | Hotel identifier | Direct mapping |
| `room_id` | `room_id` | Room identifier | Direct mapping |
| `rate_plan_id` | `rate_id` | Rate plan identifier | Direct mapping |
| `guest_name` | `guest.name` | Main guest name | Direct mapping |
| `guest_email` | `guest.email` | Guest email | Direct mapping |
| `guest_phone` | `guest.phone` | Guest phone | Direct mapping |
| `number_of_guests` | `guests` | Total guests | Direct mapping |
| `number_of_adults` | `adults` | Number of adults | Direct mapping |
| `number_of_children` | `children` | Number of children | Direct mapping or length of array |
| `check_in_date` | `checkin` | Check-in date | Converted to date object |
| `check_out_date` | `checkout` | Check-out date | Converted to date object |
| `special_requests` | `special_requests` | Special requests | Direct mapping |
| `total_price` | `total_price` | Total price | Converted to Decimal |
| `currency` | `currency` | Currency code | Direct mapping |
| `payment_status` | `payment_status` | Payment status | Direct mapping |
| `payment_method` | `payment_method` | Payment method | Direct mapping |
| `booked_at` | `created_at` | Booking timestamp | Converted to datetime object |
| `cancelled_at` | `cancelled_at` | Cancellation timestamp | Converted to datetime object |
| `raw_data` | - | Original raw data | Set to entire response object |

## Location Mapping

| Standardized Model Field | Ratehawk API Field | Description | Transformation |
|--------------------------|-------------------|-------------|----------------|
| `id` | - | Unique identifier | Generated as `ratehawk_location_{hotel_id}` |
| `source` | - | Source API identifier | Set to `"ratehawk"` |
| `source_id` | - | Original ID in source system | Generated as `{hotel_id}_location` |
| `address` | `location` | Address object | See [Address Mapping](#address-mapping) |
| `coordinates` | `location.geo` | Coordinates object | See [Coordinates Mapping](#coordinates-mapping) |
| `neighborhood` | `location.neighborhood` | Neighborhood name | Direct mapping |
| `district` | `location.district` | District name | Direct mapping |
| `nearby_attractions` | - | Nearby attractions | Default to empty list |
| `distance_to_center` | `location.distance_to_center` | Distance to city center | Direct mapping |
| `raw_data` | - | Original raw data | Set to entire location object |

### Address Mapping

| Standardized Model Field | Ratehawk API Field | Description | Transformation |
|--------------------------|-------------------|-------------|----------------|
| `id` | - | Unique identifier | Generated as `ratehawk_address_{hotel_id}` |
| `source` | - | Source API identifier | Set to `"ratehawk"` |
| `source_id` | - | Original ID in source system | Generated as `{hotel_id}_address` |
| `line1` | `location.address` | Address line 1 | Direct mapping |
| `line2` | - | Address line 2 | Default to `None` |
| `city` | `location.city.name` | City name | Direct mapping |
| `postal_code` | `location.zip_code` | Postal/ZIP code | Direct mapping |
| `state` | `location.state.name` | State/Province | Direct mapping |
| `country` | `location.country.name` | Country name | Direct mapping |
| `country_code` | `location.country.code` | Country code | Direct mapping |
| `formatted_address` | `location.address` | Full address | Direct mapping |

### Coordinates Mapping

| Standardized Model Field | Ratehawk API Field | Description | Transformation |
|--------------------------|-------------------|-------------|----------------|
| `id` | - | Unique identifier | Generated as `ratehawk_coordinates_{hotel_id}` |
| `source` | - | Source API identifier | Set to `"ratehawk"` |
| `source_id` | - | Original ID in source system | Generated as `{hotel_id}_geo` |
| `latitude` | `location.geo.lat` | Latitude | Direct mapping |
| `longitude` | `location.geo.lon` | Longitude | Direct mapping |

## Amenities Mapping

The following table shows how Ratehawk amenity strings are mapped to our standardized amenity enums:

### Hotel Amenities

| Standardized Enum | Ratehawk Amenity Strings |
|-------------------|--------------------------|
| `WIFI` | `"wifi"`, `"internet"`, `"free wifi"` |
| `POOL` | `"pool"`, `"swimming pool"`, `"outdoor pool"`, `"indoor pool"` |
| `FITNESS_CENTER` | `"fitness"`, `"fitness center"`, `"gym"` |
| `RESTAURANT` | `"restaurant"` |
| `BAR` | `"bar"`, `"lounge"` |
| `SPA` | `"spa"`, `"wellness"`, `"massage"` |
| `ROOM_SERVICE` | `"room service"` |
| `PARKING` | `"parking"`, `"free parking"` |
| `BUSINESS_CENTER` | `"business center"`, `"conference"`, `"meeting rooms"` |
| `BREAKFAST` | `"breakfast"`, `"free breakfast"` |
| `LAUNDRY` | `"laundry"`, `"dry cleaning"` |
| `SHUTTLE` | `"shuttle"`, `"airport shuttle"` |
| `CONCIERGE` | `"concierge"`, `"reception"` |
| `AIR_CONDITIONING` | `"air conditioning"`, `"ac"` |
| `DISABLED_ACCESS` | `"accessible"`, `"wheelchair accessible"`, `"disability-friendly"` |
| `PET_FRIENDLY` | `"pet friendly"`, `"pets allowed"` |
| `BEACH_ACCESS` | `"beach"`, `"beach access"`, `"beachfront"` |
| `SKI_ACCESS` | `"ski"`, `"ski storage"`, `"ski-to-door"` |

### Room Amenities

| Standardized Enum | Ratehawk Amenity Strings |
|-------------------|--------------------------|
| `AIR_CONDITIONING` | `"room air conditioning"` |
| `TV` | `"tv"`, `"television"`, `"flat-screen tv"`, `"satellite tv"` |
| `WIFI` | `"room wifi"`, `"free wifi in room"` |
| `MINI_BAR` | `"minibar"`, `"mini-bar"`, `"refrigerator"` |
| `SAFE` | `"safe"`, `"safety deposit box"` |
| `HAIRDRYER` | `"hairdryer"`, `"hair dryer"` |
| `BATHTUB` | `"bathtub"`, `"bath"` |
| `SHOWER` | `"shower"` |
| `BALCONY` | `"balcony"`, `"terrace"` |
| `KITCHEN` | `"kitchen"`, `"kitchenette"` |
| `COFFEE_MACHINE` | `"coffee machine"`, `"coffee maker"`, `"tea/coffee maker"` |
| `IRON` | `"iron"`, `"ironing facilities"` |
| `DESK` | `"desk"`, `"work desk"` |
| `TELEPHONE` | `"telephone"`, `"phone"` |
| `BATH_ROBES` | `"bathrobes"`, `"bath robes"` |
| `SEA_VIEW` | `"sea view"`, `"ocean view"` |
| `MOUNTAIN_VIEW` | `"mountain view"` |
| `CITY_VIEW` | `"city view"` |

## Search Parameters Mapping

| Standardized Parameter | Ratehawk Parameter | Description | Transformation |
|------------------------|-------------------|-------------|----------------|
| `location.city_id` | `city_id` | City identifier | Direct mapping |
| `location.coords.lat` | `latitude` | Latitude | Direct mapping |
| `location.coords.lon` | `longitude` | Longitude | Direct mapping |
| `location.radius` | `radius` | Search radius in km | Direct mapping, defaults to 10 |
| `checkin` | `checkin` | Check-in date | Formatted as ISO date string |
| `checkout` | `checkout` | Check-out date | Formatted as ISO date string |
| `adults` | `adults` | Number of adults | Direct mapping |
| `children` | `children` | Children ages | Direct mapping or generates array of ages |
| `currency` | `currency` | Currency code | Direct mapping, defaults to "EUR" |
| `language` | `language` | Language code | Direct mapping, defaults to "en" |
| `star_rating` | `star_rating` | Star rating filter | Direct mapping |
| `price_range.min` | `price_min` | Minimum price | Direct mapping |
| `price_range.max` | `price_max` | Maximum price | Direct mapping |
| `amenities` | `amenities` | Amenity filters | Direct mapping |

## Booking Request Mapping

| Standardized Request | Ratehawk Request | Description | Transformation |
|----------------------|-----------------|-------------|----------------|
| `hotel_id` | `hotel_id` | Hotel identifier | Extracts ID from prefixed format |
| `room_id` | `room_id` | Room identifier | Extracts ID from prefixed format |
| `rate_id` | `rate_id` | Rate plan identifier | Extracts ID from prefixed format |
| `checkin` | `checkin` | Check-in date | Formatted as ISO date string |
| `checkout` | `checkout` | Check-out date | Formatted as ISO date string |
| `adults` | `adults` | Number of adults | Direct mapping |
| `children` | `children` | Children ages | Direct mapping |
| `guest` | `guest` | Guest information | Transformed to Ratehawk format |
| `guest.first_name` | `guest.first_name` | Guest first name | Direct mapping or extracted from full name |
| `guest.last_name` | `guest.last_name` | Guest last name | Direct mapping or extracted from full name |
| `guest.email` | `guest.email` | Guest email | Direct mapping |
| `guest.phone` | `guest.phone` | Guest phone | Direct mapping |
| `special_requests` | `special_requests` | Special requests | Direct mapping |
| `currency` | `currency` | Currency code | Direct mapping, defaults to "EUR" |
