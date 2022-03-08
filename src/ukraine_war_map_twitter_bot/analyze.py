from typing import Dict, List, NamedTuple, Tuple

from bs4 import BeautifulSoup, Tag
from matplotlib.path import Path
from numpy import ndarray
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union
from svgpath2mpl import parse_path

from .logs.log import get_logger

LOGGER = get_logger(__name__)

RUSSIA_COLOR = "#ebc0b3"
UKRAINE_COLOR = "#e3d975"

class _UkraineMapData(NamedTuple):
    water: List[str]
    ukraine_controlled: List[str]  # russia should be rendered OVER ukraine
    russia_controlled: List[str]
    cities: Dict[str, Tuple[float, float]]  # names to coords


def _get_basemap_and_filled_in_water(svg_xml: str) -> _UkraineMapData:
    soup = BeautifulSoup(svg_xml, features="html.parser")
    basemap = soup.find("g", {"id": "layer1", "inkscape:label": "Basemap"})

    filled_water: List[str] = []
    ukraine_controlled: List[str] = []
    russia_controlled: List[str] = []
    cities: Dict[str, Tuple[float, float]] = {}  # TODO

    for path in soup.find(
        "g", {"id": "layer2", "inkscape:label": "Rivers"}
    ).findChildren("path"):
        path: Tag = path
        if "fill:none" not in path.get("style").split(";"):
            filled_water.append(path.get("d"))

    for path in soup.find(
        "g", {"id": "layer1", "inkscape:label": "Basemap"}
    ).findChildren("path"):
        path: Tag = path
        if f"fill:{UKRAINE_COLOR}" in path.get("style").split(";"):
            print("ukraine")
            ukraine_controlled.append(path.get("d"))
        if f"fill:{RUSSIA_COLOR}" in path.get("style").split(";"):
            russia_controlled.append(path.get("d"))

    return _UkraineMapData(filled_water, ukraine_controlled, russia_controlled, cities)


def _convert_svg_path_string_to_shapely(svg_paths: List[str]) -> MultiPolygon:
    geometries: List[Polygon] = []
    for path in svg_paths:
        mpl_path: Path = parse_path(path)
        coords_list: List[ndarray] = mpl_path.to_polygons()
        geometries += [Polygon(coords) for coords in coords_list]

    geometries = [geom if geom.is_valid else geom.buffer(0) for geom in geometries]
    multi_polygon: MultiPolygon = unary_union(geometries)
    return multi_polygon


def get_areas(svg_xml: str) -> Tuple[float, float]:
    """_summary_

    Args:
        svg_xml (str): SVG data in the form of an XML string.

    Returns:
        Tuple[float, float]: Russia- and separatist-controlled area, Ukraine-controlled area.
    """
    water_xml, ua_xml, ru_xml, _ = _get_basemap_and_filled_in_water(svg_xml)
    ukraine_poly = _convert_svg_path_string_to_shapely(ua_xml) # this is a base layer, so it overlaps russian areas
    russian_poly = _convert_svg_path_string_to_shapely(ru_xml)
    water_poly = _convert_svg_path_string_to_shapely(water_xml)
    
    ukraine_land = ukraine_poly.difference(water_poly)
    russian_land = russian_poly.difference(water_poly)
    ukraine_land = ukraine_land.difference(russian_land)
    
    return float(russian_land.area), float(ukraine_land.area)