import sys
import offlineBilling
from pytestqt.plugin import QtBot
from pytestqt.qt_compat import qt_api
import PyQt5.QtCore as QtCore
from PyQt5.QtWidgets import QStackedWidget, QApplication

class Tests:
    def testLoginPageIncorrect(self,qtbot):
        app = QApplication(sys.argv)
        screen = app.primaryScreen()
        widgetStack = QStackedWidget()
        ogMainWindow = offlineBilling.OGMainWindow()
        mainWindow = offlineBilling.MainWindow()
        homePage = offlineBilling.HomePage()
        widgetStack.addWidget(ogMainWindow) 
        widgetStack.addWidget(mainWindow) 
        widgetStack.addWidget(homePage) 
        widgetStack.setCurrentIndex(1)
        widgetStack.showMaximized()
        qtbot.add_widget(widgetStack)
        #Test with no username and password
        qtbot.mouseClick(mainWindow.loginBtn, QtCore.Qt.LeftButton)
        #Test with username and password
        mainWindow.usernameText.setText('admin')
        qtbot.mouseClick(mainWindow.loginBtn, QtCore.Qt.LeftButton)
        
    def testLoginCorrect(self,qtbot):
        app = QApplication(sys.argv)
        screen = app.primaryScreen()
        widgetStack = QStackedWidget()
        ogMainWindow = offlineBilling.OGMainWindow()
        mainWindow = offlineBilling.MainWindow()
        homePage = offlineBilling.HomePage()
        widgetStack.addWidget(ogMainWindow) 
        widgetStack.addWidget(mainWindow) 
        widgetStack.addWidget(homePage) 
        widgetStack.setCurrentIndex(1)
        widgetStack.showMaximized()
        qtbot.add_widget(widgetStack)
        #Test with username and password
        mainWindow.usernameText.setText('admin')
        qtbot.mouseClick(mainWindow.loginBtn, QtCore.Qt.LeftButton)