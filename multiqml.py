import os
import sys
import tempfile
import gettext

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from ui_multiqml import Ui_MultiQmlForm

# create the dialog for mapserver export
class MultiQmlDlg(QDialog, Ui_MultiQmlForm):
	def __init__(self, parent, iface):
		QDialog.__init__(self, parent)
		self.setupUi(self)

		self.iface = iface

		self.tmpQmlSrcList = []
		self.version = int( QGis.QGIS_VERSION[ 2 ] )
		if self.version > 4:
		  self.mapLayers = self.iface.legendInterface().layers()
		else:
			self.mapLayers = QgsMapLayerRegistry.instance().mapLayers().values()
		self.fileNameStyle = QString()

		QObject.connect( self.lvMapLayers, SIGNAL( "clicked( const QModelIndex & )" ), self.doApplyStyleButtonEnabled )
		QObject.connect( self.rbnRasterLayers, SIGNAL( "toggled( bool )" ), self.doApplyStyleButtonEnabled )
		QObject.connect( self.rbnVectorLayers, SIGNAL( "toggled( bool )" ), self.doApplyStyleButtonEnabled )
		QObject.connect( self.checkMakeDefault, SIGNAL( "stateChanged( int )" ), self.showWarning )

		self.loadMapLayers()
		self.readSettings()

	def showWarning( self ):
		#if self.checkMakeDefault.checkState() == Qt.Checked:
		#	res = QMessageBox.warning( self, self.tr( "MultiQML" ),
    #                    self.tr( "Enabling this option will cause overwriting of any existing QML files. Are you sure?" ),
    #                    QMessageBox.Yes | QMessageBox.No )
		#	if res != QMessageBox.Yes:
		#		self.checkMakeDefault.setCheckState( Qt.Unchecked )
		return

	@pyqtSignature( "" )
	def on_pbnApplyStyle_clicked(self):
		def isRasterQml():
			qmlFile = open( self.fileNameStyle, "rb" )
			line = qmlFile.readline()
			result = False
			while line != "":
				if "<rasterproperties>" in line:
					result = True
					break
				line = qmlFile.readline()
			qmlFile.close()
			return result

		myLastUsedDir = self.settings.value( "multiqmlplugin/lastStyleDir" ).toString()
		self.fileNameStyle = QFileDialog.getOpenFileName(self, QApplication.translate("MultiQmlDlg", "Open style"), myLastUsedDir, QApplication.translate("MultiQmlDlg", "QGIS apply style file (*.qml)"))

		if not self.fileNameStyle.isEmpty():
			selected = self.lvMapLayers.selectedIndexes()
			for i in selected:
				if self.version > 4:
				  layer = self.mapLayers[i.row()]
				else:
					layer = self.mapLayers[ self.dictLayers[ i.data().toString() ] ]

				if ( layer.type() == QgsMapLayer.VectorLayer ) and isRasterQml():
					self.myPluginMessage( QApplication.translate("MultiQmlDlg", "Unable to apply raster qml style \"%1\" to vector layer \"%2\".")\
						.arg(self.fileNameStyle).arg(layer.name()), "critical" )
					continue
				elif ( layer.type() == QgsMapLayer.RasterLayer ) and not isRasterQml():
					self.myPluginMessage( QApplication.translate("MultiQmlDlg", "Unable to apply vector qml style \"%1\" to raster layer \"%2\".")\
						.arg(self.fileNameStyle).arg(layer.name()), "critical" )
					continue

				message, isLoaded = layer.loadNamedStyle(self.fileNameStyle)
				if not isLoaded:
					self.myPluginMessage( QApplication.translate("MultiQmlDlg", "Unable to apply qml style \"%1\" to layer \"%2\"\n%3.")\
						.arg(self.fileNameStyle).arg(layer.name()).arg(message), "critical" )

				if self.checkMakeDefault.isChecked():
					msg, res = layer.saveDefaultStyle()

  			if self.version >= 5:
	  			self.iface.legendInterface().refreshLayerSymbology( layer )

			self.iface.mapCanvas().refresh()
			self.settings.setValue( "multiqmlplugin/lastStyleDir", QVariant( os.path.dirname( unicode( self.fileNameStyle ) ) ) )
		else:
			self.myPluginMessage( QApplication.translate("MultiQmlDlg", "A style was not applied." ), "information" )

	@pyqtSignature( "" )
	def on_pbnRestoreDefaultStyle_clicked(self):
		selected = self.lvMapLayers.selectedIndexes()
		for i in selected:
			if self.version > 4:
				layer = self.mapLayers[i.row()]
			else:
				layer = self.mapLayers[ self.dictLayers[ i.data().toString() ] ]
			message, isLoaded = layer.loadNamedStyle(self.tmpQmlSrcList[i.row()])
			if not isLoaded: self.myPluginMessage( QApplication.translate("MultiQmlDlg",  "Unable to restory an initial style for layer \"%1\"\n%2.")\
				.arg(layer.name()).arg(message), "critical" )
			if self.checkMakeDefault.isChecked():
				msg, res = layer.saveDefaultStyle()
			if self.version >= 5:
				self.iface.legendInterface().refreshLayerSymbology( layer )
			self.iface.mapCanvas().refresh()

	@pyqtSignature( "" )
	def on_pbnSelectAllLayers_clicked(self):
		self.lvMapLayers.selectAll()
		self.pbnSelectAllLayers.setEnabled( True )
		self.pbnApplyStyle.setEnabled( True )

	def loadMapLayers( self ):
		layersNameList = QStringList()
		if self.version > 4:
			for i in range( len( self.mapLayers ) ):
				layersNameList.append( self.mapLayers[i].name() )
				self.tmpQmlSrcList.append( tempfile.mktemp( '.qml' ) )
				message, isSaved = self.mapLayers[i].saveNamedStyle(self.tmpQmlSrcList[i])
		else:
			self.dictLayers={}
			for i in range( len( self.mapLayers ) ):
				layersNameList.append( self.mapLayers[i].name() )
				self.dictLayers[ self.mapLayers[i].name() ] = i
				self.tmpQmlSrcList.append( tempfile.mktemp( '.qml' ) )
				message, isSaved = self.mapLayers[i].saveNamedStyle(self.tmpQmlSrcList[i])
			layersNameList.sort()

		self.lvMapLayers.setModel( QStringListModel( layersNameList, self ) )
		self.lvMapLayers.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.lvMapLayers.setEditTriggers( QAbstractItemView.NoEditTriggers )

		if self.lvMapLayers.model().rowCount() == 0:
			self.pbnSelectAllLayers.setEnabled( False )

	@pyqtSignature( "" )
	def on_pbnClose_clicked(self):
		self.writeSettings()
		self.close()

	def closeEvent( self, event ):
		for i in range( len( self.mapLayers ) ):
			os.remove( self.tmpQmlSrcList[i] )
		event.accept()

	def doApplyStyleButtonEnabled( self ):
		if len( self.lvMapLayers.selectedIndexes() ) == 0:
			self.pbnApplyStyle.setEnabled( False )
		else:
			self.pbnApplyStyle.setEnabled( True )

	def on_rbnRasterLayers_toggled( self, checked ):
		for i in range( len( self.mapLayers ) ):
			if self.version > 4:
				idx = self.lvMapLayers.model().index( i, 0 )
				layerName = self.lvMapLayers.model().data( idx, 0 ).toString()
				for j in range( len( self.mapLayers ) ):
					if self.mapLayers[j].name() == layerName:
						break
				if checked and ( self.mapLayers[i].type() != QgsMapLayer.VectorLayer ):
					self.lvMapLayers.setRowHidden( i, False )
				elif not checked and ( self.mapLayers[i].type() == QgsMapLayer.RasterLayer ):
					self.lvMapLayers.setRowHidden( i, True )
				else:
					self.lvMapLayers.setRowHidden( i, True )

			if checked and ( self.mapLayers[i].type() != QgsMapLayer.VectorLayer ):
				self.lvMapLayers.setRowHidden( i, False )
			elif not checked and ( self.mapLayers[i].type() == QgsMapLayer.RasterLayer ):
				self.lvMapLayers.setRowHidden( i, True )
			else:
				self.lvMapLayers.setRowHidden( i, True )

	def on_rbnVectorLayers_toggled( self, checked ):
		for i in range( len( self.mapLayers ) ):
			if self.version > 4:
				idx = self.lvMapLayers.model().index( i, 0 )
				layerName = self.lvMapLayers.model().data( idx, 0 ).toString()
				for j in range( len( self.mapLayers ) ):
					if self.mapLayers[j].name() == layerName:
						break
				if checked and ( self.mapLayers[i].type() != QgsMapLayer.RasterLayer ):
					self.lvMapLayers.setRowHidden( i, False )
				elif not checked and ( self.mapLayers[i].type() == QgsMapLayer.VectorLayer ):
					self.lvMapLayers.setRowHidden( i, True )
				else:
					self.lvMapLayers.setRowHidden( i, True )

			if checked and ( self.mapLayers[i].type() != QgsMapLayer.RasterLayer ):
				self.lvMapLayers.setRowHidden( i, False )
			elif not checked and ( self.mapLayers[i].type() == QgsMapLayer.VectorLayer ):
				self.lvMapLayers.setRowHidden( i, True )
			else:
				self.lvMapLayers.setRowHidden( i, True )

	def readSettings(self):
		self.settings = QSettings( "Gis-Lab", "MultiQml" )
		self.resize( self.settings.value( "multiqmlplugin/size", QVariant( QSize( 330, 230 ) ) ).toSize() )
		self.move( self.settings.value( "multiqmlplugin/pos", QVariant( QPoint( 0, 0 ) ) ).toPoint() )
		self.rbnRasterLayers.setChecked( self.settings.value( "multiqmlplugin/isRasterChecked", QVariant( True ) ).toBool() )
		self.rbnVectorLayers.setChecked( self.settings.value( "multiqmlplugin/isVectorChecked", QVariant( False ) ).toBool() )
		self.checkMakeDefault.setCheckState( self.settings.value( "multiqmlplugin/saveDefault", QVariant( 0 ) ).toInt()[ 0 ] )

	def writeSettings(self):
		self.settings = QSettings( "Gis-Lab", "MultiQml" )
		self.settings.setValue( "multiqmlplugin/size", QVariant( self.size() ) )
		self.settings.setValue( "multiqmlplugin/pos", QVariant( self.pos() ) )
		self.settings.setValue( "multiqmlplugin/isRasterChecked", QVariant( self.rbnRasterLayers.isChecked() ) )
		self.settings.setValue( "multiqmlplugin/isVectorChecked", QVariant( self.rbnVectorLayers.isChecked() ) )
		self.settings.setValue( "multiqmlplugin/saveDefault", QVariant( self.checkMakeDefault.checkState() ) )

	def myPluginMessage( self, msg, type ):
		if type == "information":
			QMessageBox.information(self, QApplication.translate("MultiQmlDlg", "Information"), msg )
		elif type == "critical":
			QMessageBox.critical(self, QApplication.translate("MultiQmlDlg", "Error"), msg )
