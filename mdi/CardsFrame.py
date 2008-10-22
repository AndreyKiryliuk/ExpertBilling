#-*-coding=utf-8-*-

from PyQt4 import QtCore, QtGui, QtWebKit

from helpers import tableFormat

from helpers import Object as Object
from helpers import makeHeaders
from helpers import dateDelim
from time import mktime
from CustomForms import ComboBoxDialog
import datetime, calendar
from helpers import transaction
from helpers import HeaderUtil, SplitterUtil
from helpers import write_cards
import os, datetime
from randgen import GenPasswd2
import string
from mako.template import Template
from mako.lookup import TemplateLookup
templatedir = "templates/cards/"
strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
class SaleCards(QtGui.QDialog):
    def __init__(self, connection, cards, model=None):
        bhdr = HeaderUtil.getBinaryHeader("sale_cards_frame_header")
        super(SaleCards, self).__init__()
        self.connection = connection
        self.cards = cards # list of cards id
        self.model = model
        self.connection.commit()
        self.nominalsumm = 0
        
        self.setObjectName("SaleCards")
        self.resize(672, 645)
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setGeometry(QtCore.QRect(20, 610, 641, 26))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.comboBox_dealer = QtGui.QComboBox(self)
        self.comboBox_dealer.setGeometry(QtCore.QRect(60, 20, 601, 21))
        self.comboBox_dealer.setObjectName("comboBox_dealer")

        self.label_dealer = QtGui.QLabel(self)
        self.label_dealer.setGeometry(QtCore.QRect(11, 20, 51, 21))
        self.label_dealer.setObjectName("label_dealer")
        self.groupBox_cards_actions = QtGui.QGroupBox(self)
        self.groupBox_cards_actions.setGeometry(QtCore.QRect(10, 240, 651, 61))
        self.groupBox_cards_actions.setObjectName("groupBox_cards_actions")
        self.commandLinkButton_save = QtGui.QCommandLinkButton(self.groupBox_cards_actions)
        self.commandLinkButton_save.setGeometry(QtCore.QRect(10, 20, 201, 31))
        self.commandLinkButton_save.setObjectName("commandLinkButton_save")
        self.commandLinkButton_bill = QtGui.QCommandLinkButton(self.groupBox_cards_actions)
        self.commandLinkButton_bill.setGeometry(QtCore.QRect(220, 20, 201, 31))
        self.commandLinkButton_bill.setObjectName("commandLinkButton_bill")
        self.commandLinkButton_print = QtGui.QCommandLinkButton(self.groupBox_cards_actions)
        self.commandLinkButton_print.setGeometry(QtCore.QRect(430, 20, 201, 31))
        self.commandLinkButton_print.setObjectName("commandLinkButton_print")
        self.groupBox_dealer_info = QtGui.QGroupBox(self)
        self.groupBox_dealer_info.setGeometry(QtCore.QRect(10, 60, 321, 141))
        self.groupBox_dealer_info.setObjectName("groupBox_dealer_info")
        self.lineEdit_debet = QtGui.QLineEdit(self.groupBox_dealer_info)
        self.lineEdit_debet.setGeometry(QtCore.QRect(140, 20, 171, 20))
        self.lineEdit_debet.setObjectName("lineEdit_debet")
        self.spinBox_prepay = QtGui.QDoubleSpinBox(self.groupBox_dealer_info)
        self.spinBox_prepay.setGeometry(QtCore.QRect(140, 50, 81, 20))
        self.spinBox_prepay.setObjectName("spinBox_prepay")
        self.spinBox_prepay.setMaximum(100)
        self.spinBox_prepay.setDecimals(3)
        
        self.label_debet = QtGui.QLabel(self.groupBox_dealer_info)
        self.label_debet.setGeometry(QtCore.QRect(11, 20, 119, 20))
        self.label_debet.setObjectName("label_debet")
        self.label_prepay_procs = QtGui.QLabel(self.groupBox_dealer_info)
        self.label_prepay_procs.setGeometry(QtCore.QRect(11, 51, 119, 20))
        self.label_prepay_procs.setObjectName("label_prepay_procs")
        self.label_paydeffer = QtGui.QLabel(self.groupBox_dealer_info)
        self.label_paydeffer.setGeometry(QtCore.QRect(11, 77, 119, 20))
        self.label_paydeffer.setObjectName("label_paydeffer")
        self.spinBox_paydeffer = QtGui.QSpinBox(self.groupBox_dealer_info)
        self.spinBox_paydeffer.setGeometry(QtCore.QRect(140, 80, 81, 20))
        self.spinBox_paydeffer.setObjectName("spinBox_paydeffer")
        self.spinBox_paydeffer.setMaximum(365)
        
        
        self.label_discount = QtGui.QLabel(self.groupBox_dealer_info)
        self.label_discount.setGeometry(QtCore.QRect(10, 110, 61, 16))
        self.label_discount.setObjectName("label_discount")
        self.spinBox_discount = QtGui.QDoubleSpinBox(self.groupBox_dealer_info)
        self.spinBox_discount.setGeometry(QtCore.QRect(140, 110, 81, 20))
        self.spinBox_discount.setObjectName("spinBox_discount")
        self.spinBox_discount.setMaximum(100)
        self.spinBox_discount.setDecimals(3)
        
        self.groupBox_bill_info = QtGui.QGroupBox(self)
        self.groupBox_bill_info.setGeometry(QtCore.QRect(340, 60, 321, 141))
        self.groupBox_bill_info.setMinimumSize(QtCore.QSize(300, 0))
        self.groupBox_bill_info.setObjectName("groupBox_bill_info")
        self.label_discount_amount = QtGui.QLabel(self.groupBox_bill_info)
        self.label_discount_amount.setGeometry(QtCore.QRect(10, 80, 81, 20))
        self.label_discount_amount.setObjectName("label_discount_amount")
        self.lineEdit_discount_amount = QtGui.QLineEdit(self.groupBox_bill_info)
        self.lineEdit_discount_amount.setGeometry(QtCore.QRect(90, 80, 113, 20))
        self.lineEdit_discount_amount.setObjectName("lineEdit_discount_amount")
        self.lineEdit_amount = QtGui.QLineEdit(self.groupBox_bill_info)
        self.lineEdit_amount.setGeometry(QtCore.QRect(90, 50, 113, 20))
        self.lineEdit_amount.setObjectName("lineEdit_amount")
        self.label_amount = QtGui.QLabel(self.groupBox_bill_info)
        self.label_amount.setGeometry(QtCore.QRect(10, 50, 61, 16))
        self.label_amount.setObjectName("label_amount")
        self.lineEdit_count_cards = QtGui.QLineEdit(self.groupBox_bill_info)
        self.lineEdit_count_cards.setGeometry(QtCore.QRect(90, 20, 113, 20))
        self.lineEdit_count_cards.setObjectName("lineEdit_count_cards")
        self.label_count_carts = QtGui.QLabel(self.groupBox_bill_info)
        self.label_count_carts.setGeometry(QtCore.QRect(10, 20, 71, 20))
        self.label_count_carts.setObjectName("label_count_carts")
        self.lineEdit_for_pay = QtGui.QLineEdit(self.groupBox_bill_info)
        self.lineEdit_for_pay.setGeometry(QtCore.QRect(90, 110, 113, 20))
        self.lineEdit_for_pay.setObjectName("lineEdit_for_pay")
        self.label_for_pay = QtGui.QLabel(self.groupBox_bill_info)
        self.label_for_pay.setGeometry(QtCore.QRect(10, 110, 71, 16))
        self.label_for_pay.setObjectName("label_for_pay")
        self.label_pay = QtGui.QLabel(self)
        self.label_pay.setGeometry(QtCore.QRect(340, 210, 81, 21))
        self.label_pay.setObjectName("label_pay")
        self.lineEdit_pay = QtGui.QLineEdit(self)
        self.lineEdit_pay.setGeometry(QtCore.QRect(430, 210, 231, 21))
        self.lineEdit_pay.setObjectName("lineEdit_pay")
        self.tableWidget = QtGui.QTableWidget(self)
        self.tableWidget.setGeometry(QtCore.QRect(10, 310, 651, 291))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget = tableFormat(self.tableWidget)

        self.retranslateUi()
        
        tableHeader = self.tableWidget.horizontalHeader()
        
        self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.saveHeader)
        
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), self.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), self.reject)
        QtCore.QObject.connect(self.spinBox_discount, QtCore.SIGNAL("valueChanged (double)"), self.recalculateAmount)
        QtCore.QObject.connect(self.spinBox_prepay, QtCore.SIGNAL("valueChanged (double)"), self.recalculateAmount)
        #QtCore.QObject.connect(self.lineEdit_pay, QtCore.SIGNAL("editingFinished ()"), self.recalculatePrepay)
        
        QtCore.QObject.connect(self.commandLinkButton_save, QtCore.SIGNAL("clicked()"), self.exportToXML)
        QtCore.QObject.connect(self.commandLinkButton_print, QtCore.SIGNAL("clicked()"), self.printCards)
        
        QtCore.QMetaObject.connectSlotsByName(self)
        
        HeaderUtil.nullifySaved("sale_cards_frame_header")
        
        self.setTabOrder(self.comboBox_dealer, self.lineEdit_debet)
        self.setTabOrder(self.lineEdit_debet, self.spinBox_prepay)
        self.setTabOrder(self.spinBox_prepay, self.spinBox_paydeffer)
        self.setTabOrder(self.spinBox_paydeffer, self.spinBox_discount)
        self.setTabOrder(self.spinBox_discount, self.lineEdit_count_cards)
        self.setTabOrder(self.lineEdit_count_cards, self.lineEdit_amount)
        self.setTabOrder(self.lineEdit_amount, self.lineEdit_discount_amount)
        self.setTabOrder(self.lineEdit_discount_amount, self.lineEdit_for_pay)
        self.setTabOrder(self.lineEdit_for_pay, self.lineEdit_pay)
        self.setTabOrder(self.lineEdit_pay, self.commandLinkButton_save)
        self.setTabOrder(self.commandLinkButton_save, self.commandLinkButton_bill)
        self.setTabOrder(self.commandLinkButton_bill, self.commandLinkButton_print)
        self.setTabOrder(self.commandLinkButton_print, self.tableWidget)
        self.setTabOrder(self.tableWidget, self.buttonBox)
        self.refresh()
        self.fixtures()
        QtCore.QObject.connect(self.comboBox_dealer,QtCore.SIGNAL("currentIndexChanged(int)"),self.dealerInfo)
        self.comboBox_dealer.emit(QtCore.SIGNAL("currentIndexChanged(int)"), self.comboBox_dealer.currentIndex())
        self.setWidgetsDisabled()
        if not bhdr.isEmpty():
            HeaderUtil.setBinaryHeader("sale_cards_frame_header", bhdr)
            HeaderUtil.getHeader("sale_cards_frame_header", self.tableWidget)
        
    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "РџСЂРѕРґР°Р¶Р° РєР°СЂС‚", None, QtGui.QApplication.UnicodeUTF8))
        self.label_dealer.setText(QtGui.QApplication.translate("Dialog", "Р”РёР»РµСЂ", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_cards_actions.setTitle(QtGui.QApplication.translate("Dialog", "Р”РµР№СЃС‚РІРёСЏ СЃ РїР°СЂС‚РёРµР№ РєР°СЂС‚РѕС‡РµРє", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_save.setText(QtGui.QApplication.translate("Dialog", "РЎРѕС…СЂР°РЅРёС‚СЊ РІ С„Р°Р№Р»", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_bill.setText(QtGui.QApplication.translate("Dialog", "Р’С‹РїРёСЃР°С‚СЊ СЃС‡С‘С‚", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_print.setText(QtGui.QApplication.translate("Dialog", "Р Р°СЃРїРµС‡Р°С‚Р°С‚СЊ", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_dealer_info.setTitle(QtGui.QApplication.translate("Dialog", "РС„РѕСЂРјР°С†РёСЏ Рѕ РґРёР»РµСЂРµ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_debet.setText(QtGui.QApplication.translate("Dialog", "Р—Р°РґРѕР»Р¶РµРЅРЅРѕСЃС‚СЊ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_prepay_procs.setText(QtGui.QApplication.translate("Dialog", "Р Р°Р·РјРµСЂ РїСЂРµРґРѕРїР»Р°С‚С‹, %", None, QtGui.QApplication.UnicodeUTF8))
        self.label_paydeffer.setText(QtGui.QApplication.translate("Dialog", "РћС‚СЃСЂРѕС‡РєР° РїР»Р°С‚РµР¶Р°", None, QtGui.QApplication.UnicodeUTF8))
        self.label_discount.setText(QtGui.QApplication.translate("Dialog", "РЎРєРёРґРєР°, %", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_bill_info.setTitle(QtGui.QApplication.translate("Dialog", "РџР»Р°С‚С‘Р¶РЅР°СЏ РёРЅС„РѕСЂРјР°С†РёСЏ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_discount_amount.setText(QtGui.QApplication.translate("Dialog", "РЎСѓРјРјР° СЃРєРёРґРєРё", None, QtGui.QApplication.UnicodeUTF8))
        self.label_amount.setText(QtGui.QApplication.translate("Dialog", "РќР° СЃСѓРјРјСѓ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_count_carts.setText(QtGui.QApplication.translate("Dialog", "РљРѕР»-РІРѕР» РєР°СЂС‚", None, QtGui.QApplication.UnicodeUTF8))
        self.label_for_pay.setText(QtGui.QApplication.translate("Dialog", "Рљ РѕРїР»Р°С‚Рµ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_pay.setText(QtGui.QApplication.translate("Dialog", "РЎСѓРјРјР° РѕРїР»Р°С‚С‹", None, QtGui.QApplication.UnicodeUTF8))

        columns = ["#",u"РЎРµСЂРёСЏ",u"РќРѕРјРёРЅР°Р»",u"PIN",u"РђРєС‚РёРІРёСЂРѕРІР°С‚СЊ СЃ",u"РђРєС‚РёРІРёСЂРѕРІР°С‚СЊ РїРѕ"]
        makeHeaders(columns, self.tableWidget)
        
        
    def exportToXML(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self,
                                                  "Create XML File", "", "XML Files (*.xml)")
        if fileName=="":
            return
        try:
            f = open(fileName, "w")
            f.write("<xml>")
            for x in xrange(self.tableWidget.rowCount()):
                #card = unicode(self.tableWidget.item(x,0).text())
                f.write("<card>")
                f.write("<id>%s</id>" % unicode(self.tableWidget.item(x,0).text()))
                f.write("<series>%s</series>" % unicode(self.tableWidget.item(x,1).text()))
                f.write("<nominal>%s</nominal>" % unicode(self.tableWidget.item(x,2).text()))
                f.write("<pin>%s</pin>" % unicode(self.tableWidget.item(x,3).text()))
                f.write("<date_start>%s</date_start>" % unicode(self.tableWidget.item(x,4).text()))
                f.write("<date_end>%s</date_end>" % unicode(self.tableWidget.item(x,5).text()))
                f.write("</card>")
            f.write("</xml>")
            f.close()
            QtGui.QMessageBox.information(self, u"Р”Р°РЅРЅС‹Рµ СЃРѕС…СЂР°РЅРµРЅС‹", unicode(u"Р”Р°РЅРЅС‹Рµ СЃРѕС…СЂР°РЅРµРЅС‹ СѓСЃРїРµС€РЅРѕ."))
        except Exception, e:
            print e
            QtGui.QMessageBox.warning(self, u"Р”Р°РЅРЅС‹Рµ РЅРµ СЃРѕС…СЂР°РЅРµРЅС‹", unicode(u"Р’Рѕ РІСЂРµРјСЏ СЃРѕС…СЂР°РЅРµРЅРёСЏ РїСЂРѕРёР·РѕС€Р»Рё РѕС€РёР±РєРё."))
            
    def printCards(self):
        
        if len(self.cards)>0:
           crd = "(" + ",".join(self.cards) + ")"
        else:
           crd = "(0)" 
        #cards = self.con
        #templatelookup = TemplateLookup(directories=['.'])
        
        cards = self.connection.sql_as_dict("SELECT * FROM billservice_card WHERE id IN %s AND sold is Null;" % crd)
        data="""
        <html>
        <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
        </head>
        <body>
        """;
        
        for card in cards:
            templ = Template(filename="templates/cards/%s" % card['template'], input_encoding='utf-8')
            data+=templ.render_unicode(card=card)
        import codecs
        
        data+="</body></html>"
        file= open('templates/cards/cards.html', 'wb')
        file.write(data.encode("utf-8", 'replace'))
        file.flush()
        a=CardPreviewDialog(url="templates/cards/cards.html")
        a.exec_()
        print data
        
    def recalculateAmount(self, t=None):
        #print "recal"
        discount = (float(self.spinBox_discount.value())/float(100.00))*float(self.nominalsumm)
        #print "discount", discount
        #print index, dealer.id


        prepay = self.spinBox_prepay.value()
        self.lineEdit_for_pay.setText(unicode((self.nominalsumm-discount)))
        self.lineEdit_discount_amount.setText(unicode(discount))
        self.lineEdit_pay.setText(unicode(float(self.nominalsumm-discount)*(prepay/100.00)))
    
    def recalculatePrepay(self):
        self.spinBox_prepay.setValue(float(self.lineEdit_pay.text())/float(self.lineEdit_for_pay.text())*100)
        
    def fixtures(self):
        self.lineEdit_count_cards.setText(unicode(len(self.cards)))
        dealers = self.connection.sql("SELECT * FROM billservice_dealer WHERE deleted=False;")
        
        i=0
        for dealer in dealers:
            self.comboBox_dealer.addItem(unicode(u"%s, %s" % (dealer.organization, dealer.contactperson)))
            self.comboBox_dealer.setItemData(i, QtCore.QVariant(dealer.id))
            if self.model:
                if self.model.daler_id==dealer.id:
                    self.model_dealer = dealer
                    self.comboBox_dealer.setCurrentIndex(i)
                    self.comboBox_dealer.setDisabled(True)
            i+=1
            
    def dealerInfo(self, index):
        id = self.comboBox_dealer.itemData(index).toInt()[0]

        #print id
        dealer = self.connection.get("SELECT * FROM billservice_dealer WHERE id=%s and deleted=False" % id)
        self.model_dealer = dealer
        self.spinBox_discount.setValue(dealer.discount)
        self.spinBox_paydeffer.setValue(dealer.paydeffer)
        self.spinBox_prepay.setValue(dealer.prepayment)
        self.recalculateAmount()
        #self.
        
    def accept(self):
        if self.model:
            return
        try:
            model = Object()
            now = datetime.datetime.now()
            model.dealer_id = self.comboBox_dealer.itemData(self.comboBox_dealer.currentIndex()).toInt()[0]
            model.pay = unicode(self.lineEdit_pay.text())
            model.sum_for_pay = unicode(self.lineEdit_for_pay.text())
            model.paydeffer = self.spinBox_paydeffer.value()
            model.discount = self.spinBox_discount.value()
            model.discount_sum = unicode(self.lineEdit_discount_amount.text())
            model.prepayment = unicode(self.spinBox_prepay.value())
            model.created = now 
            
            try:
                salecard_id = self.connection.create(model.save("billservice_salecard"))
                #self.connection.commit()
            except Exception, e:
                print e
                QtGui.QMessageBox.warning(self, u"РћС€РёР±РєР°", unicode(u"Рљ СЃРѕР¶Р°Р»РµРЅРёСЋ, РґР°РЅРЅС‹Рµ РЅРµ РјРѕРіСѓС‚ Р±С‹С‚СЊ СЃРѕС…СЂР°РЅРµРЅС‹."))
                return
    
            #print [self.tableWidget.item(x,0).text().toInt()[0] for x in xrange(self.tableWidget.rowCount())]
            #self.connection.rollback()
            #return
            for card_id in [self.tableWidget.item(x,0).text().toInt()[0] for x in xrange(self.tableWidget.rowCount())]:
                salecard = Object()
                salecard.card_id = card_id
                salecard.salecard_id = salecard_id
                card = Object()
                card.id = card_id
                card.sold = now
                self.connection.create(salecard.save("billservice_salecard_cards"))
                self.connection.create(card.save("billservice_card"))
    
                
            self.connection.commit()
        except Exception, e:
            print e
            self.connection.rollback()
            QtGui.QMessageBox.warning(self, u"РћС€РёР±РєР°", unicode(u"Рљ СЃРѕР¶Р°Р»РµРЅРёСЋ, РїСЂРѕРёР·РѕС€Р»Р° РЅРµРїСЂРµРґРІРёРґРµРЅРЅР°СЏ РѕС€РёР±РєР°. РћС‚РјРµРЅР° РїСЂРѕРґР°Р¶Рё."))
            return 
        QtGui.QDialog.accept(self)
            
    
    def addrow(self, value, x, y):
        headerItem = QtGui.QTableWidgetItem()
        
        #print 'activated',activated
        if value == None:
            value = ""
            
        headerItem.setText(unicode(value))

    
        self.tableWidget.setItem(x,y,headerItem)
        
    def setWidgetsDisabled(self):
        self.lineEdit_amount.setDisabled(True)
        self.lineEdit_count_cards.setDisabled(True)
        self.lineEdit_debet.setDisabled(True)
        #self.spinBox_discount.setDisabled(True)
        self.lineEdit_discount_amount.setDisabled(True)
        self.lineEdit_for_pay.setDisabled(True)
        #self.spinBox_paydeffer.setDisabled(True)
        #self.spinBox_prepay.setDisabled(True)
        
    def refresh(self):
        print self.cards
        if len(self.cards)>0:
           crd = "(" + ",".join(self.cards) + ")"
        else:
           crd = "(0)" 
        cards = self.connection.sql("SELECT * FROM billservice_card WHERE id IN %s AND sold is Null;" % crd)
        
        self.tableWidget.setRowCount(len(cards))
        
        nominal = 0
        i=0
        for a in cards:
            
            self.addrow(a.id, i,0)
            self.addrow(a.series, i,1)
            self.addrow(a.nominal, i,2)
            self.addrow(a.pin, i,3)
            self.addrow(a.start_date.strftime(strftimeFormat), i,4)
            self.addrow(a.end_date.strftime(strftimeFormat), i,5)
            nominal += a.nominal
            i+=1
            
        self.lineEdit_count_cards.setText(unicode(len(cards)))
        self.lineEdit_amount.setText(unicode(nominal))
        self.nominalsumm=nominal
        HeaderUtil.getHeader("sale_cards_frame_header", self.tableWidget)
        
    def saveHeader(self, *args):
        if self.tableWidget.rowCount():
            HeaderUtil.saveHeader("cards_frame_header", self.tableWidget)
        
class AddCards(QtGui.QDialog):
    def __init__(self, connection,last_series=0):
        super(AddCards, self).__init__()
        
        self.connection = connection
        self.last_series=last_series
        self.connection.commit()
        self.resize(337, 426)
        self.op_model   = Object()
        self.bank_model = Object()
        self.gridLayout = QtGui.QGridLayout(self)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonBox = QtGui.QDialogButtonBox(self)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)
        self.tabWidget = QtGui.QTabWidget(self)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")
        self.params_groupBox = QtGui.QGroupBox(self.tab)
        self.params_groupBox.setGeometry(QtCore.QRect(10, 10, 291, 171))
        self.params_groupBox.setObjectName("params_groupBox")
        self.nominal_lineEdit = QtGui.QLineEdit(self.params_groupBox)
        self.nominal_lineEdit.setGeometry(QtCore.QRect(110, 50, 171, 20))
        self.nominal_lineEdit.setObjectName("nominal_lineEdit")
        self.count_label = QtGui.QLabel(self.params_groupBox)
        self.count_label.setGeometry(QtCore.QRect(10, 80, 80, 21))
        self.count_label.setObjectName("count_label")
        self.pin_label = QtGui.QLabel(self.params_groupBox)
        self.pin_label.setGeometry(QtCore.QRect(10, 110, 59, 21))
        self.pin_label.setObjectName("pin_label")
        self.series_label = QtGui.QLabel(self.params_groupBox)
        self.series_label.setGeometry(QtCore.QRect(10, 20, 46, 21))
        self.series_label.setObjectName("series_label")
        self.nominal_label = QtGui.QLabel(self.params_groupBox)
        self.nominal_label.setGeometry(QtCore.QRect(10, 50, 46, 21))
        self.nominal_label.setObjectName("nominal_label")
        self.pin_spinBox = QtGui.QSpinBox(self.params_groupBox)
        self.pin_spinBox.setGeometry(QtCore.QRect(110, 110, 101, 21))
        self.pin_spinBox.setMaximum(32)
        self.pin_spinBox.setObjectName("pin_spinBox")
        self.l_checkBox = QtGui.QCheckBox(self.params_groupBox)
        self.l_checkBox.setGeometry(QtCore.QRect(110, 140, 91, 21))
        self.l_checkBox.setObjectName("l_checkBox")
        self.numbers_checkBox = QtGui.QCheckBox(self.params_groupBox)
        self.numbers_checkBox.setGeometry(QtCore.QRect(200, 140, 81, 21))
        self.numbers_checkBox.setObjectName("numbers_checkBox")
        self.count_spinBox = QtGui.QSpinBox(self.params_groupBox)
        self.count_spinBox.setGeometry(QtCore.QRect(110, 80, 171, 21))
        self.count_spinBox.setFrame(True)
        self.count_spinBox.setButtonSymbols(QtGui.QAbstractSpinBox.UpDownArrows)
        self.count_spinBox.setAccelerated(True)
        self.count_spinBox.setMaximum(999999999)
        self.count_spinBox.setObjectName("count_spinBox")
        self.series_spinBox = QtGui.QSpinBox(self.params_groupBox)
        self.series_spinBox.setGeometry(QtCore.QRect(110, 20, 171, 22))
        self.series_spinBox.setMaximum(999999999)
        self.series_spinBox.setObjectName("series_spinBox")
        self.period_groupBox = QtGui.QGroupBox(self.tab)
        self.period_groupBox.setGeometry(QtCore.QRect(10, 190, 291, 91))
        self.period_groupBox.setObjectName("period_groupBox")
        self.end_dateTimeEdit = QtGui.QDateTimeEdit(self.period_groupBox)
        self.end_dateTimeEdit.setGeometry(QtCore.QRect(70, 50, 194, 22))
        self.end_dateTimeEdit.setCalendarPopup(True)
        self.end_dateTimeEdit.setObjectName("end_dateTimeEdit")
        self.start_dateTimeEdit = QtGui.QDateTimeEdit(self.period_groupBox)
        self.start_dateTimeEdit.setGeometry(QtCore.QRect(70, 20, 194, 22))
        self.start_dateTimeEdit.setCalendarPopup(True)
        self.start_dateTimeEdit.setObjectName("start_dateTimeEdit")
        self.start_label = QtGui.QLabel(self.period_groupBox)
        self.start_label.setGeometry(QtCore.QRect(10, 20, 46, 21))
        self.start_label.setObjectName("start_label")
        self.end_label = QtGui.QLabel(self.period_groupBox)
        self.end_label.setGeometry(QtCore.QRect(10, 50, 46, 16))
        self.end_label.setObjectName("end_label")
        self.groupBox_template = QtGui.QGroupBox(self.tab)
        self.groupBox_template.setGeometry(QtCore.QRect(10, 290, 291, 51))
        self.groupBox_template.setObjectName("groupBox_template")
        self.comboBox_templates = QtGui.QComboBox(self.groupBox_template)
        self.comboBox_templates.setGeometry(QtCore.QRect(100, 20, 181, 22))
        self.comboBox_templates.setObjectName("comboBox_templates")
        self.toolButton_preview = QtGui.QToolButton(self.groupBox_template)
        self.toolButton_preview.setGeometry(QtCore.QRect(10, 20, 81, 20))
        self.toolButton_preview.setObjectName("toolButton_preview")
        self.tabWidget.addTab(self.tab, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        

        self.retranslateUi()
        self.connect(self.buttonBox,QtCore.SIGNAL("accepted()"),self.accept)
        self.connect(self.buttonBox,QtCore.SIGNAL("rejected()"),self.reject)
        self.connect(self.toolButton_preview,QtCore.SIGNAL("clicked()"),self.preView)
        self.fixtures()


    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "Параметры серии", None, QtGui.QApplication.UnicodeUTF8))
        self.params_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Параметры генерации карточки", None, QtGui.QApplication.UnicodeUTF8))
        self.count_label.setText(QtGui.QApplication.translate("Dialog", "Количество", None, QtGui.QApplication.UnicodeUTF8))
        self.pin_label.setText(QtGui.QApplication.translate("Dialog", "Длина пина", None, QtGui.QApplication.UnicodeUTF8))
        self.series_label.setText(QtGui.QApplication.translate("Dialog", "Серия", None, QtGui.QApplication.UnicodeUTF8))
        self.nominal_label.setText(QtGui.QApplication.translate("Dialog", "Номинал", None, QtGui.QApplication.UnicodeUTF8))
        self.l_checkBox.setText(QtGui.QApplication.translate("Dialog", "Буквы (a-Z)", None, QtGui.QApplication.UnicodeUTF8))
        self.numbers_checkBox.setText(QtGui.QApplication.translate("Dialog", "Цифры (0-9)", None, QtGui.QApplication.UnicodeUTF8))
        self.period_groupBox.setTitle(QtGui.QApplication.translate("Dialog", "Период действия", None, QtGui.QApplication.UnicodeUTF8))
        self.start_label.setText(QtGui.QApplication.translate("Dialog", "Начало", None, QtGui.QApplication.UnicodeUTF8))
        self.end_label.setText(QtGui.QApplication.translate("Dialog", "Конец", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_template.setTitle(QtGui.QApplication.translate("Dialog", "Шаблон для печати", None, QtGui.QApplication.UnicodeUTF8))
        self.toolButton_preview.setText(QtGui.QApplication.translate("Dialog", "Предросмотр", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("Dialog", "Параметры", None, QtGui.QApplication.UnicodeUTF8))

    def accept(self):
        """
        понаставить проверок
        """
        try:
            if self.l_checkBox.checkState()==0 and self.numbers_checkBox.checkState()==0:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Вы не выбрали состав PIN-кода"))
                return
            
            if self.nominal_lineEdit.text().toInt()[0]==0:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указан номинал"))
                return
            
            if self.count_spinBox.text().toInt()[0]==0:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указано количество генерируемых карточек"))
                return
            
            if self.pin_spinBox.text().toInt()[0]==0:
                QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Не указана длина PIN-кода"))
                return        
            
            
            
            mask=[]
            if self.l_checkBox.checkState()==2:
                mask+=string.letters
            if self.numbers_checkBox.checkState()==2:
                mask+=string.digits
                
            dnow = datetime.datetime.now()
            for x in xrange(0, self.count_spinBox.text().toInt()[0]):
                model = Object()
                #model.card_group_id = self.group
                model.series = unicode(self.series_spinBox.text())
                model.pin = GenPasswd2(length=self.pin_spinBox.text().toInt()[0],chars=mask)
                model.nominal = unicode(self.nominal_lineEdit.text())
                model.start_date = self.start_dateTimeEdit.dateTime().toPyDateTime()
                model.end_date = self.end_dateTimeEdit.dateTime().toPyDateTime()
                model.template = str(self.comboBox_templates.currentText())
                model.created = dnow
                #model.sold=False
                #model.activated=False
                
                print model.pin
                print model.__dict__
                self.connection.create(model.save("billservice_card"))
            
            self.connection.commit()
        except Exception, ex:
            self.connection.rollback()
            print ex
            QtGui.QMessageBox.warning(self, u"Ошибка", unicode(u"Во время генерации карт возникла непредвиденная ошибка."))
            return

        QtGui.QDialog.accept(self)

    def fixtures(self):
        start=datetime.datetime.now()
        #end=datetime.datetime.now()

        self.series_spinBox.setMinimum(self.last_series)
        self.start_dateTimeEdit.setMinimumDate(start)
        self.end_dateTimeEdit.setMinimumDate(start)
        self.updateTemplates()
        
        try:
            self.op_model =self.connection.sql("SELECT * FROM billservice_operator;")[0]
        except Exception, e:
            print e
        try:
            self.bank_model=self.connection.get("SELECT * FROM billservice_bankdata WHERE operator_id=%d" % self.op_model.id)
        except Exception, e:
            print e
            

    def preView(self):
        tmplt = str(self.comboBox_templates.currentText())
        if not tmplt:
            QtGui.QMessageBox.warning(self, u"Внимание!", u"Вы не выбрали шаблон!")
            return
        mask=[]
        if self.l_checkBox.checkState()==2:
            mask+=string.letters
        if self.numbers_checkBox.checkState()==2:
            mask+=string.digits
        tdct = {}
        tdct["pin"] = GenPasswd2(length=self.pin_spinBox.text().toInt()[0],chars=mask)
        wr_files, i = write_cards(templatedir + "/" + tmplt, [tdct], strict=None, adddicts=[self.op_model.__dict__, self.bank_model.__dict__])
        if i:
            print wr_files
            child = CardPreviewDialog(wr_files[0])
            child.exec_()
            os.remove(wr_files[0])
        else:
            QtGui.QMessageBox.warning(self, u"Внимание!", u"При создании шаблона для предпросмотра произошли ошибки!")
        
        
    def updateTemplates(self):
        #print os.listdir("cards")
        #print [unicode(os.path.basename(tmplt)) for tmplt in os.listdir(templatedir) if (tmplt.find("__printandum__" == -1))]
        self.comboBox_templates.addItems([unicode(tmplt) for tmplt in os.listdir(templatedir) if ((tmplt.find("_printandum_") == -1) and os.path.isfile(''.join((templatedir, '/',tmplt))))])
        #templates = [unicode(os.path.basename(tmplt)) for tmplt in os.listdir(templatedir) if (tmplt.find("__printandum__" == -1))]
        #for tstr in templates:
            #self.comboBox_templates.addItem(unicode(tstr))

class CardsChild(QtGui.QMainWindow):
    sequenceNumber = 1

    def __init__(self, connection):
        bhdr = HeaderUtil.getBinaryHeader("cards_frame_header")
        self.splname = "cards_frame_splitter"
        bspltr = SplitterUtil.getBinarySplitter(self.splname)
        super(CardsChild, self).__init__()
        
        self.connection = connection
        self.strftimeFormat = "%d" + dateDelim + "%m" + dateDelim + "%Y %H:%M:%S"
        
        self.setObjectName("CardsMDI")
        self.resize(947, 619)
        self.setIconSize(QtCore.QSize(18, 18))
        self.centralwidget = QtGui.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        
        self.tableWidget = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget = tableFormat(self.tableWidget)
        self.tableWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 1)
        self.setCentralWidget(self.centralwidget)
        #self.statusbar = QtGui.QStatusBar(self)
        #self.statusbar.setObjectName("statusbar")
        #self.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(self)
        self.toolBar.setMovable(False)
        self.toolBar.setIconSize(QtCore.QSize(18, 18))
        self.toolBar.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar.setFloatable(False)
        self.toolBar.setObjectName("toolBar")
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        
        self.toolBar_filter = QtGui.QToolBar(self)
        self.toolBar_filter.setMovable(False)
        self.toolBar_filter.setAllowedAreas(QtCore.Qt.BottomToolBarArea)
        #self.toolBar_filter.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.toolBar_filter.setFloatable(False)
        self.toolBar_filter.setObjectName("toolBar_filter")
        ###################### Filter
        self.comboBox_nominal = QtGui.QComboBox(self)
        
        self.comboBox_nominal.setGeometry(QtCore.QRect(0,0,60,20))
        #self.comboBox_nominal.setValidator(QtGui.QIntValidator)
        self.comboBox_nominal.setEditable(True)
        
        self.date_start = QtGui.QDateTimeEdit(self)
        self.date_start.setGeometry(QtCore.QRect(420,9,161,20))
        self.date_start.setCalendarPopup(True)
        self.date_start.setObjectName("date_start")

        self.date_end = QtGui.QDateTimeEdit(self)
        self.date_end.setGeometry(QtCore.QRect(420,42,161,20))
        self.date_end.setButtonSymbols(QtGui.QAbstractSpinBox.PlusMinus)
        self.date_end.setCalendarPopup(True)
        self.date_end.setObjectName("date_end")

        self.label_date_start = QtGui.QLabel(self)
        self.label_date_start.setMargin(10)
        self.label_date_start.setObjectName("date_start_label")

        self.label_date_end = QtGui.QLabel(self)
        self.label_date_end.setMargin(10)
        self.label_date_end.setObjectName("date_end_label")
        
        self.label_nominal = QtGui.QLabel(self)
        self.label_nominal.setMargin(10)
        
        self.label_filter = QtGui.QLabel(self)
        self.label_filter.setMargin(10)
        
        self.checkBox_sold = QtGui.QCheckBox(self)
        self.checkBox_activated = QtGui.QCheckBox(self)
        
        self.checkBox_filter = QtGui.QCheckBox(self)
        
        self.pushButton_go = QtGui.QPushButton(self)
        
        self.toolBar_filter.addWidget(self.checkBox_filter)
        self.toolBar_filter.addWidget(self.label_nominal)
        self.toolBar_filter.addWidget(self.comboBox_nominal)
        self.toolBar_filter.addWidget(self.checkBox_sold)
        self.toolBar_filter.addWidget(self.checkBox_activated)
        self.toolBar_filter.addWidget(self.label_date_start)
        self.toolBar_filter.addWidget(self.date_start)
        self.toolBar_filter.addWidget(self.label_date_end)
        self.toolBar_filter.addWidget(self.date_end)

        self.toolBar_filter.addWidget(self.pushButton_go)

        ######################
        
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar_filter)
        self.insertToolBarBreak(self.toolBar_filter)
        
        self.actionGenerate_Cards = QtGui.QAction(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/add.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionGenerate_Cards.setIcon(icon)
        self.actionGenerate_Cards.setObjectName("actionGenerate_Cards")

        self.actionDelete_Cards = QtGui.QAction(self)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/del.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDelete_Cards.setIcon(icon)
        self.actionDelete_Cards.setObjectName("actionDelete_Cards")
        
        self.actionEnable_Card = QtGui.QAction(self)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("images/enable.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionEnable_Card.setIcon(icon1)
        self.actionEnable_Card.setObjectName("actionEnable_Card")
        self.actionDisable_Card = QtGui.QAction(self)
        
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("images/disable.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionDisable_Card.setIcon(icon2)
        self.actionDisable_Card.setObjectName("actionDisable_Card")
        self.actionSell_Card = QtGui.QAction(self)
        
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap("images/dollar.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionSell_Card.setIcon(icon3)
        self.actionSell_Card.setObjectName("actionSell_Card")
        
        self.toolBar.addAction(self.actionGenerate_Cards)
        self.toolBar.addAction(self.actionDelete_Cards)
        self.toolBar.addAction(self.actionEnable_Card)
        self.toolBar.addAction(self.actionDisable_Card)
        self.toolBar.addAction(self.actionSell_Card)        
        
        tableHeader = self.tableWidget.horizontalHeader()
        
        self.connect(tableHeader, QtCore.SIGNAL("sectionResized(int,int,int)"), self.saveHeader)
        self.connect(self.actionGenerate_Cards, QtCore.SIGNAL("triggered()"),  self.generateCards)
        self.connect(self.actionDelete_Cards, QtCore.SIGNAL("triggered()"),  self.deleteCards)
        self.connect(self.actionEnable_Card, QtCore.SIGNAL("triggered()"),  self.enableCard)
        self.connect(self.actionDisable_Card, QtCore.SIGNAL("triggered()"),  self.disableCard)
        self.connect(self.actionSell_Card, QtCore.SIGNAL("triggered()"),  self.saleCard )
        self.connect(self.pushButton_go, QtCore.SIGNAL("clicked()"),  self.refresh)
        self.connect(self.checkBox_filter, QtCore.SIGNAL("stateChanged(int)"), self.filterActions)
        
        self.retranslateUi()
        
        #HeaderUtil.nullifySaved("cards_frame_header")
        
        self.filterActions()
        self.fixtures()
        if not bhdr.isEmpty():
            HeaderUtil.setBinaryHeader("cards_frame_header", bhdr)
            HeaderUtil.getHeader("cards_frame_header", self.tableWidget)
        
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            self.date_start.setDateTime(settings.value("cards_date_start", QtCore.QVariant(QtCore.QDateTime(2000,1,1,0,0))).toDateTime())
            self.date_end.setDateTime(settings.value("cards_date_end", QtCore.QVariant(QtCore.QDateTime(2000,1,1,0,0))).toDateTime())
        except Exception, ex:
            print "Transactions settings error: ", ex
        #===============================================================================

        
    def retranslateUi(self):

        self.tableWidget.clear()
        
        columns=['#', u'РЎРµСЂРёСЏ', u'РќРѕРјРёРЅР°Р»', u'PIN', u"РџСЂРѕРґР°РЅРѕ", u"РђРєС‚РёРІРёСЂРѕРІР°РЅРѕ", u'РђРєС‚РёРІРёСЂРѕРІР°С‚СЊ c', u'РђРєС‚РёРІРёСЂРѕРІР°С‚СЊ РїРѕ']
        makeHeaders(columns, self.tableWidget)
        
        self.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Система карт оплаты", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar.setWindowTitle(QtGui.QApplication.translate("MainWindow", "toolBar", None, QtGui.QApplication.UnicodeUTF8))
        self.toolBar_filter.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Filter", None, QtGui.QApplication.UnicodeUTF8))
        self.actionGenerate_Cards.setText(QtGui.QApplication.translate("MainWindow", "Сгенерировать партию", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDelete_Cards.setText(QtGui.QApplication.translate("MainWindow", "Удалить карты", None, QtGui.QApplication.UnicodeUTF8))
        self.actionEnable_Card.setText(QtGui.QApplication.translate("MainWindow", "Активна", None, QtGui.QApplication.UnicodeUTF8))
        self.actionDisable_Card.setText(QtGui.QApplication.translate("MainWindow", "Неактивна", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSell_Card.setText(QtGui.QApplication.translate("MainWindow", "Продать", None, QtGui.QApplication.UnicodeUTF8))
        self.label_nominal.setText(QtGui.QApplication.translate("MainWindow", "Номинал", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_filter.setText(QtGui.QApplication.translate("MainWindow", "Фильтр", None, QtGui.QApplication.UnicodeUTF8))
        self.label_date_start.setText(QtGui.QApplication.translate("MainWindow", "С", None, QtGui.QApplication.UnicodeUTF8))
        self.label_date_end.setText(QtGui.QApplication.translate("MainWindow", "По", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_sold.setText(QtGui.QApplication.translate("MainWindow", "Проданные", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox_activated.setText(QtGui.QApplication.translate("MainWindow", "Активированные", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButton_go.setText(QtGui.QApplication.translate("MainWindow", "Фильтровать", None, QtGui.QApplication.UnicodeUTF8))

        self.tableWidget.setColumnHidden(0, True)

    def saleCard(self):
        #cards = [self.tableWidget.item(x.row(),0) for x in self.tableWidget.selected(column = 0)]
        
        items = self.tableWidget.selectedIndexes()
        cards = []
        for item in items:
            if item.column()>0:
                continue
            cards.append(unicode(self.tableWidget.item(item.row(), 0).text()))
        #print a,b
        
        
        child = SaleCards(connection=self.connection, cards = cards)
        if child.exec_()==1:
            self.refresh()
        
    def fixtures(self):
        nominals = self.connection.sql("SELECT nominal FROM billservice_card GROUP BY nominal")
        self.comboBox_nominal.clear()
        for nom in nominals:
            
            self.comboBox_nominal.addItem(unicode(nom.nominal))
            
    def filterActions(self):
        if self.checkBox_filter.checkState()==2:
            self.label_nominal.setDisabled(False)
            self.comboBox_nominal.setDisabled(False)
            self.label_date_start.setDisabled(False)
            self.date_start.setDisabled(False)
            self.label_date_end.setDisabled(False)
            self.date_end.setDisabled(False)
            self.checkBox_sold.setDisabled(False)
            self.checkBox_activated.setDisabled(False)
            self.pushButton_go.setDisabled(False)
        else:
            self.label_nominal.setDisabled(True)
            self.comboBox_nominal.setDisabled(True)
            self.label_date_start.setDisabled(True)
            self.date_start.setDisabled(True)
            self.label_date_end.setDisabled(True)
            self.date_end.setDisabled(True)
            self.checkBox_sold.setDisabled(True)
            self.checkBox_activated.setDisabled(True)
            self.pushButton_go.setDisabled(True)
            self.refresh()
            
    def enableCard(self):
        for index in self.tableWidget.selectedIndexes():
            if index.column()>1:
                continue
            i=unicode(self.tableWidget.item(index.row(), 0).text())
            #print i
            try:
                #ids.append()
                model=self.connection.get("SELECT * FROM billservice_card WHERE id=%s" % int(i))
                model.disabled=False
                self.connection.create(model.save("billservice_card"))
                self.connection.commit()
 
            except Exception, e:
                pass   
        
        self.refresh()
    
    def disableCard(self):
        ids=[]
        for index in self.tableWidget.selectedIndexes():
            #print index.column()
            if index.column()>1:
                continue
            i=unicode(self.tableWidget.item(index.row(), 0).text())
            #print i
            
            try:
                #ids.append()
                model=self.connection.get("SELECT * FROM billservice_card WHERE id=%s" % int(i))
                model.disabled=True
                self.connection.create(model.save("billservice_card"))
                self.connection.commit()

            except Exception, e:
                pass        
        
        self.refresh()
        
    def deleteCards(self):
        """
        Р”РѕР±Р°РІРёС‚СЊ РїСЂРѕРІРµСЂРєСѓ-РµСЃР»Рё РєР°СЂС‚РѕС‡РєР° РїСЂРѕРґР°РЅР°, РѕРЅР° РЅРµ РјРѕР¶РµС‚ Р±С‹С‚СЊ СѓРґР°Р»РµРЅР°
        """
        ids=[]
        for index in self.tableWidget.selectedIndexes():
            #print index.column()
            if index.column()>1:
                continue
            i=unicode(self.tableWidget.item(index.row(), 0).text())
            #print i
            
            try:
                #ids.append()
                self.connection.iddelete("billservice_card", int(i))
            except Exception, e:
                pass  
            
        self.connection.commit()    
        self.refresh()     

    def generateCards(self):

        #print model.id
        
        last_series = self.connection.get("SELECT MAX(series) as series FROM billservice_card").series
        if last_series==None:
            last_series=0
        else:
            last_series+=1
        child=AddCards(connection=self.connection, last_series=last_series)
        if child.exec_()==1:
            self.refresh()
            self.fixtures()
        
        
    def refresh(self, widget=None):
        
        sql = """SELECT * FROM billservice_card"""
        if self.checkBox_filter.checkState()==2:
            start_date = self.date_start.dateTime().toPyDateTime()
            end_date = self.date_end.dateTime().toPyDateTime()
            sql+=" WHERE id>0 "
            if unicode(self.comboBox_nominal.currentText())!="":
                sql+=" AND nominal = '%s'" % unicode(self.comboBox_nominal.currentText())
                
            if self.checkBox_activated.checkState() == 2:
                sql+=" AND activated>'%s' and activated<'%s'" % (start_date, end_date)
            
            if self.checkBox_sold.checkState() == 2:
                sql+=" AND sold>'%s' and sold<'%s'" % (start_date, end_date)
                
            if self.checkBox_sold.checkState() == 0 and self.checkBox_activated.checkState() == 0:
                sql+=" AND start_date>'%s' and end_date<'%s'" % (start_date, end_date)
        else:
            sql+=" WHERE sold is Null"
            
        #self.tableWidget.setSortingEnabled(False)

            
        self.tableWidget.clearContents()

        nodes = self.connection.sql(sql)
        self.tableWidget.setRowCount(len(nodes))
        sql+=" ORDER BY id ASC"
        i=0        
        
        for node in nodes:

            self.addrow(node.id, i,0, status = node.disabled, activated=node.activated)
            self.addrow(node.series, i,1, status = node.disabled, activated=node.activated)
            self.addrow(node.nominal, i,2, status = node.disabled, activated=node.activated)
            self.addrow(node.pin, i,3, status = node.disabled, activated=node.activated)
            self.addrow(node.sold, i,4, status = node.disabled, activated=node.activated)
            self.addrow(node.activated, i,5, status = node.disabled, activated=node.activated)
            self.addrow(node.start_date.strftime(self.strftimeFormat), i,6, status = node.disabled, activated=node.activated)
            self.addrow(node.end_date.strftime(self.strftimeFormat), i,7, status = node.disabled, activated=node.activated)
            #self.tableWidget.setRowHeight(i, 17)
            i+=1
            
        self.tableWidget.setColumnHidden(0, False)
        #self.tableWidget.resizeColumnsToContents()
        HeaderUtil.getHeader("cards_frame_header", self.tableWidget)
        #self.tableWidget.setSortingEnabled(True)
        try:
            settings = QtCore.QSettings("Expert Billing", "Expert Billing Client")
            settings.setValue("cards_date_start", QtCore.QVariant(self.date_start.dateTime()))
            settings.setValue("cards_date_end", QtCore.QVariant(self.date_end.dateTime()))
        except Exception, ex:
            print "Transactions settings save error: ", ex


    def saveHeader(self, *args):
        if self.tableWidget.rowCount():
            HeaderUtil.saveHeader("cards_frame_header", self.tableWidget)
            
        
    def getSelectedId(self):
        return int(self.tableWidget.item(self.tableWidget.currentRow(), 0).text())
    

    def addrow(self, value, x, y, status, activated):
        headerItem = QtGui.QTableWidgetItem()
        
        #print 'activated',activated
        if value == None:
            value = ""
        
        headerItem.setText(unicode(value))
        
        if status==True:
            headerItem.setTextColor(QtGui.QColor('#FF0100'))
        
        if y==5:
            headerItem.setBackgroundColor(QtGui.QColor('#dadada'))
        if activated == None and y==0:
            headerItem.setIcon(QtGui.QIcon("images/ok.png"))
        elif activated!=None and y==0:
            headerItem.setIcon(QtGui.QIcon("images/false.png"))
    
        self.tableWidget.setItem(x,y,headerItem)
        

        
    def delNodeLocalAction(self):
        if self.tableWidget.currentRow()==-1:
            self.delConsAction.setDisabled(True)
        else:
            self.delConsAction.setDisabled(False)


    def addNodeLocalAction(self):
        if self.treeWidget.currentItem() is None:
            self.addConsAction.setDisabled(True)
            self.delConsAction.setDisabled(True)
            self.delPeriodAction.setDisabled(True)
        else:
            self.addConsAction.setDisabled(False)
            self.delConsAction.setDisabled(False)
            self.delPeriodAction.setDisabled(False)
            


class CardPreviewDialog(QtGui.QDialog):
    def __init__(self, url):
        
        super(CardPreviewDialog, self).__init__()
        self.setObjectName("CardPreviewDialog")
        #self.filelist=[]
        self.url = url
        self.setObjectName("Dialog")
        self.resize(472, 636)
        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")
        self.webView = QtWebKit.QWebView(self)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.webView.sizePolicy().hasHeightForWidth())
        self.webView.setSizePolicy(sizePolicy)
        self.webView.setUrl(QtCore.QUrl("about:blank"))
        self.webView.setObjectName("webView")
        self.verticalLayout.addWidget(self.webView)
        self.commandLinkButton_print = QtGui.QCommandLinkButton(self)
        self.commandLinkButton_print.setMinimumSize(QtCore.QSize(0, 40))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/printer.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.commandLinkButton_print.setIcon(icon)
        self.commandLinkButton_print.setObjectName("commandLinkButton_print")
        self.verticalLayout.addWidget(self.commandLinkButton_print)
        
        QtCore.QObject.connect(self.commandLinkButton_print, QtCore.SIGNAL("clicked()"), self.printCard)

        self.retranslateUi()
        self.fixtures()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        self.setWindowTitle(QtGui.QApplication.translate("Dialog", "РџСЂРµРґРїСЂРѕСЃРјРѕС‚СЂ", None, QtGui.QApplication.UnicodeUTF8))
        self.commandLinkButton_print.setText(QtGui.QApplication.translate("Dialog", "РџРµС‡Р°С‚Р°С‚СЊ", None, QtGui.QApplication.UnicodeUTF8))
        #self.fixtures()
        #QtCore.QMetaObject.connectSlotsByName()
        
    def fixtures(self):
        lfurl = QtCore.QUrl.fromLocalFile(os.path.abspath(self.url))
        self.webView.load(lfurl)
        #self.webView.settings().setAttribute(QtWebKit.QWebSettings.PrintBackgrounds, True)
        #self.webView.settings().setShouldPrintBackground(True)
        
    def printCard(self):
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        #printer.setResolution(120)
        printer.setPageSize(QtGui.QPrinter.A4)
        dialog = QtGui.QPrintDialog(printer, self)
        dialog.setWindowTitle(self.tr("Print Document"))
        if dialog.exec_() != QtGui.QDialog.Accepted:
            return
        printer.setFullPage(True)
        #printer.setResolution(120)
        #printer.setOutputFileName("lol.pdf")
        #print printer.resolution()
        self.webView.print_(printer)
        
