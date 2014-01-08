#
# Copyright (c) 2014, Texas Water Development Board
# All rights reserved.
#
# This code is open-source. See LICENSE file for details.
#

# 3rd party imports
import fiona
from shapely.geometry import MultiLineString, shape
from shapely.geometry.base import BaseGeometry

# ETS imports
from scimath import units
from traits.api import Dict, Instance, Float, HasTraits, Property, provides, Str

# local imports
from hydropick.model.i_lake import ILake


@provides(ILake)
class Lake(HasTraits):
    """ A model of a lake that contains its shoreline, map projection
    information, and other metadata.

    This implementation assumes a standard shapefile containing the
    shoreline a a MultiLineString or a number of LineString features.
    """

    #### 'ILake' protocol #################################################

    #: Name of the lake
    name = Str

    #: The coordinate reference system as a pyproj dictionary mapping
    crs = Dict

    #: Elevation (in elevation_units)
    elevation = Property(Float)

    def _get_elevation(self):
        return self._properties.get('Elevation', None)

    #: Units for elevation
    elevation_units = Instance(units.unit.unit)

    def _elevation_units_default(self):
        """ Assume that units in shapefile are feet
        """
        return units.length.feet

    #: The geometry of the shoreline.
    #: Typically a MultiLineString, but could conceivably be a
    #: MultiPolygon or collections of lines and/or polygons.
    shoreline = Instance(BaseGeometry)

    def _shoreline_default(self):
        """ Load the shoreline from GIS file.

        NB: Currently has side effects, loading crs and properties traits.
        """
        with fiona.open(self.shoreline_file) as f:
            self.crs = f.crs
            geoms = []
            for rec in f:
                geoms.append(shape(rec['geometry']))
            # XXX: assuming that the proerties aren't varying by geometry
            self._properties = rec['properties']
            if len(geoms) == 1:
                return geoms[0]
            else:
                # XXX: this assumes we'll always get lines, not polygons or other
                return MultiLineString(geoms)

    #### 'Lake' protocol ######################################################

    #: The path to the GIS file containing the lake geometry
    shoreline_file = Str

    #### Private protocol #####################################################

    #: Private trait to hold properties loaded from shapefile
    _properties = Dict
