"""
/***************************************************************************
         MultiQml  -  The QGIS plugin for apply single qml to multiple raster 
		 				or vector layers
                             -------------------
    begin                : 2008-12-25
    copyright            : (C) 2008 by Lynx, Maxim Dubinin
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

import gettext

from PyQt4.QtCore import QObject, SIGNAL, SLOT, QTranslator
from PyQt4.QtGui import QMainWindow, QApplication, QAction, QIcon, \
	QDialog, QLabel, QWidget, QVBoxLayout, QPushButton

from multiqml import MultiQmlDlg
from __init__ import mVersion

import resources

class MultiQmlPlugin():
	def __init__( self, iface ):
		self.iface = iface

	def initGui( self ):
		self.actionRun = QAction( QIcon( ":/plugins/multiqml/icon.png" ),\
			QApplication.translate("MultiQmlPlugin", "MultiQml" ), self.iface.mainWindow() )
		self.actionRun.setWhatsThis( QApplication.translate("MultiQmlPlugin", "Apply single qml style to multiple raster or vector layers") )
		self.actionAbout = QAction( QApplication.translate("MultiQmlPlugin", "About" ), self.iface.mainWindow() )

		QObject.connect( self.actionRun, SIGNAL( "triggered()" ), self.run )
		QObject.connect( self.actionAbout, SIGNAL( "triggered()" ), self.about )

		self.iface.addToolBarIcon(self.actionRun)
		self.iface.addPluginToMenu( QApplication.translate("MultiQmlPlugin", "&MultiQml" ), self.actionRun )
		self.iface.addPluginToMenu( QApplication.translate("MultiQmlPlugin", "&MultiQml" ), self.actionAbout )

		self.isMultiQmlRun = False

	def unload( self ):
		self.iface.removePluginMenu( QApplication.translate("MultiQmlPlugin", "&MultiQml" ), self.actionRun )
		self.iface.removePluginMenu( QApplication.translate("MultiQmlPlugin", "&MultiQml" ), self.actionAbout )
		self.iface.removeToolBarIcon(self.actionRun)

	def run( self ):
		if not self.isMultiQmlRun:
			self.isMultiQmlRun = True
			dlgMain = MultiQmlDlg( self.iface.mainWindow(), self.iface )
			dlgMain.show()
			dlgMain.exec_()
			self.isMultiQmlRun = False

	def about( self ):
		dlgAbout = QDialog()
		dlgAbout.setWindowTitle( QApplication.translate("MultiQmlPlugin", "About", "Window title") )
		lines = QVBoxLayout( dlgAbout )
		lines.addWidget( QLabel( QApplication.translate("MultiQmlPlugin", "<b>MultiQml (Version %1):</b>" ).arg(mVersion) ) )
		lines.addWidget( QLabel( QApplication.translate("MultiQmlPlugin", "    This plugin takes single qml style and\n    applies it to multiple raster or vector layers" ) ) )
		lines.addWidget( QLabel( QApplication.translate("MultiQmlPlugin", "<b>Developers:</b>" ) ) )
		lines.addWidget( QLabel( "    Lynx (alex-86p@yandex.ru)" ) )
		lines.addWidget( QLabel( "    Maxim Dubinin (sim@gis-lab.info)" ) )
		lines.addWidget( QLabel( QApplication.translate("MultiQmlPlugin", "<b>Link:</b>") ) )
		#		lines.addWidget( QLabel( "<homepage>http://gis-lab.info/qa/qgis-multiqml-eng.html</homepage>" ) )
		link = QLabel( QApplication.translate("MultiQmlPlugin", "<a href=\"http://gis-lab.info/qa/qgis-multiqml-eng.html\">http://gis-lab.info/qa/qgis-multiqml-eng.html</a>" ) )
		link.setOpenExternalLinks( True )
		lines.addWidget( link )

		pbnClose = QPushButton(QApplication.translate("MultiQmlPlugin", "Close"))
		lines.addWidget(pbnClose)

		QObject.connect(pbnClose, SIGNAL("clicked()"), dlgAbout, SLOT("close()"))

		dlgAbout.exec_()

