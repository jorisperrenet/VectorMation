import sys
from PyQt5.QtCore import QFile, QSize, Qt, QEvent
from PyQt5.QtGui import QBrush, QColor, QImage, QPainter, QPixmap, QPen
from PyQt5.QtWidgets import (QActionGroup, QApplication, QFileDialog,
        QGraphicsItem, QGraphicsRectItem, QGraphicsScene, QGraphicsView,
        QMainWindow, QMenu, QMessageBox, QWidget, QProgressBar,
        QHBoxLayout, QMenuBar, QPushButton, QLabel)
from PyQt5.QtOpenGL import QGL, QGLFormat, QGLWidget
from PyQt5.QtSvg import QGraphicsSvgItem


class MainWindow(QMainWindow):
    def __init__(self, display, use_menubar=True):
        super(MainWindow, self).__init__()
        # Set the viewer and the placeholder for the path to the displayed svg
        self.view = SvgView(self, display)
        self.currentPath = ''

        # Add a default size for floating windows
        self.resize(800, 600)

        # Add mouse tracking
        self.setMouseTracking(True)

        if use_menubar:
            # Define the layout of the top bar
            self.layout = QHBoxLayout()
            self.layout.setContentsMargins(0, 0, 0, 0)

            ### Add the renderers to an option menu
            rendererMenu = QMenu("&Renderer", self)
            self.nativeAction = rendererMenu.addAction("&Native")
            self.nativeAction.setCheckable(True)
            self.nativeAction.setChecked(True)

            if QGLFormat.hasOpenGL():
                self.glAction = rendererMenu.addAction("&OpenGL")
                self.glAction.setCheckable(True)

            self.imageAction = rendererMenu.addAction("&Image")
            self.imageAction.setCheckable(True)

            if QGLFormat.hasOpenGL():
                rendererMenu.addSeparator()
                self.highQualityAntialiasingAction = rendererMenu.addAction("&High Quality Antialiasing")
                self.highQualityAntialiasingAction.setEnabled(False)
                self.highQualityAntialiasingAction.setCheckable(True)
                self.highQualityAntialiasingAction.setChecked(False)
                self.highQualityAntialiasingAction.toggled.connect(self.view.setHighQualityAntialiasing)

            rendererGroup = QActionGroup(self)
            rendererGroup.addAction(self.nativeAction)

            if QGLFormat.hasOpenGL():
                rendererGroup.addAction(self.glAction)

            rendererGroup.addAction(self.imageAction)
            rendererGroup.triggered.connect(self.setRenderer)

            # Add renderer options to menubar
            self.menu_bar = QMenuBar()
            self.menu_bar.addMenu(rendererMenu)

            # Add start and stop buttons for the animation
            start_button = QPushButton('&Restart')
            start_button.clicked.connect(self.start_anim)
            stop_button = QPushButton('&Stop')
            stop_button.clicked.connect(self.stop_anim)

            # Add a progress bar for displaying the frame count
            self.progress_label = QLabel('Frame:')
            self.progress = QProgressBar(self)
            self.progress.setMaximumWidth(2000)
            # self.progress.setRange(0, 100)
            # self.progress.setValue(0)
            self.progress.setFormat(f'{0}/??')

            # Add x and y positions of mouse
            self.xpos = QLabel(f'x=?')
            self.ypos = QLabel(f'y=?')

            # Add the widgets to the layout
            self.menu_bar.setMaximumSize(rendererMenu.size())
            self.layout.addWidget(self.menu_bar)
            self.layout.addStretch()
            self.layout.addWidget(self.progress_label)
            self.layout.addWidget(self.progress)
            self.layout.addStretch()
            self.layout.addWidget(self.xpos)
            self.layout.addWidget(self.ypos)
            self.layout.addWidget(start_button)
            self.layout.addWidget(stop_button)
            # Add layout to a bar
            widget = QWidget(self)
            self.setMenuWidget(widget)
            widget.setLayout(self.layout)

        # Make the SvgView widget the displayed widget
        self.setCentralWidget(self.view)
        self.setWindowTitle("SVG Viewer")

    def start_anim(self):
        """Restart the animation"""
        canvas = self.view.display
        canvas.time = canvas.start_anim
        canvas.frame_count = 0
        return True

    def stop_anim(self):
        """Stop animating..."""
        self.view.display.animate = 1 - self.view.display.animate
        return True

    def openFile(self, path=None):
        """Opens and checks the svg file's existence"""
        if path:
            svg_file = QFile(path)
            if not svg_file.exists():
                QMessageBox.critical(self, "Open SVG File",
                        "Could not open file '%s'." % path)
                return

            self.view.openFile(svg_file)

            if not path.startswith(':/'):
                self.currentPath = path
                self.setWindowTitle("%s - SVGViewer" % self.currentPath)

    def setRenderer(self, action):
        """Change the renderer"""
        if QGLFormat.hasOpenGL():
            self.highQualityAntialiasingAction.setEnabled(False)

        if action == self.nativeAction:
            self.view.setRenderer(SvgView.Native)
        elif action == self.glAction:
            if QGLFormat.hasOpenGL():
                self.highQualityAntialiasingAction.setEnabled(True)
                self.view.setRenderer(SvgView.OpenGL)
        elif action == self.imageAction:
            self.view.setRenderer(SvgView.Image)

    def closeEvent(self, event):
        print('Detecting a window-kill, closing...')
        sys.exit()

    """Sent all info to the animation"""
    def eventFilter(self, qobject, qevent):
        return self.view.eventFilter(event)

    def resizeEvent(self, event):
        self.view.resizeEvent(event)

    def keyPressEvent(self, event):
        self.view.keyPressEvent(event)

    def mousePressEvent(self, event):
        self.view.mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self.view.mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        self.view.mouseMoveEvent(event)


class SvgView(QGraphicsView):
    Native, OpenGL, Image = range(3)

    def __init__(self, mainwindow, display, parent=None):
        super(SvgView, self).__init__(parent)

        self.display = display
        self.renderer = SvgView.Native
        self.svgItem = None
        self.windowBorder = None
        self.mainwindow = mainwindow
        self.image = QImage()

        # Add mouse tracking
        self.setMouseTracking(True)

        # Disable scrolling bars
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setScene(QGraphicsScene(self))

        # Prepare background check-board pattern.
        tilePixmap = QPixmap(64, 64)
        tilePixmap.fill(Qt.white)
        tilePainter = QPainter(tilePixmap)
        color = QColor(220, 220, 220)
        tilePainter.fillRect(0, 0, 32, 32, color)
        tilePainter.fillRect(32, 32, 32, 32, color)
        tilePainter.end()

        self.setBackgroundBrush(QBrush(tilePixmap))
        # self.setBackgroundBrush(QBrush(Qt.black))


    def openFile(self, svg_file):
        """Draws the contents of an svg file"""
        if not svg_file.exists():
            return

        s = self.scene()
        s.clear()
        self.resetTransform()

        # Draw the svgviewer
        self.svgItem = QGraphicsSvgItem(svg_file.fileName())
        self.svgItem.setFlags(QGraphicsItem.ItemClipsToShape)
        self.svgItem.setCacheMode(QGraphicsItem.NoCache)
        self.svgItem.setZValue(0)

        # Get the svgviewer's bounding rectangle (adjusted for the width of the windowBorder)
        sw = 2
        bounding = self.svgItem.boundingRect()
        self.windowBorder = QGraphicsRectItem(bounding)

        # Draw a dashed border around the viewer
        outline = QPen(Qt.blue, sw)
        self.windowBorder.setPen(outline)
        self.windowBorder.setBrush(QBrush(Qt.NoBrush))
        self.windowBorder.setZValue(1)

        s.addItem(self.svgItem)
        s.addItem(self.windowBorder)

        # Resize the window to fit the drawings
        self.resizeEvent(0)


    def setRenderer(self, renderer):
        """Change the renderer"""
        self.renderer = renderer

        if self.renderer == SvgView.OpenGL:
            if QGLFormat.hasOpenGL():
                self.setViewport(QGLWidget(QGLFormat(QGL.SampleBuffers)))
        else:
            self.setViewport(QWidget())

    def setHighQualityAntialiasing(self, highQualityAntialiasing):
        if QGLFormat.hasOpenGL():
            self.setRenderHint(QPainter.HighQualityAntialiasing,
                    highQualityAntialiasing)


    def paintEvent(self, event):
        """Redraws the canvas"""
        if self.renderer == SvgView.Image:
            if self.image.size() != self.viewport().size():
                self.image = QImage(self.viewport().size(),
                        QImage.Format_ARGB32_Premultiplied)

            imagePainter = QPainter(self.image)
            QGraphicsView.render(self, imagePainter)
            imagePainter.end()

            p = QPainter(self.viewport())
            p.drawImage(0, 0, self.image)
        else:
            super(SvgView, self).paintEvent(event)

    """Sent all noteworthy events to the display"""
    def eventFilter(self, _, qevent):
        qtype = qevent.type()

        if qtype in [QEvent.Timer, QEvent.Paint]:
            # Nothing important happens
            qevent.accept()
            return True
        else:
            # Sent the event
            self.display.event(qevent)
        qevent.accept()
        return True

    def keyPressEvent(self, event):
        self.display.event(event)

    def mousePressEvent(self, event):
        self.display.event(event)

    def mouseReleaseEvent(self, event):
        self.display.event(event)

    def mouseMoveEvent(self, event):
        self.display.event(event)

    def resizeEvent(self, _):
        """Rescale the window to fit the svg-viewer"""
        if self.svgItem != None:
            w, h = self.width()+4, self.height()+4
            bounding = self.svgItem.boundingRect()
            svgw, svgh = bounding.width(), bounding.height()
            sc = min((w/svgw, 'w'), (h/svgh, 'h'))

            self.svgItem.setScale(sc[0])
            self.windowBorder.setScale(sc[0])
            if sc[1] == 'h':
                self.svgItem.setPos((w-sc[0]*svgw)//2, 0)
                self.windowBorder.setPos((w-sc[0]*svgw)//2, 0)
            else:
                self.svgItem.setPos(0, (h-sc[0]*svgh)//2)
                self.windowBorder.setPos(0, (h-sc[0]*svgh)//2)
            self.scene().setSceneRect(0, 0, w, h)


class SVGViewer:
    """A simple Qt-powered SVGViewer that can open files untill destruction"""
    def __init__(self, display):
        self.app = QApplication(sys.argv)

        self.window = MainWindow(display)
        self.window.show()

    def view(self, filename, wait_till=None):
        self.window.openFile(filename)
        if wait_till is not None:
            from PyQt5 import QtTest
            import datetime
            to_wait = wait_till - datetime.datetime.now()
            secs = to_wait.total_seconds()
            QtTest.QTest.qWait(int(secs*1000))

    def destroy(self):
        # sys.exit(self.app.exec_())
        sys.exit(self.app.exec())
