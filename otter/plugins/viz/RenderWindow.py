import os
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from PyQt5 import QtWidgets, QtCore
from otter.plugins.common.ExodusIIReader import ExodusIIReader
from otter.plugins.common.VTKReader import VTKReader
from otter.plugins.common.OSplitter import OSplitter
from otter.plugins.PluginWindowBase import PluginWindowBase
from otter.plugins.viz.ParamsWindow import ParamsWindow
from otter.plugins.viz.FileProps import FileProps
from otter.plugins.viz.TextProps import TextProps


class LoadThread(QtCore.QThread):
    """ Worker thread for loading ExodusII files """

    def __init__(self, file_name):
        super().__init__()
        if file_name.endswith('.e') or file_name.endswith('.exo'):
            self._reader = ExodusIIReader(file_name)
        elif file_name.endswith('.vtk'):
            self._reader = VTKReader(file_name)
        else:
            self._reader = None

    def run(self):
        self._reader.load()

    def getReader(self):
        return self._reader


class RenderWindow(PluginWindowBase):
    """
    Window for displaying the result
    """

    def __init__(self, plugin):
        super().__init__(plugin)
        self._props = []
        self._file_name = None
        self._vtk_renderer = vtk.vtkRenderer()
        self._load_thread = None
        self._progress = None

        self.setupWidgets()
        self.setupMenuBar()
        self.setupToolBar()
        self.updateWindowTitle()

        state = self.plugin.settings.value("splitter/state")
        if state is not None:
            self._splitter.restoreState(state)

        self.setAcceptDrops(True)

        self._vtk_render_window = self._vtk_widget.GetRenderWindow()
        self._vtk_interactor = self._vtk_render_window.GetInteractor()

        self._vtk_interactor.SetInteractorStyle(
            vtk.vtkInteractorStyleTrackballCamera())

        # set anti-aliasing on
        self._vtk_renderer.SetUseFXAA(True)
        self._vtk_render_window.SetMultiSamples(1)

        self._vtk_interactor.Initialize()
        self._vtk_interactor.Start()

        self.clear()
        self.show()

        self._update_timer = QtCore.QTimer()
        self._update_timer.timeout.connect(self.onUpdateWindow)
        self._update_timer.start(250)

    def setupWidgets(self):
        self._splitter = OSplitter(QtCore.Qt.Horizontal, self)

        self._params_window = ParamsWindow(self)
        self._params_window.show()
        self._splitter.addWidget(self._params_window)
        self._splitter.setCollapsible(0, True)

        frame = QtWidgets.QFrame(self)
        self._vtk_widget = QVTKRenderWindowInteractor(frame)

        self._vtk_widget.GetRenderWindow().AddRenderer(self._vtk_renderer)

        self._layout = QtWidgets.QVBoxLayout()
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.addWidget(self._vtk_widget)

        frame.setLayout(self._layout)
        frame.setSizePolicy(QtWidgets.QSizePolicy.Maximum,
                            QtWidgets.QSizePolicy.Expanding)

        self._splitter.addWidget(frame)
        self._splitter.setCollapsible(1, False)
        self._splitter.setStretchFactor(1, 10)

        self.setCentralWidget(self._splitter)

    def setupMenuBar(self):
        file_menu = self._menubar.addMenu("File")
        self._new_action = file_menu.addAction(
            "New", self.onNewFile, "Ctrl+N")
        self._open_action = file_menu.addAction(
            "Open", self.onOpenFile, "Ctrl+O")
        self._recent_menu = file_menu.addMenu("Open Recent")
        self.buildRecentFilesMenu()
        file_menu.addSeparator()
        self._close_action = file_menu.addAction(
            "Close", self.onClose, "Ctrl+W")
        file_menu.addSeparator()
        self._render_action = file_menu.addAction(
            "Render", self.onRender, "Ctrl+Shift+R")

    def setupToolBar(self):
        self._toolbar = QtWidgets.QToolBar()
        self._toolbar.setMovable(False)
        self._toolbar.setFloatable(False)
        self._toolbar.setFixedHeight(32)
        self._toolbar.setStyleSheet("""
            border: none;
            """)
        self._toolbar.addAction("O", self.onOpenFile)
        self._toolbar.addSeparator()
        self._toolbar.addAction("T", self.onAddText)

        self.addToolBar(QtCore.Qt.TopToolBarArea, self._toolbar)

    def updateWindowTitle(self):
        title = "Viz"
        if self._file_name is None:
            self.setWindowTitle(title)
        else:
            self.setWindowTitle("{} \u2014 {}".format(
                title, os.path.basename(self._file_name)))

    def _updateViewModeLocation(self):
        pass

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()

            file_names = []
            for url in event.mimeData().urls():
                file_names.append(url.toLocalFile())
            if len(file_names) > 0:
                self.plugin.loadFile(file_names[0])
        else:
            event.ignore()

    def closeEvent(self, event):
        self.plugin.settings.setValue(
            "splitter/state", self._splitter.saveState())
        super().closeEvent(event)

    def clear(self):
        # todo: remove actors and free them prop dialogs
        self._params_window.clear()

    def onUpdateWindow(self):
        self._vtk_render_window.Render()

    def loadFile(self, file_name):
        self._load_thread = LoadThread(file_name)
        if self._load_thread.getReader() is not None:
            self._progress = QtWidgets.QProgressDialog(
                "Loading {}...".format(os.path.basename(file_name)),
                None, 0, 0, self)
            self._progress.setWindowModality(QtCore.Qt.WindowModal)
            self._progress.setMinimumDuration(0)
            self._progress.show()

            self._load_thread.finished.connect(self.onFileLoadFinished)
            self._load_thread.start(QtCore.QThread.IdlePriority)
        else:
            self._load_thread = None
            QtWidgets.QMessageBox.critical(
                None,
                "Unsupported file format",
                "Selected file in not in a supported format.\n"
                "We support the following formats:\n"
                "  ExodusII")

    def onFileLoadFinished(self):
        reader = self._load_thread.getReader()

        file_name = reader.getFileName()
        file_props = FileProps(reader, self)
        self._params_window.addPipelineItem("File", file_props)
        file_props.show()

        actors = file_props.getVtkActor()
        if isinstance(actors, list):
            for act in actors:
                self._vtk_renderer.AddViewProp(act)

        self._progress.hide()
        self._progress = None

        self.addToRecentFiles(file_name)
        self._file_name = file_name
        self.updateWindowTitle()

    def onClose(self):
        self.close()

    def onNewFile(self):
        self.clear()

    def onOpenFile(self):
        file_name, f = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Open File',
            "",
            "ExodusII files (*.e *.exo)")
        if file_name:
            self.loadFile(file_name)

    def onRender(self):
        pass

    def onAddText(self):
        props = TextProps(self)
        self._params_window.addPipelineItem("Text", props)
        props.show()

        actor = props.getVtkActor()
        if actor is not None:
            self._vtk_renderer.AddViewProp(actor)

    def onAddFile(self):
        file_name, f = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Open File',
            "",
            "ExodusII files (*.e *.exo)")
        if file_name:
            self.loadFile(file_name)
