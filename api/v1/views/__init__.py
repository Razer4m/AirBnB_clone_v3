#!/usr/bin/python3
"""
Initialization file for the views module in the AirBnB clone API.
Sets up the blueprint for API routes.
"""

from flask import Blueprint

app_views = Blueprint('app_views', __name__, url_prefix='/api/v1')

if app_views is not None:
    from api.v1.views.index import *
