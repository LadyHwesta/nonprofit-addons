# -*- coding: utf-8 -*-
"""Small great-circle helpers for the row/spot -> lat/lng placement math.

Good enough for placing booths across a festival footprint (city-block to
few-hundred-meter scale) - not survey-grade, and not meant to be. See the
module README for the calibration workflow this backs.
"""
import math

EARTH_RADIUS_M = 6371000.0


def destination_point(lat, lng, bearing_deg, distance_m):
    """Given a start point, a compass bearing and a distance, return the
    (lat, lng) reached - the standard "destination point given distance and
    bearing" great-circle formula.
    """
    if not distance_m:
        return lat, lng
    ang_dist = distance_m / EARTH_RADIUS_M
    bearing = math.radians(bearing_deg)
    lat1 = math.radians(lat)
    lng1 = math.radians(lng)

    lat2 = math.asin(
        math.sin(lat1) * math.cos(ang_dist)
        + math.cos(lat1) * math.sin(ang_dist) * math.cos(bearing)
    )
    lng2 = lng1 + math.atan2(
        math.sin(bearing) * math.sin(ang_dist) * math.cos(lat1),
        math.cos(ang_dist) - math.sin(lat1) * math.sin(lat2),
    )
    return math.degrees(lat2), (math.degrees(lng2) + 540) % 360 - 180


def bearing_and_distance(lat1, lng1, lat2, lng2):
    """Inverse of destination_point: given two points, return the compass
    bearing (0-360) and great-circle distance in meters from point 1 to
    point 2. Used by the calibration wizard.
    """
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_lambda = math.radians(lng2 - lng1)

    y = math.sin(d_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(d_lambda)
    bearing = (math.degrees(math.atan2(y, x)) + 360) % 360

    d_phi = phi2 - phi1
    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )
    distance = EARTH_RADIUS_M * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return bearing, distance
