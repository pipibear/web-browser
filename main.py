import sys,os,time,traceback,datetime, threading

from PyQt5.QtCore import Qt, QUrl, pyqtSignal, QThread
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout,QTabWidget,QDesktopWidget,QHBoxLayout
from PyQt5.QtWidgets import QSystemTrayIcon,QMenu,QAction,QFileDialog,QMessageBox,QSplashScreen,qApp,QAction
from PyQt5.QtGui import QPixmap,QKeySequence
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineDownloadItem
from PyQt5.QtWebChannel import QWebChannel

from lib.Window import Window
from lib.Loading import Loading
from lib.Icon import Icon
from lib.Util import Util
from lib.WebPage import WebPage
from lib.Printer import Printer
from lib.Updater import Updater
from lib.MessageBox import MessageBox
import main_rc

######################################
class WebWindow(QWidget):
    webview = None
    tabWidget = None
    def __init__(self, *args, **kwargs):
        super(WebWindow, self).__init__(*args, **kwargs)
        self.windowType = Util.getConfigValue('newWindowType')

        self.layout = QVBoxLayout(self, spacing=0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        #tab
        if self.windowType == 'tab':
            self.tabWidget = QTabWidget(self)
            self.tabWidget.setTabShape(QTabWidget.Triangular)
            self.tabWidget.setDocumentMode(True)
            self.tabWidget.setMovable(True)
            self.tabWidget.setTabsClosable(True)

            self.tabWidget.tabBar().hide()
            self.tabWidget.tabCloseRequested.connect(self.on_closeTab)
            self.layout.addWidget(self.tabWidget)

        self.setLayout(self.layout)
    

    def loadUrl(self, url):
        c = Util.getTicker()

        if self.windowType == 'tab':
            self.webview = WebView(self)
            self.webview.load(QUrl(url))
            
            #tab
            tab = QWidget()
            tab.index = c
            self.tabWidget.addTab(tab, Util.getTabTitle(Util.lang('loading', 'Loading...')))
            #self.tabWidget.setCurrentWidget(tab)
            layout = QHBoxLayout(tab)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.addWidget(self.webview)
        else:
            self.webview = WebView(self)
            self.webview.load(QUrl(url))
            self.layout.addWidget(self.webview)

        self.index = c

        self.spinner = Loading(self)
        self.spinner.start()

    def resizeCenter(self, w, h):
        self.resize(w, h)

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    
    def on_closeTab(self, index):
        if self.tabWidget.count()>1:
            self.tabWidget.removeTab(index)
        else:
            self.parentWidget().close()
        
        if self.tabWidget.count()>1:
            self.tabWidget.tabBar().show()
        else:
            self.tabWidget.tabBar().hide()



    def keyPressEvent(self, event):
        if event.key() == Qt.Key_A and QApplication.keyboardModifiers() == (Qt.ControlModifier | Qt.ShiftModifier):
            print('Ctrl+Shift+A')

            if Util.isWindows():
                from lib.Screenshot import capture
                capture()



######################################
class WebView(QWebEngineView):
    mainWindow = None
    windowType = 'tab'

    def __init__(self, mainWindow):
        super(WebView, self).__init__()

        self.mainWindow = mainWindow
        self.windowType = Util.getConfigValue('newWindowType')

        #mypage
        page = WebPage(self)
        self.setPage(page)

        #webchannel
        self.webPrinter = Printer(self, mainWindow)
        self.channel = QWebChannel()
        self.channel.registerObject('printer', self.webPrinter)
        self.page().setWebChannel(self.channel)

        #event
        self.loadStarted.connect(self.on_loadStarted)
        self.loadFinished.connect(self.on_loadFinished)
        self.urlChanged.connect(self.on_urlChanged)

        self.page().profile().setHttpUserAgent(Util.getUserAgent())
        self.page().profile().downloadRequested.connect(self.on_downloadRequested)
        self.page().printRequested.connect(self.webPrinter.on_printRequested)
        self.page().pdfPrintingFinished.connect(self.webPrinter.on_pdfPrintingFinished)
        self.page().windowCloseRequested.connect(self.webPrinter.on_windowCloseRequested)
        self.loadProgress.connect(self.on_loadProgress)

        #self.setZoomFactor(1)

        if Util.getConfigValue('closeByEscape'):
            esc_action = QAction(self)
            esc_action.setShortcut(QKeySequence(Qt.Key_Escape))
            self.addAction(esc_action)
            esc_action.triggered.connect(self.esc)
        
    def esc(self):
        #print('esc')
        if isinstance(self.mainWindow, WebWindow):
            self.mainWindow.parentWidget().on_moreMenu_exit()
        elif hasattr(self.mainWindow, 'tabWidget'):
            self.mainWindow.tabWidget.parent().on_closeTab(self.mainWindow.tabWidget.currentIndex())
        else:
            self.mainWindow.close()


    def on_loadProgress(self, progress):
        #print('on_loadProgress=>%d' % progress)
        pass

    #overide
    def createWindow(self, QWebEnginePage_WebWindowType):
        if self.windowType == 'window':
            #print('createWindow=>%d' % QWebEnginePage_WebWindowType)

            mainWnd = MainWindow(isMain=False)

            mainWnd.setWindowTitle(Util.getWindowTitle(Util.lang('loading', 'Loading...')))
            mainWnd.setWindowIcon(Icon.getLogoIcon())
            mainWnd.resizeCenter(Util.getConfigValue('width'), Util.getConfigValue('height'))

            #webview
            webview = WebView(mainWnd)
            webview.page().profile().setHttpUserAgent(Util.getUserAgent(True))

            mainWnd.setWidget(webview)
            mainWnd.webview = webview
            mainWnd.show()

            #loading
            mainWnd.spinner = Loading(mainWnd)
            mainWnd.spinner.start()

            mainWnd.index = Util.getTicker()

            return webview
        elif self.windowType == 'tab':
             #tab
            tab = QWidget()

            self.mainWindow.tabWidget.addTab(tab, Util.getTabTitle(Util.lang('loading', 'Loading...')))
            self.mainWindow.tabWidget.setCurrentWidget(tab)
            layout = QHBoxLayout(tab)
            layout.setContentsMargins(0, 0, 0, 0)

            #webview
            mainWnd = tab
            mainWnd.tabWidget = self.mainWindow.tabWidget

            #webview
            new_webview = WebView(mainWnd)
            new_webview.page().profile().setHttpUserAgent(Util.getUserAgent(True))

            layout.addWidget(new_webview)
            mainWnd.webview = new_webview
            mainWnd.show()

            mainWnd.spinner = self.mainWindow.spinner
            mainWnd.spinner.start()

            if mainWnd.tabWidget.count()>1:
                mainWnd.tabWidget.tabBar().show()

            mainWnd.index = Util.getTicker()

            return new_webview
        else:
            MessageBox.alert(Util.lang('invalid_window_type', 'Opening a new window is not supported.')) 

    def on_loadStarted(self):
        #print('sub started=>%d' % self.mainWindow.index)

        url = self.url().toString()
        if url.startswith('http'):
            self.currentUrl = url

        #print('url=>%s' % url)
        
    def on_loadFinished(self, finished):
        #print('sub finished=>%d,%r' % (self.mainWindow.index, finished))
        self.mainWindow.spinner.stop()

        if not finished:
            return

        title = Util.getWindowTitle(self.mainWindow.webview.title())
        if self.mainWindow.parentWidget():
            self.mainWindow.parentWidget().setWindowTitle(title)
        else:
            self.mainWindow.setWindowTitle(title)
        
        if self.windowType == 'tab':
            self.mainWindow.tabWidget.setTabText(Util.getTabIndex(self.mainWindow.tabWidget, self.mainWindow.index), Util.getTabTitle(self.mainWindow.webview.title()))
        
    def on_urlChanged(self, url):
        #print('on_urlChanged=>%s' % url)
        pass

    def on_downloadRequested(self, downloadItem):
        #download
        if  downloadItem.isFinished()==False and downloadItem.state()==0:
            #print('on_downloadRequested=>%d' % self.mainWindow.index)

            #filename
            #the_filename = downloadItem.url().fileName()
            the_filename = os.path.basename(downloadItem.path())
            
            if len(the_filename) == 0 or "." not in the_filename:
                cur_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                the_filename = cur_time + '.' + downloadItem.mimeType().split('/')[1]
            
            
            if Util.getConfigValue('defaultSavePath'):
                the_sourceFile = Util.getConfigValue('defaultSavePath') + '/' + Util.getRandomFileName(the_filename)
            else:
                f =  QFileDialog.getSaveFileName(None,"Save File", the_filename ,"All files(*.*)")
                if not f[0]:
                    downloadItem.cancel()
                    return False
                the_sourceFile = f[0]

            #the_sourceFile = os.path.join(os.getcwd(), the_filename)
            
            # downloadItem.setSavePageFormat(QWebEngineDownloadItem.CompleteHtmlSaveFormat)
            downloadItem.setPath(the_sourceFile)
            downloadItem.accept()
            downloadItem.finished.connect(self.on_downloadFinished)
            downloadItem.downloadProgress.connect(self.on_downloadProgress)

    def on_downloadProgress(self):
        self.mainWindow.spinner.start()

    def on_downloadFinished(self):
        self.mainWindow.spinner.stop()
        js_string = 'alert("%s")' % Util.lang('download_success', 'Download successfully.')
        self.mainWindow.webview.page().runJavaScript(js_string)


class MainWindow(Window):
    tray = None
    isMain = True
    updater = None

    def __init__(self, isMain=True, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.isMain = isMain
        self.showWindowTitle = Util.getConfigValue('showTitle')
        self.showWindowIcon = Util.getConfigValue('showWindowIcon')
        self.defaultStyle = Util.getConfigValue('style')
        self.closeConfirm = Util.getConfigValue('closeConfirm')
        self.closeToTray = Util.getConfigValue('closeToTray')
        
        if not self.isMain:
            self.titleBar.buttonMore.hide()
        if not self.showWindowIcon:
            self.titleBar.iconLabel.hide()
        if not self.showWindowTitle:
            self.titleBar.titleLabel.hide()

        self.titleBar.settionAction.triggered.disconnect()
        self.titleBar.settionAction.triggered.connect(self.on_moreMenu_setting)
        self.titleBar.exitAction.triggered.disconnect()
        self.titleBar.exitAction.triggered.connect(self.on_moreMenu_exit)
        self.titleBar.settingLabel.setText(Util.lang('setting', 'Setting'))
        self.titleBar.exitLabel.setText(Util.lang('exit', 'Exit'))

        #updater
        self.updater = Updater()
        self.updater.signal.connect(self.log)
        self.updater.init()

    def on_moreMenu_setting(self):
        from setting import DlgSetting
        
        self.settingDialog = DlgSetting(self)

        self.settingWindow = Window()
        self.settingWindow.setWindowTitle(Util.lang('setting', 'Setting'))
        self.settingWindow.setWindowIcon(Icon.getLogoIcon())
        self.settingWindow.setWidget(self.settingDialog)
        self.settingWindow.titleBar.buttonMinimum.hide()
        self.settingWindow.titleBar.buttonMaximum.hide()
        self.settingWindow.titleBar.buttonMore.hide()
        self.settingWindow.resizeCenter(500,420)
        self.settingWindow.showPopupWindow()

    def reloadConfig(self):
        Util.reloadConfig()
        self.showWindowTitle = Util.getConfigValue('showTitle')
        self.showWindowIcon = Util.getConfigValue('showWindowIcon')
        self.defaultStyle = Util.getConfigValue('style')
        self.closeConfirm = Util.getConfigValue('closeConfirm')
        self.closeToTray = Util.getConfigValue('closeToTray')
        Util.loadTheme()

    def on_settingOK(self):
        old_style = self.defaultStyle
        self.reloadConfig()

        if self.showWindowIcon:
            self.titleBar.iconLabel.show()
        else:
            self.titleBar.iconLabel.hide()

        if self.showWindowTitle:
            self.titleBar.titleLabel.show()
        else:
            self.titleBar.titleLabel.hide()


        #change theme
        new_style = Util.getConfigValue('style')
        if old_style != new_style:
            self._widget.webview.page().runJavaScript("changeBrowserTheme('%s')" % new_style)
        

    def on_moreMenu_exit(self):
        if self.closeConfirm and self.isMain:
            reply = MessageBox.question(self.parentWidget(), Util.lang('msg_title', 'Information'), Util.lang('exit_confirm', 'Are you sure to exit?'), QMessageBox.Yes | QMessageBox.No, QMessageBox.No) 
            if reply == QMessageBox.Yes: 
                self.exitAll()
        else:
            self.exitAll()

    def closeEvent(self, event):
        if self.closeToTray and self.isMain:
            self.hide()
            event.ignore()
        elif self.closeConfirm and self.isMain:
            reply = MessageBox.question(self.parentWidget(), Util.lang('msg_title', 'Information'), Util.lang('exit_confirm', 'Are you sure to exit?'), QMessageBox.Yes | QMessageBox.No, QMessageBox.No) 
            if reply == QMessageBox.Yes: 
                self.exitAll()
            else:
                event.ignore()
        elif self.isMain:
            self.exitAll()
        else:
            event.accept()

    def addSystemTray(self):
        self.tray = QSystemTrayIcon() 

        self.icon = Icon.getLogoIcon()
        self.tray.setIcon(self.icon) 

        self.tray.activated.connect(self.clickTray) 
        #self.tray.messageClicked.connect(self.clickTray)

        self.tray_menu = QMenu(QApplication.desktop()) 
        self.ShowAction = QAction(Util.lang('show_window', 'Window'), self, triggered=self.showWindow) 
        self.SettingAction = QAction(Util.lang('setting', 'Setting'), self, triggered=self.on_moreMenu_setting) 
        self.QuitAction = QAction(Util.lang('exit', 'Exit'), self, triggered=self.on_moreMenu_exit) 
        self.tray_menu.addAction(self.ShowAction) 
        self.tray_menu.addAction(self.SettingAction) 
        self.tray_menu.addAction(self.QuitAction)
        
        self.tray.setContextMenu(self.tray_menu)

        self.tray.show()

    def clickTray(self, reason):
        if reason != QSystemTrayIcon.DoubleClick:
            return False

        self.showWindow()

        
    def showWindow(self):
        if self.isMaximized():
            self.showMaximized()
        elif self.isFullScreen():
            self.showFullScreen()
        else:
            self.showNormal()
            
        self.activateWindow()

    def loadData(self, splash=None):
        self._widget.loadUrl(Util.getConfigValue('url'))

        if Util.isWindows():
            self.addSystemTray()

        #check upgrade
        mainScript = Util.getScriptName()
        t1 = threading.Thread(target=self.updater.checkUpgrade,args=(False,mainScript))
        t1.setDaemon(True)
        t1.start()

        #splash
        if splash:
            splash.showMessage("Loading... 100%", Qt.AlignHCenter | Qt.AlignBottom, Qt.white)
            qApp.processEvents()

    def log(self, o):
        if o['extra']:
            if o['extra'][0] == 'check-end' and o['extra'][1]['allowUpgrade']:
                reply = MessageBox.question(self.parentWidget(), Util.lang('msg_title', 'Information'), Util.lang('allow_upgrade', 'There is a newer version, do you want to download it?'), QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes) 
                if reply == QMessageBox.Yes: 
                    mainScript = Util.getScriptName()
                    self.updater.runScriptFile(self.updater.updaterFilePath, ' -s' + mainScript)
                    sys.exit()


    def exitAll(self):
        self.tray and self.tray.hide()
        sys.exit()

    def __del__(self):
        #print('close')
        self.tray and self.tray.hide()

###############################################
class Updater(Updater, QThread):
    signal = pyqtSignal(object)
    def __init__(self, parent=None):
        super(Updater, self).__init__(False)
        super(QThread, self).__init__()

    def log(self, str, extra=None):
        self.signal.emit({"str":str, "extra":extra})


#handle error
def saveError(v):
    #save
    s = '['+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + ']\n' + v + '\n'
    p = os.path.dirname(os.path.realpath(sys.argv[0])) + '/tmp/error.log'
    with open(p, "a+", encoding="utf-8") as f:
        f.write(s)
def errorHandler(type, value, trace):  
    v = 'Main Error: \n%s' % (''.join(traceback.format_exception(type, value, trace)))
    print(v)
    saveError(v)
    sys.__excepthook__(type, value, trace) 
sys.excepthook = errorHandler


#main function
if __name__ == '__main__':
    from PyQt5.QtNetwork import QLocalSocket, QLocalServer

    tmpPath = os.path.dirname(os.path.realpath(sys.argv[0])) + '/tmp'
    splashPath = os.path.dirname(os.path.realpath(sys.argv[0])) + '/misc/splash.png'
    if not os.path.exists(tmpPath):
        os.mkdir(tmpPath)

    #scale
    QApplication.setAttribute(Qt.AA_UseSoftwareOpenGL)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    #single instance
    #startupTime = Util.timestamp()
    if Util.getConfigValue('singleInstance'):
        try:
            socket = QLocalSocket()
            serverName = 'CristBrowser-Application'
            socket.connectToServer(serverName)
            if socket.waitForConnected(500):
                QMessageBox.critical(None, Util.lang('alert', 'Alert'), Util.lang('run_once', 'This program has been running, you can find it in the system tray.'), QMessageBox.Ok, QMessageBox.Ok)
                sys.exit()
            else:
                localServer = QLocalServer()
                localServer.listen(serverName)
        except Exception as e:
            QMessageBox.critical(None, Util.lang('alert', 'Alert'), e.__str__(), QMessageBox.Ok, QMessageBox.Ok)
            sys.exit()
    #print(Util.timestamp() - startupTime)


    #splash
    splash = None
    if Util.getConfigValue('showSplash') and os.path.exists(splashPath):
        splash = QSplashScreen(QPixmap(splashPath))
        splash.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint | Qt.Tool)
        splash.showMessage("Loading... 0%", Qt.AlignHCenter | Qt.AlignBottom, Qt.white)
        splash.show()
        qApp.processEvents()

    Util.loadTheme()

    #main
    Window.Margins = 5 if Util.getConfigValue('resizable') else 0
    Window.StayOnTop = Util.getConfigValue('windowStayOnTop')
    mainWnd = MainWindow()

    mainWnd.setWidget(WebWindow(mainWnd))
    mainWnd.loadData(splash)

    #ui
    mainWnd.setWindowTitle(Util.getWindowTitle(Util.lang('loading', 'Loading...')))
    mainWnd.setWindowIcon(Icon.getLogoIcon())
    if not Util.getConfigValue('showTitleBar'):
        mainWnd.titleBar.hide()
    
    mainWnd.resizeCenter(Util.getConfigValue('width'), Util.getConfigValue('height'))
    mainWnd.show_(Util.getConfigValue('fullscreen'))
    
    #MessageBox.alert(sys.argv[0])
    splash and splash.close()
    sys.exit(app.exec_())
