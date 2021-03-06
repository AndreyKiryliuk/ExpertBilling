#-*-coding=utf-8*-
#global connection
import sys
from PyQt4 import QtCore, QtGui

#import socket
#socket.setdefaulttimeout(None)
from helpers import Object as Object
from helpers import connlogin
import Pyro.core
import Pyro.util
import Pyro.protocol
import Pyro.constants
import Pyro.errors
import Pyro.configuration
import threading
import Pyro


#Pyro.config.PYRO_BROKEN_MSGWAITALL = 1
import isdlogger
#logger = isdlogger.pyrologger('logging', loglevel=0, ident='mdi', filename='log/mdi_log')
#Pyro.util.Log = logger
#Pyro.core.Log = logger
#Pyro.protocol.Log = logger
import mdi_rc

from AccountFrame import AccountsMdiEbs as AccountsMdiChild
from NasFrame import NasEbs
from SettlementPeriodFrame import SettlementPeriodEbs as SettlementPeriodChild
from TimePeriodFrame import TimePeriodChildEbs as TimePeriodChild
from ClassFrame import ClassChildEbs as ClassChild
from MonitorFrame import MonitorEbs as MonitorFrame
from PoolFrame import PoolEbs as PoolFrame
#from SystemUser import SystemUserChild
from SystemUser import SystemEbs
from CustomForms import ConnectDialog, ConnectionWaiting, OperatorDialog
from Reports import NetFlowReportEbs as NetFlowReport, StatReport , LogViewWindow
from CardsFrame import CardsChildEbs as CardsChild
from DealerFrame import DealerMdiEbs as DealerMdiChild
from CustomForms import TemplatesWindow, SqlDialog
from TPChangeRules import TPRulesEbs
from AddonServiceFrame import AddonServiceEbs


_reportsdict = [['Статистика по группам',[['report3_users.xml', ['groups'], 'Общий трафик']]],\
                ['Глобальная статистика',[['report3_users.xml', ['gstat_globals'], 'Общий трафик'],['report3_users.xml', ['gstat_multi'], 'Трафик с выбором классов'], ['report3_pie.xml', ['pie_gmulti'], 'Пирог']]],\
                ['Другие отчёты',[['report3_sess.xml', ['sessions'], 'Сессии пользователей'], ['report3_tr.xml', ['trans_crd'], 'Динамика прибыли']]]]

#разделитель для дат по умолчанию
dateDelim = "."


outQueue = []
inQueue  = []
outQLock = threading.Lock()
inQLock  = threading.Lock()

class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        self.workspace = QtGui.QWorkspace()

        self.setCentralWidget(self.workspace)

        self.connect(self.workspace, QtCore.SIGNAL("windowActivated(QWidget *)"), self.updateMenus)
        self.windowMapper = QtCore.QSignalMapper(self)
        self.connect(self.windowMapper, QtCore.SIGNAL("mapped(QWidget *)"),
                     self.workspace, QtCore.SLOT("setActiveWindow(QWidget *)"))

        self.createActions()
        self.createMenus()
        self.createToolBars()
        self.createStatusBar()
        self.updateMenus()

        self.readSettings()

        self.setWindowTitle(u"Expert Billing Client 0.2")

    def closeEvent(self, event):
        self.workspace.closeAllWindows()
        if self.activeMdiChild():
            event.ignore()
        else:
            self.writeSettings()
            event.accept()

    @connlogin
    def newFile(self):
        self.workspace.windowList()
        

        child =  AccountsMdiChild(connection=connection, parent=self)
        #child.setIcon( QPixmap("images/icon.ico") )        
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        #self.wsp.addSubWindow(child)        
        child.show()
    

    @connlogin
    def templates(self):
        self.workspace.windowList()  

        child =  TemplatesWindow(connection=connection)
        #child.setIcon( QPixmap("images/icon.ico") )        
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        #self.wsp.addSubWindow(child)
        
        child.show()
 

    @connlogin
    def pool(self):
        self.workspace.windowList()  

        child =  PoolFrame(connection=connection)
        #child.setIcon( QPixmap("images/icon.ico") )        
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        #self.wsp.addSubWindow(child)
        
        child.show()
               
    @connlogin
    def dealers(self):
        self.workspace.windowList()
        child =  DealerMdiChild(parent=self, connection=connection)
        #child.setIcon( QPixmap("images/icon.ico") )

        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)        
        child.show()        

    @connlogin
    def open(self):
        child = NasEbs(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return            
        self.workspace.addWindow(child)
        child.show()
        #return child

    @connlogin
    def save(self):
        child=SettlementPeriodChild(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return            
        self.workspace.addWindow(child)
        child.show()


    @connlogin
    def saveAs(self):

        child = SystemEbs(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return            
        self.workspace.addWindow(child)
        child.show()

    @connlogin
    def tpchangerules(self):
        child = TPRulesEbs(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return            
        self.workspace.addWindow(child)
        child.show()       
               
    
    @connlogin
    def cut(self):
        child=TimePeriodChild(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
            
        self.workspace.addWindow(child)
        child.show()

    @connlogin
    def copy(self):
        child=ClassChild(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
            
        self.workspace.addWindow(child)
        child.show()

    @connlogin
    def paste(self):
        child = MonitorFrame(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        child.show()

    @connlogin
    def addonservice(self):
        child = AddonServiceEbs(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        child.show()

    @connlogin
    def logview(self):
        child = LogViewWindow(connection=connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        child.show()

        
    @connlogin
    def about(self):
        QtGui.QMessageBox.about(self, u"О программе",
                                u"Expert Billing Client<br>Интерфейс конфигурирования.<br>Версия 0.2")

    @connlogin
    def aboutOperator(self):
        child = OperatorDialog(connection=connection)
        child.exec_()
        
    @connlogin
    def sqlDialog(self):
        child = SqlDialog(connection=connection)
        child.exec_()
        
    @connlogin
    def cardsFrame(self):
        child = CardsChild(connection = connection)
        for window in self.workspace.windowList():
            if child.objectName()==window.objectName():
                self.workspace.setActiveWindow(window)
                return
        self.workspace.addWindow(child)
        child.show()

    @connlogin
    def netflowReport(self):
        child = NetFlowReport(connection = connection)
        self.workspace.addWindow(child)
        child.show()
        
        

    def relogin(self):
        global connection
        connection = login()
        global mainwindow
        mainwindow.setWindowTitle("ExpertBilling administrator interface #%s - %s" % (username, server_ip)) 
        

    def updateMenus(self):
        hasMdiChild = (self.activeMdiChild() is not None)
        #self.saveAct.setEnabled(hasMdiChild)
        #self.saveAsAct.setEnabled(hasMdiChild)
        self.pasteAct.setEnabled(True)
        self.closeAct.setEnabled(hasMdiChild)
        self.closeAllAct.setEnabled(hasMdiChild)
        self.tileAct.setEnabled(hasMdiChild)
        self.cascadeAct.setEnabled(hasMdiChild)
        self.arrangeAct.setEnabled(hasMdiChild)
        self.nextAct.setEnabled(hasMdiChild)
        self.previousAct.setEnabled(hasMdiChild)
        self.separatorAct.setVisible(hasMdiChild)


    def updateWindowMenu(self):
        self.windowMenu.clear()
        self.windowMenu.addAction(self.closeAct)
        self.windowMenu.addAction(self.closeAllAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.tileAct)
        self.windowMenu.addAction(self.cascadeAct)
        self.windowMenu.addAction(self.arrangeAct)
        self.windowMenu.addSeparator()
        self.windowMenu.addAction(self.nextAct)
        self.windowMenu.addAction(self.previousAct)
        self.windowMenu.addAction(self.separatorAct)

        windows = self.workspace.windowList()
        self.separatorAct.setVisible(len(windows) != 0)

        i = 0

        for child in windows:
            i += 1
            action = self.windowMenu.addAction(child.windowTitle())
            action.setCheckable(True)
            action.setChecked(child == self.activeMdiChild())
            self.connect(action, QtCore.SIGNAL("triggered()"),
                         self.windowMapper, QtCore.SLOT("map()"))
            self.windowMapper.setMapping(action, child)


       
    def createActions(self):
        self.newAct = QtGui.QAction(QtGui.QIcon("images/accounts.png"),
                                    u"&Пользователи и тарифы", self)
        #self.newAct.setShortcut(self.tr("Ctrl+A"))
        self.newAct.setStatusTip(u"Пользователи и тарифы")
        self.connect(self.newAct, QtCore.SIGNAL("triggered()"), self.newFile)

        self.dealerAct = QtGui.QAction(QtGui.QIcon("images/add.png"),
                                    u"&Дилеры", self)
        #self.dealerAct.setShortcut(self.tr("Ctrl+D"))
        self.dealerAct.setStatusTip(u"Дилеры")
        self.connect(self.dealerAct, QtCore.SIGNAL("triggered()"), self.dealers)
        self.openAct = QtGui.QAction(QtGui.QIcon("images/nas.png"), u"&Серверы доступа", self)
        
        #self.openAct.setShortcut(self.tr("Ctrl+N"))
        self.openAct.setStatusTip(u'Серверы доступа')
        self.connect(self.openAct, QtCore.SIGNAL("triggered()"), self.open)

        self.saveAct = QtGui.QAction(QtGui.QIcon("images/sp.png"), u'Расчётные периоды', self)
        #self.saveAct.setShortcut(self.tr("Ctrl+S"))
        self.saveAct.setStatusTip(u"Расчётные периоды")
        self.connect(self.saveAct, QtCore.SIGNAL("triggered()"), self.save)

        self.saveAsAct = QtGui.QAction(QtGui.QIcon("images/system_administrators.png"),u'Администраторы', self)
        self.saveAsAct.setStatusTip(u"Системные администраторы")
        self.connect(self.saveAsAct, QtCore.SIGNAL("triggered()"), self.saveAs)

        self.poolAct = QtGui.QAction(u'IP пулы', self)
        self.poolAct.setStatusTip(u"Системные администраторы")
        self.connect(self.poolAct, QtCore.SIGNAL("triggered()"), self.pool)


        self.exitAct = QtGui.QAction(u"Выход", self)
        self.exitAct.setShortcut(self.tr("Ctrl+Q"))
        self.exitAct.setStatusTip(u"Выход из программы")
        self.connect(self.exitAct, QtCore.SIGNAL("triggered()"), self.close)
        
        
        self.cutAct = QtGui.QAction(QtGui.QIcon("images/tp.png"),
                                    u'Периоды тарификации', self)

        self.cutAct.setStatusTip(u"Периоды тарификации")
        self.connect(self.cutAct, QtCore.SIGNAL("triggered()"), self.cut)


        self.sqlDialogAct = QtGui.QAction(QtGui.QIcon("images/sql.png"),u'SQL Консоль', self)

        self.sqlDialogAct.setShortcut(self.tr("Ctrl+Y"))
        self.connect(self.sqlDialogAct, QtCore.SIGNAL("triggered()"), self.sqlDialog)


        self.copyAct = QtGui.QAction(QtGui.QIcon("images/tc.png"),
                                     u"Классы трафика", self)
        #self.copyAct.setShortcut(self.tr("Ctrl+C"))
        self.copyAct.setStatusTip(u"Классы трафика")
        self.connect(self.copyAct, QtCore.SIGNAL("triggered()"), self.copy)

        self.pasteAct = QtGui.QAction(QtGui.QIcon("images/monitor.png"),
                                      u"Монитор сессий", self)
        
        #self.pasteAct.setShortcut(self.tr("Ctrl+M"))
        self.pasteAct.setStatusTip(u"Монитор сессий")

        self.connect(self.pasteAct, QtCore.SIGNAL("triggered()"), self.paste)

        self.cardsAct = QtGui.QAction(QtGui.QIcon("images/cards.png"),
                                      u"Карты экспресс-оплаты", self)
        #self.reportPropertiesAct.setShortcut(self.tr("Ctrl+V"))
        self.cardsAct.setStatusTip(u"Карты экспресс-оплаты")

        self.connect(self.cardsAct, QtCore.SIGNAL("triggered()"), self.cardsFrame)

        self.netflowReportAct=QtGui.QAction(QtGui.QIcon("images/nfstat.png"), u"Сетевая статистика", self)

        self.netflowReportAct.setStatusTip(u"Сетевая статистика")

        self.connect(self.netflowReportAct, QtCore.SIGNAL("triggered()"), self.netflowReport)

        self.reloginAct = QtGui.QAction(QtGui.QIcon("images/refresh_connection.png"),self.tr("&Reconnect"), self)
        self.reloginAct.setStatusTip(self.tr("Reconnect"))
        self.connect(self.reloginAct, QtCore.SIGNAL("triggered()"), self.relogin)

        self.templatesAct = QtGui.QAction(QtGui.QIcon("images/templates.png"),u"Шаблоны документов", self)
        #self.reloginAct.setStatusTip(self.tr("Reconnect"))
        self.connect(self.templatesAct, QtCore.SIGNAL("triggered()"), self.templates)


        self.tpchangeAct = QtGui.QAction(QtGui.QIcon("images/tarif_change.png"),u"Правила смены ТП", self)
        #self.reloginAct.setStatusTip(self.tr("Reconnect"))
        self.connect(self.tpchangeAct, QtCore.SIGNAL("triggered()"), self.tpchangerules)

        self.addonserviceAct = QtGui.QAction(u"Подключаемые услуги", self)
        #self.reloginAct.setStatusTip(self.tr("Reconnect"))
        self.connect(self.addonserviceAct, QtCore.SIGNAL("triggered()"), self.addonservice)
 
        self.logViewAct = QtGui.QAction(QtGui.QIcon("images/logs.png"), u"Просмотр логов", self)
        #self.reloginAct.setStatusTip(self.tr("Reconnect"))
        self.connect(self.logViewAct, QtCore.SIGNAL("triggered()"), self.logview)       
        
        
        self.reportActs = []
        i = 0
        
        for branch in _reportsdict:
            j=0
            self.reportActs.append([branch[0],[]])
            for leaf in branch[1]:
                rAct = QtGui.QAction(self.trUtf8(leaf[2]), self)
                rAct.setStatusTip(u"Отчёт")
                rAct.setData(QtCore.QVariant('_'.join((str(i), str(j)))))
                self.connect(rAct, QtCore.SIGNAL("triggered()"), self.reportsMenu)
                self.reportActs[-1][1].append(rAct)
                j+=1
            i += 1

        self.closeAct = QtGui.QAction(self.tr("Cl&ose"), self)
        self.closeAct.setShortcut(self.tr("Ctrl+F4"))
        self.closeAct.setStatusTip(self.tr("Close the active window"))
        self.connect(self.closeAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.closeActiveWindow)

        self.closeAllAct = QtGui.QAction(self.tr("Close &All"), self)
        self.closeAllAct.setStatusTip(self.tr("Close all the windows"))
        self.connect(self.closeAllAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.closeAllWindows)

        self.tileAct = QtGui.QAction(self.tr("&Tile"), self)
        self.tileAct.setStatusTip(self.tr("Tile the windows"))
        self.connect(self.tileAct, QtCore.SIGNAL("triggered()"), self.workspace.tile)

        self.cascadeAct = QtGui.QAction(self.tr("&Cascade"), self)
        self.cascadeAct.setStatusTip(self.tr("Cascade the windows"))
        self.connect(self.cascadeAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.cascade)

        self.arrangeAct = QtGui.QAction(self.tr("Arrange &icons"), self)
        self.arrangeAct.setStatusTip(self.tr("Arrange the icons"))
        self.connect(self.arrangeAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.arrangeIcons)

        self.nextAct = QtGui.QAction(self.tr("Ne&xt"), self)
        self.nextAct.setShortcut(self.tr("Ctrl+F6"))
        self.nextAct.setStatusTip(self.tr("Move the focus to the next window"))
        self.connect(self.nextAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.activateNextWindow)

        self.previousAct = QtGui.QAction(self.tr("Pre&vious"), self)
        self.previousAct.setShortcut(self.tr("Ctrl+Shift+F6"))
        self.previousAct.setStatusTip(self.tr("Move the focus to the previous "
                                              "window"))
        self.connect(self.previousAct, QtCore.SIGNAL("triggered()"),
                     self.workspace.activatePreviousWindow)

        self.separatorAct = QtGui.QAction(self)
        self.separatorAct.setSeparator(True)

        self.aboutAct = QtGui.QAction(self.tr("&About"), self)
        self.aboutAct.setStatusTip(self.tr("Show the application's About box"))
        self.connect(self.aboutAct, QtCore.SIGNAL("triggered()"), self.about)
        
        self.aboutOperAct = QtGui.QAction(self.tr("About &Operator"), self)
        self.aboutOperAct.setStatusTip(self.tr("Show the operator info"))
        self.connect(self.aboutOperAct, QtCore.SIGNAL("triggered()"), self.aboutOperator)

        self.aboutQtAct = QtGui.QAction(self.tr("About &Qt"), self)
        self.aboutQtAct.setStatusTip(self.tr("Show the Qt library's About box"))
        self.connect(self.aboutQtAct, QtCore.SIGNAL("triggered()"),
                     QtGui.qApp, QtCore.SLOT("aboutQt()"))



    def createMenus(self):
        self.fileMenu = self.menuBar().addMenu(u"&Главное меню")
        self.fileMenu.addAction(self.newAct)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.saveAct)
        
        #self.editMenu = self.menuBar().addMenu(self.tr("&Edit"))
        self.fileMenu.addAction(self.cutAct)
        self.fileMenu.addAction(self.copyAct)
        self.fileMenu.addAction(self.pasteAct)
        
        self.fileMenu.addAction(self.poolAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.saveAsAct)
        self.fileMenu.addAction(self.dealerAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.templatesAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.reloginAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.sqlDialogAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.tpchangeAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.addonserviceAct)
        self.fileMenu.addSeparator()

        self.fileMenu.addAction(self.logViewAct)
        self.fileMenu.addSeparator()
        

        self.fileMenu.addAction(self.exitAct)

        self.windowMenu = self.menuBar().addMenu(u"&Окна")
        self.connect(self.windowMenu, QtCore.SIGNAL("aboutToShow()"),
                     self.updateWindowMenu)
        self.reportsMenu = self.menuBar().addMenu(u"&Отчёты")
        for menuName, branch in self.reportActs:
            branchMenu = self.reportsMenu.addMenu(self.trUtf8(menuName))
            for leaf in branch:
                branchMenu.addAction(leaf)

        self.menuBar().addSeparator()

        self.helpMenu = self.menuBar().addMenu(u"&Справка")
        
        self.helpMenu.addAction(self.aboutOperAct)
        self.helpMenu.addAction(self.aboutAct)
        #self.helpMenu.addAction(self.aboutQtAct)

    @connlogin
    def reportsMenu(self):
        #print self.sender().data().toInt()
        i,j = [int(vstr) for vstr in str(self.sender().data().toString()).split('_')]
        child=StatReport(connection=connection, chartinfo=_reportsdict[i][1][j])
        self.workspace.addWindow(child)
        child.show()

    def createToolBars(self):
        self.fileToolBar = QtGui.QToolBar(self)
        self.fileToolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.fileToolBar.addAction(self.newAct)
        self.fileToolBar.addAction(self.openAct)
        self.fileToolBar.addAction(self.saveAct)
        self.fileToolBar.setMovable(False)
        self.fileToolBar.setFloatable(False)

        self.fileToolBar.setAllowedAreas(QtCore.Qt.TopToolBarArea)
        self.fileToolBar.setIconSize(QtCore.QSize(18,18))

        self.fileToolBar.addAction(self.cutAct)
        self.fileToolBar.addAction(self.copyAct)
        self.fileToolBar.addAction(self.pasteAct)
        self.fileToolBar.addAction(self.cardsAct)
        self.fileToolBar.addAction(self.netflowReportAct)

        self.addToolBar(QtCore.Qt.TopToolBarArea,self.fileToolBar)

    def createStatusBar(self):
        self.statusBar().showMessage(self.tr("Ready"))

    def readSettings(self):
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        pos = settings.value("pos", QtCore.QVariant(QtCore.QPoint(200, 200))).toPoint()
        size = settings.value("size", QtCore.QVariant(QtCore.QSize(400, 400))).toSize()
        self.move(pos)
        self.resize(size)

    def writeSettings(self):
        settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
        settings.setValue("pos", QtCore.QVariant(self.pos()))
        settings.setValue("size", QtCore.QVariant(self.size()))

    def activeMdiChild(self):
        return self.workspace.activeWindow()

    def findMdiChild(self, fileName):
        canonicalFilePath = QtCore.QFileInfo(fileName).canonicalFilePath()

        for window in self.workspace.windowList():
            if window.currentFile() == canonicalFilePath:
                return window
        return None
    
class Executor(Object):
    def __init__(self):
        pass
    def execute(self, execcmd):
        inQueue.append(execcmd)
        #use locks etc
        return outQueue.pop()
    
class rpcDispatcher(threading.Thread):
    
    def __init__(self):
        pass
    
    def run(self):
        pass

class antiMungeValidator(Pyro.protocol.DefaultConnValidator):
    def __init__(self):
        Pyro.protocol.DefaultConnValidator.__init__(self)
    def createAuthToken(self, authid, challenge, peeraddr, URI, daemon):
        return authid
    def mungeIdent(self, ident):
        return ident
      

def login():
    child = ConnectDialog()
    while True:

        if child.exec_()==1:
            #waitchild = ConnectionWaiting()
            #waitchild.show()
            global splash, username, server_ip
            pixmap = QtGui.QPixmap("splash.png")
            splash = QtGui.QSplashScreen(pixmap, QtCore.Qt.WindowStaysOnTopHint)
            splash.setMask(pixmap.mask()) # this is usefull if the splashscreen is not a regular ractangle...
            splash.show()
            splash.showMessage(u'Starting...', QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom,QtCore.Qt.yellow)
            # make sure Qt really display the splash screen
            global app
            app.processEvents()
            try:
                connection = Pyro.core.getProxyForURI("PYROLOC://%s:7766/rpc" % unicode(child.address))
                password = unicode(QtCore.QCryptographicHash.hash(child.password.toUtf8(), QtCore.QCryptographicHash.Md5).toHex())
                connection._setNewConnectionValidator(antiMungeValidator())
                username = str(child.name)
                server_ip = unicode(child.address)
                connection._setIdentification("%s:%s:0" % (str(child.name), str(password)))
                connection.test()
                #waitchild.hide()
                return connection

            except Exception, e:
                #print "login connection error"
                splash.hide()
                if isinstance(e, Pyro.errors.ConnectionDeniedError):
                    QtGui.QMessageBox.warning(None, unicode(u"Ошибка"), unicode(u"Отказано в авторизации."))
                else:
                    QtGui.QMessageBox.warning(None, unicode(u"Ошибка"), unicode(u"Невозможно подключиться к серверу."))
            #splash.hide()
            #del waitchild
        else:
            #splash.hide()
            return None

if __name__ == "__main__":
    global app
    app = QtGui.QApplication(sys.argv)
    global connection, username, server_ip
    connection = login() 
       
    if connection is None:
        sys.exit()
    connection.commit()
    try:
        global mainwindow
        mainwindow = MainWindow()
        splash.finish(mainwindow) 
        mainwindow.show()
        mainwindow.setWindowTitle("ExpertBilling administrator interface #%s - %s" % (username, server_ip))  
        #app.setStyle("cleanlooks")
        mainwindow.setWindowIcon(QtGui.QIcon("images/icon.png"))
        app.setStyleSheet(open("./style.qss","r").read())
        sys.exit(app.exec_())
        connection.commit()
    except Exception, ex:
        print "main-----------"
        print ex

    #QtGui.QStyle.SH_Table_GridLineColor

