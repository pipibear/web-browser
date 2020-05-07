# -*- coding: utf-8 -*-
import sys, os

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox, QWidget, QFileDialog
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout,QTabWidget,QDesktopWidget,QHBoxLayout
from PyQt5.QtWidgets import QMessageBox,QSystemTrayIcon,QMenu,QAction,QFileDialog,QFontDialog
from PyQt5.QtGui import QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineDownloadItem
from PyQt5.QtWebChannel import QWebChannel

from lib.Window import Window
from lib.Util import Util
from lib.Printer import Printer
from lib.Icon import Icon
from Ui_setting import Ui_DlgSetting

class DlgSetting(QWidget, Ui_DlgSetting):
    mainWindow = None
    config = None
    lang = None

    def __init__(self, mainWindow=None):
        super(DlgSetting, self).__init__()
        self.setupUi(self)
        #self.setSizeGripEnabled(False)
        #self.setFixedSize()
        
        self.mainWindow = mainWindow
        self.config = Util.getConfig()

        #common
        cfg = self.config['Default']
        index = 0
        for k,v in cfg['styleList'].items():
            self.combo_theme.addItem(v)
            if k == cfg['style']:
                self.combo_theme.setCurrentIndex(index)
            index += 1

        self.chk_close_to_tray.setChecked(cfg['closeToTray'])
        self.chk_close_confirm.setChecked(cfg['closeConfirm'])

        #printer
        printer = Printer()
        cfg = self.config['Printer']

        #defaut
        index = 0
        for i in printer.getPrinterList():
            name = i.printerName()
            self.combo_printer_list.addItem(name)
            if cfg['defaultPrinter'] and name == cfg['defaultPrinter']:
                self.combo_printer_list.setCurrentIndex(index)
            elif not cfg['defaultPrinter'] and i.isDefault():
                self.combo_printer_list.setCurrentIndex(index)

            index += 1

        #page size & page margin
        self.txt_margin.setValue(cfg['margin'])
        self.chk_fullpage.setChecked(cfg['fullPage'])

        self.rdo_portrait.setChecked(not cfg['orientation'])
        self.rdo_landscape.setChecked(cfg['orientation'])

        self.txt_font.setText(cfg['font'])
        self.txt_savepath.setText(Util.getConfigValue('defaultSavePath'))
        
        self.translateUi()

    
    def getDefaultSetting(self):
        setting = {
            "closeConfirm":'true' if self.chk_close_confirm.isChecked() else 'false',
            "closeToTray":'true' if self.chk_close_to_tray.isChecked() else 'false',
            "defaultSavePath":self.txt_savepath.text(),
        }

        styleIndex = self.combo_theme.currentIndex()
        index = 0
        for k,_ in self.config['Default']['styleList'].items():
            if styleIndex == index:
                setting['style'] = k
            index += 1

        return setting 
    
    def getPrinterSetting(self):
        setting = {
            'defaultPrinter':self.combo_printer_list.currentText(),
            'fullPage':'true' if self.chk_fullpage.isChecked() else 'false',
            'orientation':1 if self.rdo_landscape.isChecked() else 0,
            'font':self.txt_font.text(),
            'margin':int(self.txt_margin.value()),
        }

        return setting 
    
    @pyqtSlot() 
    def on_btn_ok_clicked(self):
        #default
        default = self.getDefaultSetting()
        printer = self.getPrinterSetting()

        if not Util.saveConfig('Default', default):
            QMessageBox.critical(self, 'Message', Util.lang('save_config_error', 'Save config.ini file failure.'), QMessageBox.Ok, QMessageBox.Ok) 
            return

        if not Util.saveConfig('Printer', printer):
            QMessageBox.critical(self, 'Message', Util.lang('save_config_error', 'Save config.ini file failure.'), QMessageBox.Ok, QMessageBox.Ok) 
            return

        if self.mainWindow:
            self.mainWindow.on_settingOK()

        self.parentWidget().close()

    @pyqtSlot() 
    def on_btn_apply_clicked(self):
        #default
        default = self.getDefaultSetting()
        printer = self.getPrinterSetting()

        if not Util.saveConfig('Default', default):
            QMessageBox.critical(self, 'Message', Util.lang('save_config_error', 'Save config.ini file failure.'), QMessageBox.Ok, QMessageBox.Ok) 
            return

        if not Util.saveConfig('Printer', printer):
            QMessageBox.critical(self, 'Message', Util.lang('save_config_error', 'Save config.ini file failure.'), QMessageBox.Ok, QMessageBox.Ok) 
            return

        if self.mainWindow:
            self.mainWindow.on_settingOK()
        else:
            Util.reloadConfig()
            Util.loadTheme()

    @pyqtSlot() 
    def on_btn_cancel_clicked(self):
        self.parentWidget().close()

    @pyqtSlot() 
    def on_btn_browse_savepath_clicked(self):
        f =  QFileDialog.getExistingDirectory(self, "Select Directory", self.txt_savepath.text())
        if not f:
            return
        
        self.txt_savepath.setText(f)

    @pyqtSlot() 
    def on_btn_clear_clicked(self):
        self.txt_savepath.setText('')

    def formatSetting(self, setting):
        t = setting
        for (k, v) in t.items():
            if v in ['true','false']:
                t[k] = Util.strToBool(v)

        return t

    @pyqtSlot() 
    def on_btn_font_clicked(self):
        currentFont = QFont()
        currentFont.fromString(self.txt_font.text())

        dialog = QFontDialog(self)
        dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowStaysOnTopHint)
        dialog.setCurrentFont(currentFont)
        if dialog.exec_() == QFontDialog.Accepted:
            self.txt_font.setText(dialog.selectedFont().toString())

    @pyqtSlot() 
    def on_btn_test_clicked(self):
        '''
        printer = Printer()
        printer.printTest(self.formatSetting(self.getPrinterSetting()))
        '''

        self.showTestWindow()

    def showTestWindow(self):
        from main import WebView, WebWindow

        self.mainWnd = Window()
        self.mainWnd.setWindowTitle('Test')
        self.mainWnd.setWindowIcon(Icon.getLogoIcon())

        self.testWindow = WebWindow()
        self.testWindow.loadUrl(Util.getTestPage())

        self.mainWnd.setWidget(self.testWindow)
        #self.mainWnd.titleBar.buttonMinimum.hide()
        #self.mainWnd.titleBar.buttonMaximum.hide()
        self.mainWnd.titleBar.buttonMore.hide()
        self.mainWnd.titleBar.titleLabel.show()

        self.mainWnd.resizeCenter(670, 500)
        self.mainWnd.showPopupWindow()
                    

    def translateUi(self):
        self.tab_other.setTabText(0, Util.lang('common', 'Common'))
        self.tab_other.setTabText(1, Util.lang('printer', 'Printer'))
        self.tab_other.setTabText(2, Util.lang('others', 'Others'))

        self.group_theme.setTitle(Util.lang('theme', 'Theme'))
        self.group_ui.setTitle(Util.lang('ui', 'User interface'))
        self.group_printer.setTitle(Util.lang('default_printer', 'Default printer'))
        self.group_document.setTitle(Util.lang('document', 'Document'))
        self.group_other.setTitle(Util.lang('others', 'Others'))
        self.group_savepath.setTitle(Util.lang('save_path', 'Default file save directory'))


        self.rdo_portrait.setText(Util.lang('portrait', 'Portrait'))
        self.rdo_landscape.setText(Util.lang('landscape', 'Landscape'))


        self.chk_close_to_tray.setText(Util.lang('close_to_tray', 'Close to system tray'))
        self.chk_close_confirm.setText(Util.lang('close_confirm', 'Closing confirmation'))
        self.chk_fullpage.setText(Util.lang('fullpage', 'Fullpage printing'))


        self.lbl_font.setText(Util.lang('font', 'Font'))
        self.lbl_margin.setText(Util.lang('margin', 'Margin'))
        self.lbl_font.setText(Util.lang('font', 'Font'))

        self.btn_test.setText(Util.lang('test', 'Test'))
        self.btn_ok.setText(Util.lang('ok', 'OK'))
        self.btn_apply.setText(Util.lang('apply', 'Apply'))
        self.btn_cancel.setText(Util.lang('cancel', 'Cancel'))
        self.btn_font.setText(Util.lang('select', 'Select'))
        self.btn_browse_savepath.setText(Util.lang('select', 'Select'))
        self.btn_clear.setText(Util.lang('clear', 'Clear'))
        



#main
if __name__ == '__main__':
    app = QApplication(sys.argv)

    Util.loadTheme()

    settingWindow = DlgSetting()
    
    #testing
    #settingWindow.showTestWindow()
    #sys.exit(app.exec_())
    
    mainWnd = Window()
    mainWnd.setWindowTitle(Util.lang('setting', 'Setting'))
    mainWnd.setWindowIcon(Icon.getLogoIcon())
    mainWnd.center()
    mainWnd.setWidget(settingWindow)
    mainWnd.titleBar.buttonMinimum.hide()
    mainWnd.titleBar.buttonMaximum.hide()
    mainWnd.titleBar.buttonMore.hide()
    mainWnd.resizeCenter(500,420)
    mainWnd.show()
    
    sys.exit(app.exec_())

