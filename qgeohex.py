# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GEOHEX
                                 A QGIS plugin
 This plugin creates GEOHEX Zone.
                              -------------------
        begin                : 2015-12-06
        git sha              : $Format:%H$
        copyright            : (C) 2015 by PEmugi
        email                : PEmugi@chizuwota.net
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from qgeohex_dialog import GEOHEXDialog
import os.path
import geohex
import qgis.core

class GEOHEX:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GEOHEX_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = GEOHEXDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&GEOHEX')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'GEOHEX')
        self.toolbar.setObjectName(u'GEOHEX')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GEOHEX', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/GEOHEX/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'GEOHEX'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&GEOHEX'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
                
        layers = self.iface.legendInterface().layers()
        layer_list = [l.name() for l in layers]
        layer_list.append('Current Map Window')
        self.dlg.extentLayerList.clear()
        self.dlg.extentLayerList.addItems(layer_list)

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()

        # See if OK was pressed
        if result:
            gh_level = self.dlg.levelLineEdit.text()
            
            selected_layer_idx = self.dlg.extentLayerList.currentIndex()
            
            
            if selected_layer_idx == len(layer_list) - 1:         
                w_extent = self.iface.mapCanvas().extent()
                w_crs = self.iface.mapCanvas().mapSettings().destinationCrs()
            else:
                selected_layer = layers[selected_layer_idx]
                w_extent = selected_layer.extent()
                w_crs = selected_layer.crs()
            
            w_srid = w_crs.authid()
            
            wgs84 = qgis.core.QgsCoordinateReferenceSystem(4326)
            transform = qgis.core.QgsCoordinateTransform(w_crs, wgs84)
            gh_extent = transform.transformBoundingBox(w_extent)
            
            out_transform = qgis.core.QgsCoordinateTransform(wgs84, w_crs)
            
            zones = geohex.create_zones_by_extent(int(gh_level), 
                                                gh_extent.xMinimum(),
                                                gh_extent.yMinimum(),
                                                gh_extent.xMaximum(),
                                                gh_extent.yMaximum())
            
            #create event layer
            gh_layer = qgis.core.QgsVectorLayer('Polygon?crs={srid}&field=code:string(50)'.format(srid=w_srid), 'geohex_lev'+gh_level, 'memory')
            hg_dp = gh_layer.dataProvider()
            for zone in zones:
                f = qgis.core.QgsFeature(gh_layer.pendingFields())
                f.setAttribute('code', zone.code)
                geom = qgis.core.QgsGeometry.fromWkt(zone.get_wkt_deg())
                geom.transform(out_transform)
                f.setGeometry(geom)
                hg_dp.addFeatures([f])
            gh_layer.updateExtents()
            
            qgis.core.QgsMapLayerRegistry.instance().addMapLayer(gh_layer)
            
            
             
            