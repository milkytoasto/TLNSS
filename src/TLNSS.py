import sys
import os
import shutil
import configparser

from PyQt5.QtWidgets import *
from PyQt5.Qt import *
from PyQt5.QtGui import *


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller
    https://stackoverflow.com/questions/31836104/pyinstaller-and-onefile-how-to-include-an-image-in-the-exe-file
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


config = configparser.ConfigParser()
config.read('TLNSS.config.ini')


class TreeView(QTreeView):
    """
    TreeView class that disables the default event of double
    clicks.
    """

    def edit(self, index, trigger, event):
        if trigger == QAbstractItemView.DoubleClicked:
            return False
        return QTreeView.edit(self, index, trigger, event)


class NoIconProvider(QFileIconProvider):
    """
    File Icon Provider for the purpose of removing folder/file 
    icons from a tree view.
    """

    def icon(self, _):
        return QIcon()


class TLNSS(QWidget):
    """
    Main class for the Touhou Luna Nights Save Switcher GUI
    """

    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        logo, folderClosed, folderExpanded = resource_path('./icons/logo.png').replace("\\", "/"), resource_path(
            './icons/folder-closed.png').replace("\\", "/"), resource_path('./icons/folder-expanded.png').replace("\\", "/")
        self.setWindowIcon(QIcon(logo))

        styleSheet = '''QGroupBox
                            {
                                font-size: 12px;
                                font-weight: bold;
                            }

                            QTreeView {
                                show-decoration-selected: 1;
                            }

                            QTreeView::item:hover {
                                background: none;
                                border: none;
                            }

                            QTreeView::item:selected {
                                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6ea1f1, stop: 1 #567dbc);
                                color: white;
                            }

                            QTreeView::item:selected:active{
                                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6ea1f1, stop: 1 #567dbc);
                                color: white;
                            }

                            QTreeView::branch:has-children:!has-siblings:closed,
                            QTreeView::branch:closed:has-children:has-siblings,
                            QTreeView::branch:closed:adjoins-item:has-children {
                                    border-image: none;
                                    image: url(folderClosed);
                            }

                            QTreeView::branch:open:has-children:!has-siblings,
                            QTreeView::branch:open:has-children:has-siblings,
                            QTreeView::branch:open:adjoins-item,
                            QTreeView:branch:open  {
                                    border-image: none;
                                    image: url(folderExpanded);
                            }
                            '''
        styleSheet = styleSheet.replace('folderClosed', folderClosed)
        styleSheet = styleSheet.replace('folderExpanded', folderExpanded)
        self.setStyleSheet(styleSheet)
        self.setWindowTitle('Touhou Luna Nights Save Switcher')
        self.setFixedSize(480, 360)
        self.model = QFileSystemModel()
        self.treeView, self.treeModel = self.makeTree()

        vbox = QVBoxLayout()
        tophbox = QHBoxLayout()
        centralhbox = QHBoxLayout()
        bottomhbox = QHBoxLayout()

        tophbox.addWidget(self.makeDirectoryControls())
        centralhbox.addWidget(self.treeView)
        centralhbox.addLayout(self.makeSaveControls())
        bottomhbox.addWidget(self.makeEditControls())

        vbox.addLayout(tophbox)
        vbox.addLayout(centralhbox)
        vbox.addLayout(bottomhbox)

        self.setLayout(vbox)

    def makeTree(self):
        """
        Creates the file system view for the save switcher.
        """

        treeModel = QFileSystemModel()
        treeModel.setRootPath(config['DEFAULT']['SAVE_DIRECTORY'])
        treeModel.setReadOnly(False)
        treeModel.setIconProvider(NoIconProvider())

        treeView = TreeView()
        treeView.setModel(treeModel)

        treeView.setDragEnabled(True)
        treeView.setAcceptDrops(True)
        treeView.setDropIndicatorShown(True)
        treeView.setDragDropMode(QAbstractItemView.InternalMove)

        treeView.setRootIndex(treeModel.index(
            config['DEFAULT']['SAVE_DIRECTORY']))
        treeView.installEventFilter(self)

        treeView.header().setVisible(False)
        for i in range(1, treeView.header().length()):
            treeView.hideColumn(i)

        return treeView, treeModel

    def makeDirectoryControls(self):
        """
        Creates the controls for managing directory locations.
        """

        controlsGroup = QGroupBox()
        controls = QVBoxLayout()
        subcontrols1 = QHBoxLayout()
        subcontrols2 = QHBoxLayout()

        savesTextbox = QLineEdit(self)
        gameTextbox = QLineEdit(self)
        button = QPushButton('Saves Folder')
        button2 = QPushButton('Game Folder')

        savesTextbox.setText(os.path.abspath(
            config['DEFAULT']['SAVE_DIRECTORY']))
        gameTextbox.setText(os.path.abspath(
            config['DEFAULT']['GAME_DIRECTORY']))

        savesTextbox.setReadOnly(True)
        gameTextbox.setReadOnly(True)

        button.clicked.connect(lambda: self.select_saves_directory())
        button2.clicked.connect(lambda: self.select_game_directory())

        self.savesTextbox = savesTextbox
        self.gameTextbox = gameTextbox

        subcontrols1.addWidget(self.savesTextbox)
        subcontrols2.addWidget(self.gameTextbox)
        subcontrols1.addWidget(button)
        subcontrols2.addWidget(button2)

        controls.addLayout(subcontrols1)
        controls.addLayout(subcontrols2)
        controlsGroup.setLayout(controls)

        return controlsGroup

    def makeEditControls(self):
        """
        Creates the controls for button controls on the bottom toolbar.
        Controls include create folder, rename item, and delete item.
        """

        controlsGroup = QGroupBox()
        controls = QHBoxLayout()
        button = QPushButton('Create Folder')
        button2 = QPushButton('Rename Item')
        button3 = QPushButton('Delete Item')

        button.clicked.connect(lambda: self.create_folder())
        button2.clicked.connect(lambda: self.change_name(None))
        button3.clicked.connect(lambda: self.delete_directory(None))

        controls.addWidget(button)
        controls.addWidget(button2)
        controls.addWidget(button3)
        controlsGroup.setLayout(controls)
        return controlsGroup

    def makeSaveControls(self):
        """
        Creates the controls save export/importing.
        See makeSwapControls and makeImportControls
        """

        controls = QVBoxLayout()
        controls.setAlignment(Qt.AlignTop)
        controls.addWidget(self.makeSwapControls())
        controls.addWidget(self.makeImportControls())
        return controls

    def makeSwapControls(self):
        """
        Creates the controls save exporting.
        """

        controlsGroup = QGroupBox()
        controls = QVBoxLayout()
        controls.setAlignment(Qt.AlignHCenter)

        controlsGroup.setTitle('Export Save to:')
        game1 = QPushButton('Data 1')
        game2 = QPushButton('Data 2')
        game3 = QPushButton('Data 3')

        game1.clicked.connect(lambda: self.switch_save(0))
        game2.clicked.connect(lambda: self.switch_save(1))
        game3.clicked.connect(lambda: self.switch_save(2))

        controls.addWidget(game1)
        controls.addWidget(game2)
        controls.addWidget(game3)
        controlsGroup.setLayout(controls)
        return controlsGroup

    def makeImportControls(self):
        """
        Creates the controls save importing.
        """

        controlsGroup = QGroupBox()
        controls = QVBoxLayout()
        controls.setAlignment(Qt.AlignHCenter)

        controlsGroup.setTitle('Import Save from:')
        game1 = QPushButton('Data 1')
        game2 = QPushButton('Data 2')
        game3 = QPushButton('Data 3')

        game1.clicked.connect(lambda: self.import_save(0))
        game2.clicked.connect(lambda: self.import_save(1))
        game3.clicked.connect(lambda: self.import_save(2))

        controls.addWidget(game1)
        controls.addWidget(game2)
        controls.addWidget(game3)
        controlsGroup.setLayout(controls)
        return controlsGroup

    def eventFilter(self, source, event):
        """
        Event filter used for handling events.
        """

        if event.type() == QEvent.ContextMenu and source is self.treeView:
            """
            Handles options for the right-click context menu in the treeView.
            """

            gp = event.globalPos()
            lp = self.treeView.viewport().mapFromGlobal(gp)
            index = self.treeView.indexAt(lp)

            if not index.isValid():
                menu = QMenu()
                createFolderAction = menu.addAction("Create Folder")
                createFolderAction.triggered.connect(
                    lambda: self.create_folder())
                menu.exec_(gp)
                self.treeView.update()
                return True

            menu = QMenu()
            renameAction = menu.addAction("Rename")
            deleteAction = menu.addAction("Delete")
            renameAction.triggered.connect(lambda: self.change_name(index))
            deleteAction.triggered.connect(
                lambda: self.delete_directory(index))
            menu.exec_(gp)
            return True
        return True

    def getSelectedItem(self):
        """
        Helper function that returns the select index in the treeView.
        """
        indices = self.treeView.selectedIndexes()
        if not indices:
            return
        return indices[0]

    def create_folder(self):
        """
        Helper function to create a folder, prompting the user to enter a name.
        """

        name, _ = QInputDialog.getText(
            self, "Rename", "Enter a new name", QLineEdit.Normal)
        d = os.path.join(config['DEFAULT']['SAVE_DIRECTORY'], name)
        if not os.path.exists(d):
            os.mkdir(d)
        index = self.treeModel.index(d)
        QTimer.singleShot(
            0, lambda ix=index: self.treeView.setCurrentIndex(index))
        self.treeView.selectionModel().clearSelection()

    def delete_directory(self, index):
        """
        Helper function to delete a folder or directory, providing
        different dialog confirmations depending on which.
        """

        if index is None:
            index = self.getSelectedItem()
        if index is None or not index.isValid():
            return
        model = index.model()
        qm = QMessageBox

        if os.path.isdir(model.filePath(index)):
            ret = qm.question(
                self, '', "This will permanently delete all of your files in this directory, are you sure you want to do this?", qm.Yes | qm.No)
            if ret == qm.Yes:
                QDir(model.filePath(index)).removeRecursively()
                return True
            else:
                return False
        else:
            ret = qm.question(
                self, '', "Are you sure you want to permanently delete this file?", qm.Yes | qm.No)
            if ret == qm.Yes:
                QDir().remove(model.filePath(index))
                return True
            else:
                return False

    def change_name(self, index):
        """
        Helper function to rename an item, prompting the user to enter a new name.
        """

        if not index:
            index = self.getSelectedItem()
        if index is None or not index.isValid():
            return
        model = index.model()
        old_name = model.fileName(index)
        name, ok = QInputDialog.getText(
            self, "Rename", "Enter a new name", QLineEdit.Normal, old_name)
        if ok and name and name != old_name:
            model.setData(index, name)
        model.dataChanged
        self.treeView.selectionModel().clearSelection()

    def select_saves_directory(self):
        """
        Helper function for changing the saves directory.
        """

        file = str(QFileDialog.getExistingDirectory(
            self, "Select Saves Directory"))
        if not file:
            return
        config.set("DEFAULT", "SAVE_DIRECTORY", str(file))
        with open(resource_path('TLNSS.config.ini'), 'w') as configfile:
            config.write(configfile)
        self.treeModel.setRootPath(file)
        self.treeView.setRootIndex(self.treeModel.index(file))
        self.treeView.setCurrentIndex(self.treeModel.index(file))
        self.savesTextbox.setText(file)

    def select_game_directory(self):
        """
        Helper function for changing the game directory.
        """

        file = str(QFileDialog.getExistingDirectory(
            self, "Select Saves Directory"))
        if not file:
            return
        config.set("DEFAULT", "GAME_DIRECTORY", str(file))
        with open(resource_path('TLNSS.config.ini'), 'w') as configfile:
            config.write(configfile)
        self.gameTextbox.setText(file)

    def switch_save(self, save_slot):
        """
        Helper function for exporting the selected save file into the game
        directory as the provided save slot (int from 0-2).
        """

        index = self.getSelectedItem()
        if index is not None:
            save_file = self.treeModel.filePath(index)
            d = os.path.join(
                config['DEFAULT']['GAME_DIRECTORY'], 'game{}.sav'.format(save_slot))
            shutil.copyfile(save_file, d)
            QTimer.singleShot(
                0, lambda ix=index: self.treeView.setCurrentIndex(index))

    def import_save(self, save_slot):
        """
        Helper function for importing save files into the save directory.
        """

        save_file = os.path.join(
            config['DEFAULT']['GAME_DIRECTORY'], 'game{}.sav'.format(save_slot))
        if os.path.isfile(save_file):
            d = os.path.join(
                config['DEFAULT']['SAVE_DIRECTORY'], 'game{}.sav'.format(save_slot))
            shutil.copyfile(save_file, d)
            index = self.treeModel.index(d)
            QTimer.singleShot(
                0, lambda ix=index: self.treeView.setCurrentIndex(index))


def getPalette():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    return palette


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    palette = getPalette()
    app.setPalette(palette)
    t = TLNSS()
    t.show()
    sys.exit(app.exec_())
