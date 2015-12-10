# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GEOHEX
                                 A QGIS plugin
 This plugin creates GEOHEX Zone.
                             -------------------
        begin                : 2015-12-06
        copyright            : (C) 2015 by PEmugi
        email                : PEmugi@chizuwota.net
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load GEOHEX class from file GEOHEX.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .qgeohex import GEOHEX
    return GEOHEX(iface)
