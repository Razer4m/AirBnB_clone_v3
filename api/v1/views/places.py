#!/usr/bin/python3
"""
Defines the RESTful API actions for Place objects.
Handles all default CRUD operations for Place.
"""

from flask import jsonify, abort, request
from api.v1.views import app_views
from models import storage
from models.place import Place
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.user import User


@app_views.route('/cities/<city_id>/places',
                 methods=['GET'], strict_slashes=False)
def get_places(city_id):
    """Retrieves the list of all Place objects of a City"""
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    return jsonify([place.to_dict() for place in city.places])


@app_views.route('/places/<place_id>',
                 methods=['GET'], strict_slashes=False)
def get_place(place_id):
    """Retrieves a specific Place object by its ID"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>',
                 methods=['DELETE'], strict_slashes=False)
def delete_place(place_id):
    """Deletes a specific Place object by its ID"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    storage.delete(place)
    storage.save()
    return jsonify({}), 200


@app_views.route('/cities/<city_id>/places',
                 methods=['POST'], strict_slashes=False)
def create_place(city_id):
    """Creates a new Place object linked to a specific City"""
    city = storage.get(City, city_id)
    if not city:
        abort(404)
    if not request.get_json():
        abort(400, description="Not a JSON")
    if 'user_id' not in request.get_json():
        abort(400, description="Missing user_id")
    if 'name' not in request.get_json():
        abort(400, description="Missing name")

    data = request.get_json()
    user = storage.get(User, data['user_id'])
    if not user:
        abort(404)

    new_place = Place(**data)
    new_place.city_id = city_id
    storage.new(new_place)
    storage.save()
    return jsonify(new_place.to_dict()), 201


@app_views.route('/places/<place_id>', methods=['PUT'], strict_slashes=False)
def update_place(place_id):
    """Updates a specific Place object by its ID"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    if not request.get_json():
        abort(400, description="Not a JSON")

    data = request.get_json()
    ignored_keys = ['id', 'user_id', 'city_id', 'created_at', 'updated_at']
    for key, value in data.items():
        if key not in ignored_keys:
            setattr(place, key, value)
    storage.save()
    return jsonify(place.to_dict()), 200


@app_views.route('/places_search',
                 methods=['POST'], strict_slashes=False)
def search_places():
    """Retrieves all Place objects based on JSON search criteria"""
    if not request.get_json():
        abort(400, description="Not a JSON")

    data = request.get_json()
    state_ids = data.get('states', [])
    city_ids = data.get('cities', [])
    amenity_ids = data.get('amenities', [])

    if not state_ids and not city_ids:
        places = storage.all(Place).values()
    else:
        places = set()
        if state_ids:
            for state_id in state_ids:
                state = storage.get(State, state_id)
                if state:
                    for city in state.cities:
                        places.update(city.places)
        if city_ids:
            for city_id in city_ids:
                city = storage.get(City, city_id)
                if city:
                    places.update(city.places)

    if amenity_ids:
        filtered_places = []
        for place in places:
            if all(
                storage.get(Amenity, amenity_id) in place.amenities
                for amenity_id in amenity_ids
            ):
                filtered_places.append(place)
        places = filtered_places

    return jsonify([place.to_dict() for place in places])
