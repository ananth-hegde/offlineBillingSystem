import sys
import types
import os
import time
import PyQt5.QtCore
from PyQt5 import QtGui
from PyQt5.QtGui import QDoubleValidator, QFont, QIntValidator
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QFrame, QHeaderView, QMainWindow
import pickle
from pathlib import Path
import math
from fpdf import FPDF, HTMLMixin
from models import *
QtWidgets.QApplication.setAttribute(PyQt5.QtCore.Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
QtWidgets.QApplication.setAttribute(PyQt5.QtCore.Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons
class MyFPDF(FPDF, HTMLMixin):
    pass
def truncate(number, decimals=0):
    """
    Returns a value truncated to a specific number of decimal places.
    """
    if not isinstance(decimals, int):
        raise TypeError("decimal places must be an integer.")
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more.")
    elif decimals == 0:
        return math.trunc(number)

    factor = 10.0 ** decimals
    return math.trunc(number * factor) / factor

class Number2Words(object):

        def __init__(self):
            '''Initialise the class with useful data'''

            self.wordsDict = {1: 'one', 2: 'two', 3: 'three', 4: 'four', 5: 'five', 6: 'six', 7: 'seven',
                              8: 'eight', 9: 'nine', 10: 'ten', 11: 'eleven', 12: 'twelve', 13: 'thirteen',
                              14: 'fourteen', 15: 'fifteen', 16: 'sixteen', 17: 'seventeen',
                              18: 'eighteen', 19: 'nineteen', 20: 'twenty', 30: 'thirty', 40: 'forty',
                              50: 'fifty', 60: 'sixty', 70: 'seventy', 80: 'eighty', 90: 'ninty' }

            self.powerNameList = ['thousand', 'lac', 'crore']


        def convertNumberToWords(self, number):

            # Check if there is decimal in the number. If Yes process them as paisa part.
            formString = str(number)
            if formString.find('.') != -1:
                withoutDecimal, decimalPart = formString.split('.')
                
                paisaPart =  "{:.2f}".format(round(float(formString), 2)).split('.')[1]
                
                inPaisa = self._formulateDoubleDigitWords(paisaPart)

                formString, formNumber = str(withoutDecimal), int(withoutDecimal)
            else:
                # Process the number part without decimal separately
                formNumber = int(number)
                inPaisa = None

            if not formNumber:
                return 'zero'

            self._validateNumber(formString, formNumber)

            inRupees = self._convertNumberToWords(formString)

            if inPaisa:
                return '%s Rupees and %s paisa only' % (inRupees.title(), inPaisa.title())
            else:
                return '%s Rupees only' % inRupees.title()


        def _validateNumber(self, formString, formNumber):

            assert formString.isdigit()

            # Developed to provide words upto 999999999
            if formNumber > 999999999 or formNumber < 0:
                raise AssertionError('Out Of range')


        def _convertNumberToWords(self, formString):

            MSBs, hundredthPlace, teens = self._getGroupOfNumbers(formString)

            wordsList = self._convertGroupsToWords(MSBs, hundredthPlace, teens)

            return ' '.join(wordsList)


        def _getGroupOfNumbers(self, formString):

            hundredthPlace, teens = formString[-3:-2], formString[-2:]

            msbUnformattedList = list(formString[:-3])

            #---------------------------------------------------------------------#

            MSBs = []
            tempstr = ''
            for num in msbUnformattedList[::-1]:
                tempstr = '%s%s' % (num, tempstr)
                if len(tempstr) == 2:
                    MSBs.insert(0, tempstr)
                    tempstr = ''
            if tempstr:
                MSBs.insert(0, tempstr)

            #---------------------------------------------------------------------#

            return MSBs, hundredthPlace, teens


        def _convertGroupsToWords(self, MSBs, hundredthPlace, teens):

            wordList = []

            #---------------------------------------------------------------------#
            if teens:
                teens = int(teens)
                tensUnitsInWords = self._formulateDoubleDigitWords(teens)
                if tensUnitsInWords:
                    wordList.insert(0, tensUnitsInWords)

            #---------------------------------------------------------------------#
            if hundredthPlace:
                hundredthPlace = int(hundredthPlace)
                if not hundredthPlace:
                    # Might be zero. Ignore.
                    pass
                else:
                    hundredsInWords = '%s hundred' % self.wordsDict[hundredthPlace]
                    wordList.insert(0, hundredsInWords)

            #---------------------------------------------------------------------#
            if MSBs:
                MSBs.reverse()

                for idx, item in enumerate(MSBs):
                    inWords = self._formulateDoubleDigitWords(int(item))
                    if inWords:
                        inWordsWithDenomination = '%s %s' % (inWords, self.powerNameList[idx])
                        wordList.insert(0, inWordsWithDenomination)

            #---------------------------------------------------------------------#
            return wordList


        def _formulateDoubleDigitWords(self, doubleDigit):

            if not int(doubleDigit):
                # Might be zero. Ignore.
                return None
            elif self.wordsDict.__contains__(int(doubleDigit)):
                # Global dict has the key for this number
                tensInWords = self.wordsDict[int(doubleDigit)]
                return tensInWords
            else:
                doubleDigitStr = str(doubleDigit)
                tens, units = int(doubleDigitStr[0])*10, int(doubleDigitStr[1])
                tensUnitsInWords = '%s %s' % (self.wordsDict[tens], self.wordsDict[units])
                return tensUnitsInWords
wGenerator = Number2Words()

class EditStockDialog(QDialog):
    def __init__(self,i,j):
        super(EditStockDialog, self).__init__()
        self.setWindowTitle("Add Stock")
        self.saveBtn = QtWidgets.QPushButton("Save")
        self.cancelBtn = QtWidgets.QPushButton("Cancel")
        self.saveBtn.clicked.connect(lambda: self.accept(j))
        self.cancelBtn.clicked.connect(lambda: self.reject())
        self.hLayout = QtWidgets.QHBoxLayout()
        self.hLayout.addWidget(self.saveBtn)
        self.hLayout.addWidget(self.cancelBtn)
        self.layout = QtWidgets.QVBoxLayout()
        self.nameLabel = QtWidgets.QLabel("Item Name")
        self.nameText = QtWidgets.QLabel(addItems.itemList[j].name)
        self.codeLabel = QtWidgets.QLabel("HSN/ASC")
        self.codeText = QtWidgets.QLabel(addItems.itemList[j].code)
        self.currStockLabel = QtWidgets.QLabel("Current Stock")
        self.currStockText = QtWidgets.QLabel(str(addItems.itemList[j].stock))
        self.supplierLabel = QtWidgets.QLabel("Supplier")
        self.supplierText = QtWidgets.QLineEdit("")
        self.supplierGstinLabel = QtWidgets.QLabel("Supplier GSTIN")
        self.supplierGstinText = QtWidgets.QLineEdit("")
        self.supplierAddressLabel = QtWidgets.QLabel("Supplier Address")
        self.supplierAddressText = QtWidgets.QLineEdit("")
        self.dateLabel = QtWidgets.QLabel("Date of Purchase")
        self.dateText = QtWidgets.QDateEdit(PyQt5.QtCore.QDate.currentDate())
        self.priceLabel = QtWidgets.QLabel("New Price")
        self.priceText = QtWidgets.QLineEdit(str(addItems.itemList[j].price))
        self.priceText.setValidator(QDoubleValidator())
        self.addStockLabel = QtWidgets.QLabel("Add Stock")
        self.addStockText = QtWidgets.QLineEdit("0")
    
        
        self.addStockText.setValidator(QIntValidator())
        self.layout.addWidget(self.nameLabel)
        self.layout.addWidget(self.nameText)
        self.layout.addWidget(self.codeLabel)
        self.layout.addWidget(self.codeText)
        self.layout.addWidget(self.currStockLabel)
        self.layout.addWidget(self.currStockText)
        self.layout.addWidget(self.supplierLabel)
        self.layout.addWidget(self.supplierText)
        self.layout.addWidget(self.supplierGstinLabel)
        self.layout.addWidget(self.supplierGstinText)
        self.layout.addWidget(self.supplierAddressLabel)
        self.layout.addWidget(self.supplierAddressText)
        self.layout.addWidget(self.dateLabel)
        self.layout.addWidget(self.dateText)
        self.layout.addWidget(self.priceLabel)
        self.layout.addWidget(self.priceText)
        self.layout.addWidget(self.addStockLabel)
        self.layout.addWidget(self.addStockText)
        self.layout.addLayout(self.hLayout)
        self.setLayout(self.layout)
    def accept(self,j):
        try:
            stockToAdd = int(self.addStockText.text())
        except ValueError:
            stockToAdd = 0
        try:
            newPrice = float(self.priceText.text())
        except ValueError:
            newPrice = addItems.itemList[j].price
        addItems.itemList[j].stock += stockToAdd
        addItems.itemList[j].price = newPrice
        #Write to stock details
        stockDetailsItem = StockDetailsData(addItems.itemList[j].code,self.supplierText.text(),self.supplierGstinText.text(),self.supplierAddressText.text(),self.dateText.date(),self.addStockText.text(),self.priceText.text())
        addStock.stockDetailsList.append(stockDetailsItem)
        myFile = "stockDetails.pkl"
        with open(myFile,"wb") as output:
            pickle.dump(addStock.stockDetailsList,output,-1)
        self.done(1)
    def reject(self):
        self.done(0)

class EditItemDialog(QDialog):
    def __init__(self,i,j):
        super(EditItemDialog, self).__init__()
        self.setWindowTitle("Edit Item")
        self.saveBtn = QtWidgets.QPushButton("Save")
        self.cancelBtn = QtWidgets.QPushButton("Cancel")
        self.saveBtn.clicked.connect(lambda: self.accept(j))
        self.cancelBtn.clicked.connect(lambda: self.reject(j))
        self.hLayout = QtWidgets.QHBoxLayout()
        self.hLayout.addWidget(self.saveBtn)
        self.hLayout.addWidget(self.cancelBtn)
        self.layout = QtWidgets.QVBoxLayout()
        self.nameLabel = QtWidgets.QLabel("Item Name")
        self.nameText = QtWidgets.QLineEdit(addItems.itemList[j].name)
        self.codeLabel = QtWidgets.QLabel("Item Code")
        self.codeText = QtWidgets.QLineEdit(addItems.itemList[j].code)
        self.priceLabel = QtWidgets.QLabel("Item Price")
        self.priceText = QtWidgets.QLineEdit(str(addItems.itemList[j].price))
        self.cgstLabel = QtWidgets.QLabel("CGST (%)")
        self.cgstText = QtWidgets.QLineEdit(str(addItems.itemList[j].cgst))
        self.sgstLabel = QtWidgets.QLabel("SGST (%)")
        self.sgstText = QtWidgets.QLineEdit(str(addItems.itemList[j].sgst))
        self.igstLabel = QtWidgets.QLabel("IGST (%)")
        self.igstText = QtWidgets.QLineEdit(str(addItems.itemList[j].igst))
        
        self.priceText.setValidator(QDoubleValidator())
        self.igstText.setValidator(QDoubleValidator())
        self.cgstText.setValidator(QDoubleValidator())
        self.sgstText.setValidator(QDoubleValidator())
        self.layout.addWidget(self.nameLabel)
        self.layout.addWidget(self.nameText)
        self.layout.addWidget(self.codeLabel)
        self.layout.addWidget(self.codeText)
        self.layout.addWidget(self.priceLabel)
        self.layout.addWidget(self.priceText)
        self.layout.addWidget(self.cgstLabel)
        self.layout.addWidget(self.cgstText)
        self.layout.addWidget(self.sgstLabel)
        self.layout.addWidget(self.sgstText)
        self.layout.addWidget(self.igstLabel)
        self.layout.addWidget(self.igstText)
        self.layout.addLayout(self.hLayout)
        self.setLayout(self.layout)
    def accept(self,j):
        itemName = self.nameText.text()
        itemCode = self.codeText.text()
        try:
            itemPrice = float(self.priceText.text())
        except ValueError:
            self.dlg = QtWidgets.QMessageBox(3,"Invalid Item!","Item Price cannot be empty!")
            self.dlg.exec_()
            self.done(0)
            return
        try:
            itemIgst = float(self.igstText.text())
        except ValueError:
            itemIgst = 0
        try:
            itemCgst = float(self.cgstText.text())
        except ValueError:
            itemCgst = 0
        try:
            itemSgst = float(self.sgstText.text())
        except ValueError:
            itemSgst = 0
        itemPrice = truncate(itemPrice,2)
        itemIgst = truncate(itemIgst,2)
        itemCgst = truncate(itemCgst,2)
        itemSgst = truncate(itemSgst,2)
        if itemCode=="" or itemName=="":
            self.dlg = QtWidgets.QMessageBox(3,"Invalid Item!","Item Name and Code cannot be empty!")
            self.dlg.exec_()
        elif (itemIgst<0 and itemIgst>100) or (itemCgst<0 and itemCgst>100) or (itemSgst<0 and itemSgst>100):
            self.dlg = QtWidgets.QMessageBox(3,"Invalid Item!","Item IGST, CGST and SGST must be between 0 and 100!")
            self.dlg.exec_()
        else:
            check = 1
            for i in range(len(addItems.itemList)):
                if(i==j):
                    continue
                if addItems.itemList[i].name == itemName or addItems.itemList[i].code == itemCode:
                    check = 0
                    break
            if check == 0:
                self.dlg = QtWidgets.QMessageBox(3,"Repeated Item!","Item has been repeated! Please check code or name!")
                self.dlg.exec_() 
            else:
                addItems.itemList[j].name = itemName
                addItems.itemList[j].code = itemCode
                addItems.itemList[j].price = itemPrice
                addItems.itemList[j].igst = itemIgst
                addItems.itemList[j].cgst = itemCgst
                addItems.itemList[j].sgst = itemSgst
                self.done(1)
    def reject(self,j):
        self.done(0)

class OGMainWindow(QMainWindow):
    def __init__(self):
        super(OGMainWindow, self).__init__()
        self.wid = QtWidgets.QWidget(self)
        self.mainWindow = MainWindow()
        self.setCentralWidget(self.mainWindow)
class MainWindow(QDialog):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("mainWindow.ui", self)
        self.loginBtn.clicked.connect(self.loginClicked)
        self.passwordText.setEchoMode(QtWidgets.QLineEdit.Password)
    def loginClicked(self):
        if(self.usernameText.text()=="admin" and self.passwordText.text()==""):
            widgetStack.setCurrentIndex(widgetStack.currentIndex()+1)
        else:
            self.dlg = QtWidgets.QMessageBox(3,"Invalid Credentials","You have entered invalid username/password. Please try again")
            self.dlg.exec_()

class HomePage(QDialog):
    def __init__(self):
        super(HomePage, self).__init__()
        loadUi("homePage.ui", self)
        self.label.setTextFormat(PyQt5.QtCore.Qt.RichText)
        self.label.setText("<h2><center>"+companyName.upper()+"</center></h2>")
        self.companyBtn.clicked.connect(self.goToCompanyDetails)
        self.addItemsBtn.clicked.connect(self.goToAddItems)
        self.createInvoiceBtn.clicked.connect(self.goToCreateInvoice)
        self.stockDetailsBtn.clicked.connect(self.goToStockDetails)
        self.addStockBtn.clicked.connect(self.goToAddStock)
        self.caReportBtn.clicked.connect(self.goToCaReport)
        self.salesReportBtn.clicked.connect(self.goToSalesReport)
        self.addCustomersBtn.clicked.connect(self.goToAddCustomers)
    def goToAddCustomers(self):
        widgetStack.setCurrentIndex(10)
    def goToSalesReport(self):
        salesReport.reloadPage()
        widgetStack.setCurrentIndex(9)
    def goToCaReport(self):
        widgetStack.setCurrentIndex(8)
    def goToStockDetails(self):
        stockDetails.reloadPage()
        widgetStack.setCurrentIndex(6)
    def goToCompanyDetails(self):
        widgetStack.setCurrentIndex(3)
    def goToCreateInvoice(self):
        createInvoice.loadPage()
        widgetStack.setCurrentIndex(4)
    def goToAddItems(self):
        widgetStack.setCurrentIndex(5)
    def goToAddStock(self):
        addStock.reloadPage()
        widgetStack.setCurrentIndex(7)
    
class CompanyDetails(QDialog):
    def __init__(self):
        super(CompanyDetails, self).__init__()
        loadUi("companyDetails.ui", self)
        self.label.setTextFormat(PyQt5.QtCore.Qt.RichText)
        self.label.setText("<h2><center>"+companyName.upper()+"</center></h2>")
        self.homeBtn.clicked.connect(self.goToHomepage)
        self.addStockBtn.clicked.connect(self.goToAddStock)
        self.addItemsBtn.clicked.connect(self.goToAddItems)
        self.saveDetailsBtn.clicked.connect(self.saveCompanyDetails)
        self.logoBtn.clicked.connect(self.addLogo)
        self.barCodeBtn.clicked.connect(self.addBarCode)
        self.createInvoiceBtn.clicked.connect(self.goToCreateInvoice)
        self.stockDetailsBtn.clicked.connect(self.goToStockDetails)
        self.companyContact1Text.setValidator(QIntValidator())
        self.companyContact2Text.setValidator(QIntValidator())
        self.companyContact1Text.setMaxLength(10)
        self.companyContact2Text.setMaxLength(10)
        self.companyDetailsList= CompanyDetailsData("","","","","","","","","","")
        self.caReportBtn.clicked.connect(self.goToCaReport)
        self.salesReportBtn.clicked.connect(self.goToSalesReport)
        self.addCustomersBtn.clicked.connect(self.goToAddCustomers)
        self.loadData()
    def goToAddCustomers(self):
        widgetStack.setCurrentIndex(10)
    def goToSalesReport(self):
        salesReport.reloadPage()
        widgetStack.setCurrentIndex(9)
    def goToCaReport(self):
        widgetStack.setCurrentIndex(8)
        

    def addLogo(self):

        fileName = QtWidgets.QFileDialog.getOpenFileName(self,"Select Logo Image", "", "Image Files (*.png *.jpg *.bmp)")
        if(fileName):
            fileName = fileName[0]
            self.companyLogoText.setText(fileName)
            
    def addBarCode(self):
        fileName = QtWidgets.QFileDialog.getOpenFileName(self,"Select Bar Code Image", "", "Image Files (*.png *.jpg *.bmp)")
        if(fileName):
            fileName = fileName[0]
            self.companyBarCodeText.setText(fileName)
            
    def goToStockDetails(self):
        stockDetails.reloadPage()
        widgetStack.setCurrentIndex(6)
    def loadData(self):
        myFile = Path("companyDetails.pkl")
        try:
            myPath = myFile.resolve(strict=True)
        except FileNotFoundError:
            self.companyNameText.clear()
            self.companyAddressText.clear()
            self.companyContact1Text.clear()
            self.companyContact2Text.clear()
            self.companyBankNameText.clear()
            self.companyIfscCodeText.clear()
            self.companyUpiIdText.clear()
            self.companyAcNumberText.clear()

        else:
            try:
                with open(myFile,"rb") as input:
                    self.companyDetailsList = pickle.load(input)
            except EOFError:
                self.companyDetailsList = CompanyDetailsData('','','','','','','','','','')
            self.companyNameText.setText(self.companyDetailsList.name)
            self.companyAddressText.setText(self.companyDetailsList.address)
            self.companyContact1Text.setText(self.companyDetailsList.contact1)
            self.companyContact2Text.setText(self.companyDetailsList.contact2)
            self.companyBankNameText.setText(self.companyDetailsList.bankName)
            self.companyIfscCodeText.setText(self.companyDetailsList.ifscCode)
            self.companyUpiIdText.setText(self.companyDetailsList.upiId)
            self.companyAcNumberText.setText(self.companyDetailsList.acNumber)
            self.companyLogoText.setText(self.companyDetailsList.logo)
            self.companyBarCodeText.setText(self.companyDetailsList.barCode)
    def saveCompanyDetails(self):
        cName = self.companyNameText.text()
        global companyName
        companyName = cName
        cAddress = self.companyAddressText.text()
        cContact1 = self.companyContact1Text.text()
        cContact2 = self.companyContact2Text.text()
        cBankName = self.companyBankNameText.text()
        cIfscCode = self.companyIfscCodeText.text()
        cAcNumber = self.companyAcNumberText.text()
        cLogo = self.companyLogoText.text()
        cBarCode = self.companyBarCodeText.text()
        cUpiId = self.companyUpiIdText.text()
        self.companyDetailsList = CompanyDetailsData(cName,cAddress,cContact1,cContact2,cBankName,cIfscCode,cUpiId,cAcNumber,cLogo,cBarCode)
        fileName = "companyDetails.pkl"
        with open(fileName,"wb") as output:
            pickle.dump(self.companyDetailsList,output,-1)
        self.dlg = QtWidgets.QMessageBox(1,"Successfully Saved!","Successfully Saved Data!")
        self.dlg.exec_() 
    def goToHomepage(self):
        widgetStack.setCurrentIndex(2)
    def goToCreateInvoice(self):
        createInvoice.loadPage()
        widgetStack.setCurrentIndex(4)
    def goToAddItems(self):
        widgetStack.setCurrentIndex(5)
    def goToAddStock(self):
        addStock.reloadPage()
        widgetStack.setCurrentIndex(7)

class CreateInvoice(QDialog):
    def __init__(self):
        super(CreateInvoice, self).__init__()
        loadUi("createInvoice.ui", self)   
        self.label.setTextFormat(PyQt5.QtCore.Qt.RichText)
        self.label.setText("<h2><center>"+companyName.upper()+"</center></h2>")
        self.homeBtn.clicked.connect(self.goToHomepage)
        self.addStockBtn.clicked.connect(self.goToAddStock)
        self.companyBtn.clicked.connect(self.goToCompanyDetails)
        self.addItemsBtn.clicked.connect(self.goToAddItems)
        self.clearInvoiceBtn.clicked.connect(self.clearInvoice)
        self.productNameText.setMaxLength(10)
        self.addToInvoiceBtn.clicked.connect(self.addItemToInvoice)
        self.printBtn.clicked.connect(self.printInvoices)
        
        self.qtyText.setValidator(QIntValidator())
        self.qtyText.setMaxLength(4)
        self.unitText.setMaxLength(6)
        self.otherChargesText.setValidator(QDoubleValidator())
        self.otherChargesText.textChanged.connect(self.reloadPage)
        self.itemNameList.currentIndexChanged.connect(self.getItemDetails)
        self.invoiceItemList = []
        self.grossTotal = 0.00
        self.customerNameList.currentIndexChanged.connect(self.getCustomerDetails)
        self.stockDetailsBtn.clicked.connect(self.goToStockDetails)
        self.caReportBtn.clicked.connect(self.goToCaReport)
        self.salesReportBtn.clicked.connect(self.goToSalesReport)
        self.addCustomersBtn.clicked.connect(self.goToAddCustomers)
    def goToAddCustomers(self):
        widgetStack.setCurrentIndex(10)
    def printInvoices(self):
        dir = "invoices\\"
        if not os.path.exists(dir):
            os.makedirs(dir)
        if(self.invoiceNumberText.text().strip()==""):
            onlyfiles = next(os.walk(dir))[2]
            invoiceNumber = int((len(onlyfiles))+1)
        else:
            invoiceNumber = int(self.invoiceNumberText.text().strip())
        self.printInvoice("Original",invoiceNumber)
    def goToSalesReport(self):
        salesReport.reloadPage()
        widgetStack.setCurrentIndex(9)
    def goToCaReport(self):
        widgetStack.setCurrentIndex(8)
    def goToStockDetails(self):
        stockDetails.reloadPage()
        widgetStack.setCurrentIndex(6)
    def goToAddStock(self):
        addStock.reloadPage()
        addStock.reloadPage()
        widgetStack.setCurrentIndex(7)
    def printInvoice(self,invoiceType,invoiceNumber):
        
        pdf = MyFPDF()
        #First page
        pdf.add_page()
        pdf.rect(5, 5, 202, 287, 'D')
        
        try:
            
            pdf.image(companyDetails.companyDetailsList.logo,w=20,h=20)
            pdf.image(companyDetails.companyDetailsList.barCode,10,75,w=35,h=35)
        except FileNotFoundError:
            self.dlg = QtWidgets.QMessageBox(3,"Logo or barcode not found!","Please Update Logo and bar code!")
            self.dlg.exec_()
        except RuntimeError:
            self.dlg = QtWidgets.QMessageBox(3,"Unsupported image","Unsupported logo or barcode format.")
            self.dlg.exec_()
        pdf.set_font('Arial','B',20)
        #Cell(width , height , text , border , end line , [align] )#
        pdf.cell(71 ,10,'',0,0)
        pdf.cell(59 ,5,invoiceType+' Invoice',0,0)
        pdf.cell(59 ,10,'',0,1)
        pdf.set_font('Arial','B',15)
        pdf.cell(71 ,5,companyDetails.companyDetailsList.name,0,0)
        pdf.cell(59 ,5,'',0,0)
        pdf.cell(59 ,5,'Details',0,1)
        pdf.set_font('Arial','',10)
        pdf.cell(130 ,5,companyDetails.companyDetailsList.address,0,0)
        pdf.cell(25 ,5,'Bill To :',0,0)
        if(self.customerNameList.currentText()!="New Customer"):
            customerName = self.customerNameList.currentText()
        else:
            customerName = self.customerNameText.text()
        pdf.cell(34 ,5,customerName,0,1)
        pdf.cell(130 ,5,companyDetails.companyDetailsList.contact1+"/"+companyDetails.companyDetailsList.contact2,0,0)
        pdf.cell(25 ,5,'Contact:',0,0)
        pdf.cell(34 ,5,self.mobileText.text(),0,1)
        pdf.cell(130 ,5,"Bank Name: "+companyDetails.companyDetailsList.bankName,0,0)
        pdf.cell(25 ,5,'Contact 2:',0,0)
        pdf.cell(34 ,5,self.phoneText.text(),0,1)
        pdf.cell(130 ,5,"A/C Number: "+companyDetails.companyDetailsList.acNumber,0,0)
        pdf.cell(25 ,5,'Invoice No:',0,0)
        pdf.cell(34 ,5,str(invoiceNumber),0,1)
        pdf.cell(130 ,5,"IFSC Code: "+companyDetails.companyDetailsList.ifscCode,0,0)
        pdf.cell(25 ,5,'Date:',0,0)
        dateOfInvoice = self.dateText.date()
        pdf.cell(34 ,5,dateOfInvoice.toString(),0,1)
        pdf.cell(130 ,5,"UPI ID: "+companyDetails.companyDetailsList.upiId,0,0)
        pdf.cell(25 ,5,'Vehicle No:',0,0)
        pdf.cell(34 ,5,self.lrNumberText.text(),0,1)
        pdf.cell(130 ,5,'',0,0)
        pdf.cell(25 ,5,'ADD:',0,0)
        pdf.multi_cell(34 ,5,self.addText.text(),0,1)
        pdf.cell(130 ,5,'',0,0)
        pdf.cell(25 ,5,'Transport:',0,0)
        pdf.cell(34 ,5,self.transportText.text(),0,1)
        pdf.cell(130 ,5,'',0,0)
        pdf.cell(25 ,5,'GST No:',0,0)
        pdf.cell(34 ,5,self.gstNumberText.text(),0,1)
        pdf.cell(130 ,5,'',0,0)
        pdf.cell(25 ,5,'P.O. No:',0,0)
        pdf.cell(34 ,5,self.pqNumberText.text(),0,1)
        
        pdf.set_font('Arial','B',15)
        pdf.cell(59 ,5,'',0,0)
        pdf.set_font('Arial','B',10)
        pdf.cell(189 ,10,'',0,1)
        pdf.cell(50 ,10,'',0,1)
        pdf.set_font('Arial','B',10)
        #Heading Of the table
        pdf.cell(7 ,6,'Sl',1,0,'C')
        pdf.cell(20 ,6,'Name',1,0,'C')
        pdf.cell(17 ,6,'Price',1,0,'C')
        pdf.cell(17 ,6,'Qty',1,0,'C')
        pdf.cell(23 ,6,'Amount',1,0,'C')
        pdf.cell(20 ,6,'CGST',1,0,'C')
        pdf.cell(10 ,6,'%',1,0,'C')
        pdf.cell(20 ,6,'SGST',1,0,'C')
        pdf.cell(10 ,6,'%',1,0,'C')
        pdf.cell(20 ,6,'IGST',1,0,'C')
        pdf.cell(10 ,6,'%',1,0,'C')
        pdf.cell(22 ,6,'Total',1,1,'C')
        pdf.set_font('Arial','',10)
        for i in range(len(self.invoiceItemList)):
            top = pdf.y
            offset = pdf.x + 7
            pdf.multi_cell(7 ,6,str(i+1)+"\n"+" ","LR",0)
            pdf.y = top
            pdf.x = offset
            top = pdf.y
            offset = pdf.x + 20
            
            pdf.multi_cell(20 ,6,self.invoiceItemList[i].name,"LR",0)
            pdf.y = top
            pdf.x = offset
            top = pdf.y
            offset = pdf.x + 17
            pdf.multi_cell(17 ,6,str(self.invoiceItemList[i].price)+"\n"+" ","LR",0)
            pdf.y = top
            pdf.x = offset
            top = pdf.y
            offset = pdf.x + 17
            pdf.multi_cell(17 ,6,str(self.tableView.item(i,2).text())+"\n"+" ","LR",0,'R')
            pdf.y = top
            pdf.x = offset
            top = pdf.y
            offset = pdf.x + 23
            pdf.multi_cell(23 ,6,"{:.2f}".format(self.invoiceItemList[i].subAmount)+"\n"+" ","LR",0,'R')
            pdf.y = top
            pdf.x = offset
            top = pdf.y
            offset = pdf.x + 20
            pdf.multi_cell(20 ,6,"{:.2f}".format(self.invoiceItemList[i].cgstAmount)+"\n"+" ","LR",0,'R')
            pdf.y = top
            pdf.x = offset
            top = pdf.y
            offset = pdf.x + 10
            pdf.multi_cell(10 ,6,"{:.2f}".format(self.invoiceItemList[i].cgst)+"\n"+" ","LR",0,'R')
            pdf.y = top
            pdf.x = offset
            top = pdf.y
            offset = pdf.x + 20
            pdf.multi_cell(20 ,6,"{:.2f}".format(self.invoiceItemList[i].sgstAmount)+"\n"+" ","LR",0,'R')
            pdf.y = top
            pdf.x = offset
            top = pdf.y
            offset = pdf.x + 10
            pdf.multi_cell(10 ,6,"{:.2f}".format(self.invoiceItemList[i].sgst)+"\n"+" ","LR",0,'R')
            pdf.y = top
            pdf.x = offset
            top = pdf.y
            offset = pdf.x + 20
            pdf.multi_cell(20 ,6,"{:.2f}".format(self.invoiceItemList[i].igstAmount)+"\n"+" ","LR",0,'R')
            pdf.y = top
            pdf.x = offset
            top = pdf.y
            offset = pdf.x + 10
            pdf.multi_cell(10 ,6,"{:.2f}".format(self.invoiceItemList[i].igst)+"\n"+" ","LR",0,'R')
            pdf.y = top
            pdf.x = offset
            top = pdf.y
            offset = pdf.x + 22
            pdf.multi_cell(22 ,6,"{:.2f}".format(self.invoiceItemList[i].totalAmount)+"\n"+" ","LR",1,'R')
            #add data to sales details
            if(invoiceType=="Original"):
                salesDetailsItem = SalesDetailsData(dateOfInvoice,customerName,self.invoiceItemList[i].qty,self.invoiceItemList[i].name,str(invoiceNumber),"{:.2f}".format(self.invoiceItemList[i].totalAmount))
                salesReport.salesList.append(salesDetailsItem)
                myFile = "salesReport.pkl"
                with open(myFile,"wb") as output:
                    pickle.dump(salesReport.salesList,output,-1)
                #Remove stock from items and rewrite itemDetails.pkl
                    for j in range(len(addItems.itemList)):
                        if addItems.itemList[j].name == self.invoiceItemList[i].name:
                            addItems.itemList[j].stock -= salesDetailsItem.quantity
                            fileName = "itemDetails.pkl"
                            with open(fileName,"wb") as output:
                                pickle.dump(addItems.itemList,output,-1)
        if(len(self.invoiceItemList)%20==0):
            pass
        else:
            for i in range(10-len(self.invoiceItemList)%10):
                pdf.cell(7 ,6," ","LR",0)
                pdf.cell(20 ,6," ","LR",0)
                pdf.cell(17 ,6," ","LR",0)
                pdf.cell(17 ,6," ","LR",0)
                pdf.cell(23 ,6," ","LR",0)
                pdf.cell(20 ,6," ","LR",0)
                pdf.cell(10 ,6," ","LR",0)
                pdf.cell(20 ,6," ","LR",0)
                pdf.cell(10 ,6," ","LR",0)
                pdf.cell(20 ,6," ","LR",0)
                pdf.cell(10 ,6," ","LR",0)
                pdf.cell(22 ,6,"","LR",0)
                pdf.ln()
        
        if(self.otherChargesText.text().strip()==""):
            otherCharges = 0
        else:
            otherCharges = float(self.otherChargesText.text())
        pdf.cell(144 ,6,'',0,0)
        pdf.cell(30 ,6,'Other Charges',0,0)
        pdf.cell(22 ,6,"{:.2f}".format(otherCharges),1,1,'L')
        pdf.cell(144 ,6,'',0,0)
        pdf.cell(30 ,6,'Grand Total',0,0)
        
        pdf.cell(22 ,6,"{:.2f}".format(self.grossTotal),1,1,'R')
        pdf.cell(40,6,"Amount in words: ")
        pdf.cell(120,6,self.amountInWordsText.text())
        pdf.cell(40,6,"")
        pdf.ln(12)
        pdf.cell(40,6,"________________________")
        pdf.ln(5)
        pdf.cell(40,6,"Authorized Signature")
        dir = "invoices\\"
        pdfName = str(invoiceType)+str(invoiceNumber)
        print(pdfName)
        outputPath = str(dir)+pdfName+".pdf"
        outputPath = r""+outputPath
        if(invoiceType=="Original"):
            invoiceToAdd = invoiceDetailsData(invoiceNumber,dateOfInvoice,self.grossTotal)
            caReport.invoicesList.append(invoiceToAdd)
        with open("invoiceDetails.pkl","wb") as output:
            pickle.dump(caReport.invoicesList,output,-1)
        pdf.output(outputPath, 'F')
        
        os.startfile(outputPath)
    def getCustomerDetails(self):
        index = self.customerNameList.currentIndex()
        if(index>=len(addCustomers.customersList) or index == -1):
            self.mobileText.setText("")
            self.gstNumberText.setText("")
            self.addText.setText("")
        else:
            customer = addCustomers.customersList[index]
            self.mobileText.setText(str(customer.contact))
            self.gstNumberText.setText(str(customer.gstin))
            self.addText.setText(str(customer.address))
    def getItemDetails(self):
        index = self.itemNameList.currentIndex()
        if(index>=len(addItems.itemList) or index==-1):
            self.priceText.setText("")
            self.cgstText.setText("0")
            self.sgstText.setText("0")
            self.igstText.setText("0")
        else:
            item = addItems.itemList[index]
            self.priceText.setText(str(item.price))
            self.cgstText.setText(str(item.cgst))
            self.sgstText.setText(str(item.sgst))
            self.igstText.setText(str(item.igst))
    def clearInvoice(self):
        self.invoiceItemList = []
        self.reloadPage()
    def loadPage(self):
        self.itemNameList.clear()
        for i in addItems.itemList:
            self.itemNameList.addItem(i.name)
        self.itemNameList.addItem("New Item")
        self.customerNameList.clear()
        for i in addCustomers.customersList:
            self.customerNameList.addItem(i.name)
        self.customerNameList.addItem("New Customer")
        self.qtyText.setValidator(QIntValidator())
        self.reloadPage()
    def reloadPage(self):
        self.dateText.setDate(PyQt5.QtCore.QDate.currentDate())
        self.grossTotal = 0
        self.tableView.setRowCount(len(self.invoiceItemList)+1)
        self.tableView.setColumnCount(8)
        self.tableView.setHorizontalHeaderLabels(['Name','Price (INR)','Qty.','Sub Amount (INR)','CGST (INR)','SGST (INR)','IGST (INR)','Total Amount (INR)'])
        self.tableView.clearContents()
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableView.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        i=0
        for i in range(len(self.invoiceItemList)):
            item1 = QtWidgets.QTableWidgetItem(self.invoiceItemList[i].name)
            self.tableView.setItem(i,0,item1)
            item3 = QtWidgets.QTableWidgetItem(str(self.invoiceItemList[i].price))
            self.tableView.setItem(i,1,item3)
            item3 = QtWidgets.QTableWidgetItem(str(self.invoiceItemList[i].qty)+" "+self.invoiceItemList[i].unit)
            self.tableView.setItem(i,2,item3)
            item3 = QtWidgets.QTableWidgetItem("{:.2f}".format(self.invoiceItemList[i].subAmount))
            self.tableView.setItem(i,3,item3)
            item3 = QtWidgets.QTableWidgetItem("{:.2f}".format(self.invoiceItemList[i].cgstAmount))
            self.tableView.setItem(i,4,item3)
            item3 = QtWidgets.QTableWidgetItem("{:.2f}".format(self.invoiceItemList[i].sgstAmount))
            self.tableView.setItem(i,5,item3)
            item3 = QtWidgets.QTableWidgetItem("{:.2f}".format(self.invoiceItemList[i].igstAmount))
            self.tableView.setItem(i,6,item3)
            item3 = QtWidgets.QTableWidgetItem("{:.2f}".format(self.invoiceItemList[i].totalAmount))
            self.tableView.setItem(i,7,item3)
            self.grossTotal +=self.invoiceItemList[i].totalAmount
        i+=1
        item3 = QtWidgets.QTableWidgetItem("Total Amount")
        self.tableView.setItem(i,6,item3)
        
        if(not self.otherChargesText.text().strip()==""):
            charges = float(self.otherChargesText.text().strip())
        else: 
            charges = 0
        self.grossTotal = self.grossTotal+charges
        item3 = QtWidgets.QTableWidgetItem("{:.2f}".format(self.grossTotal))
        self.tableView.setItem(i,7,item3)
        
        self.amountInWordsText.setText(wGenerator.convertNumberToWords(self.grossTotal))
       
    def addItemToInvoice(self):
        if(self.itemNameList.currentIndex()>=len(addItems.itemList)):
            itemToAdd = itemDetailsData(self.productNameText.text(),self.priceText.text(),"",self.igstText.text(),self.cgstText.text(),self.sgstText.text())
        else:
            itemToAdd = addItems.itemList[self.itemNameList.currentIndex()]
        if(self.qtyText.text()=="" or int(self.qtyText.text()) == 0):
            self.dlg = QtWidgets.QMessageBox(3,"Invalid Addition!","Item Qty cannot be empty or 0!")
            self.dlg.exec_()
        else:
            qty = int(self.qtyText.text())
            if(itemToAdd.stock<qty and itemToAdd.code!=""):
                self.dlg = QtWidgets.QMessageBox(3,"Invalid Addition!","Not Enough Stock!")
                self.dlg.exec_()
                return
            try:
                subAmount = float(self.priceText.text())*qty

                cgstAmount = subAmount*float(self.cgstText.text())/100.0
                sgstAmount = subAmount*float(self.sgstText.text())/100.0
                igstAmount = subAmount*float(self.igstText.text())/100.0
                totalAmount = subAmount
                subAmount = subAmount-cgstAmount-igstAmount-sgstAmount
                
                invoiceItemToAdd = InvoiceItemData(itemToAdd.name,itemToAdd.code,self.unitText.text(),float(self.priceText.text()),qty,subAmount,cgstAmount,float(self.cgstText.text()),sgstAmount,float(self.sgstText.text()),igstAmount,float(self.igstText.text()),totalAmount)
                self.invoiceItemList.append(invoiceItemToAdd)
            except:
                self.dlg = QtWidgets.QMessageBox(3,"Invalid Details","Please check price and gst amounts!")
                self.dlg.exec_()
            self.reloadPage()
   
    def goToHomepage(self):
        widgetStack.setCurrentIndex(2)
    def goToCompanyDetails(self):
        widgetStack.setCurrentIndex(3)
    def goToCreateInvoice(self):
        createInvoice.loadPage()
        widgetStack.setCurrentIndex(4)
    def goToAddItems(self):
        widgetStack.setCurrentIndex(5)
    def goToAddStock(self):
        addStock.reloadPage()
        addStock.reloadPage()
        widgetStack.setCurrentIndex(7)
class AddItems(QDialog):
    def __init__(self):
        super(AddItems, self).__init__()
        loadUi("addItems.ui", self)
        self.label.setTextFormat(PyQt5.QtCore.Qt.RichText)
        self.label.setText("<h2><center>"+companyName.upper()+"</center></h2>")
        self.homeBtn.clicked.connect(self.goToHomepage)
        self.addStockBtn.clicked.connect(self.goToAddStock)
        self.createInvoiceBtn.clicked.connect(self.goToCreateInvoice)
        self.companyBtn.clicked.connect(self.goToCompanyDetails)
        self.addItemBtn.clicked.connect(self.addItem)
        self.itemPriceText.setValidator(QDoubleValidator())
        self.itemNameText.setMaxLength(10)
        self.igstText.setValidator(QDoubleValidator())
        self.cgstText.setValidator(QDoubleValidator())
        self.sgstText.setValidator(QDoubleValidator())
        self.caReportBtn.clicked.connect(self.goToCaReport)
        self.stockDetailsBtn.clicked.connect(self.goToStockDetails)
        self.salesReportBtn.clicked.connect(self.goToSalesReport)
        self.addCustomersBtn.clicked.connect(self.goToAddCustomers)
        self.loadPage()
    def goToAddCustomers(self):
        widgetStack.setCurrentIndex(10)
    def goToSalesReport(self):
        salesReport.reloadPage()
        widgetStack.setCurrentIndex(9)
    def goToCaReport(self):
        widgetStack.setCurrentIndex(8)
    def loadPage(self):
        myFile = Path("itemDetails.pkl")
        try:
            myPath = myFile.resolve(strict=True)
        except FileNotFoundError:
            self.itemList = []
        else:
            try:
                with open(myFile,"rb") as input:
                    self.itemList = pickle.load(input)
            except EOFError:
                self.itemList = []
        #clear table
        self.tableView.clearContents()
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableView.setRowCount(len(self.itemList))
        self.tableView.setColumnCount(8)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableView.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableView.setHorizontalHeaderLabels(['Name','HSN/ASC','Price','CGST','SGST','IGST','Edit','Delete'])
        for i in range(len(self.itemList)):
            item2 = QtWidgets.QTableWidgetItem(self.itemList[i].name)
            self.tableView.setItem(i,0,item2)
            item3 = QtWidgets.QTableWidgetItem(str(self.itemList[i].code))
            self.tableView.setItem(i,1,item3)
            item3 = QtWidgets.QTableWidgetItem(str(self.itemList[i].price))
            self.tableView.setItem(i,2,item3)
            item3 = QtWidgets.QTableWidgetItem(str(self.itemList[i].cgst))
            self.tableView.setItem(i,3,item3)
            item3 = QtWidgets.QTableWidgetItem(str(self.itemList[i].sgst))
            self.tableView.setItem(i,4,item3)
            item3 = QtWidgets.QTableWidgetItem(str(self.itemList[i].igst))
            self.tableView.setItem(i,5,item3)
            self.editBtn = QtWidgets.QPushButton('Edit')
            self.editBtn.clicked.connect(self.editItem)
            self.tableView.setCellWidget(i,6,self.editBtn)
            self.deleteBtn = QtWidgets.QPushButton('Delete')
            self.deleteBtn.clicked.connect(self.deleteItem)
            self.tableView.setCellWidget(i,7,self.deleteBtn)
    def goToStockDetails(self):
        stockDetails.reloadPage()
        widgetStack.setCurrentIndex(6)
    def editItem(self,i):
        button = self.sender()
        index = self.tableView.indexAt(button.pos())
        if index.isValid():
            i = index.row()
            dlg = EditItemDialog(self,i)
            dlg.exec_()
        fileName = "itemDetails.pkl"
        with open(fileName,"wb") as output:
            pickle.dump(self.itemList,output,-1)
        self.loadPage()
    def deleteItem(self,i):
        button = self.sender()
        index = self.tableView.indexAt(button.pos())
        if index.isValid():
            i = index.row()
            del self.itemList[i]
        fileName = "itemDetails.pkl"
        with open(fileName,"wb") as output:
            pickle.dump(self.itemList,output,-1)
        self.dlg = QtWidgets.QMessageBox(1,"Successfully Deleted!","Successfully Deleted Item!")
        self.dlg.exec_()
        self.loadPage()
    def goToHomepage(self):
        widgetStack.setCurrentIndex(2)
    def goToCompanyDetails(self):
        widgetStack.setCurrentIndex(3)
    def goToCreateInvoice(self):
        createInvoice.loadPage()
        widgetStack.setCurrentIndex(4)
    def addItem(self):
        itemCode = self.itemCodeText.text().strip()
        itemName = self.itemNameText.text().strip()
        try:
            itemPrice = float(self.itemPriceText.text())
        except ValueError:
            self.dlg = QtWidgets.QMessageBox(3,"Invalid Item!","Item Price cannot be empty!")
            self.dlg.exec_()
            return
        try:
            itemIgst = float(self.igstText.text())
        except ValueError:
            itemIgst = 0.00
        try:
            itemCgst = float(self.cgstText.text())
        except ValueError:
            itemCgst = 0.00
        try:
            itemSgst = float(self.sgstText.text())
        except ValueError:
            itemSgst = 0.00
        itemPrice = truncate(itemPrice,2)
        itemIgst = truncate(itemIgst,2)
        itemCgst = truncate(itemCgst,2)
        itemSgst = truncate(itemSgst,2)
        if itemCode=="" or itemName=="":
            self.dlg = QtWidgets.QMessageBox(3,"Invalid Item!","Item Name and Code cannot be empty!")
            self.dlg.exec_()
        elif (itemIgst<0 and itemIgst>100) or (itemCgst<0 and itemCgst>100) or (itemSgst<0 and itemSgst>100):
            self.dlg = QtWidgets.QMessageBox(3,"Invalid Item!","Item IGST, CGST and SGST must be between 0 and 100!")
            self.dlg.exec_()
        else:
            itemToAdd = itemDetailsData(itemName,itemPrice,itemCode,itemIgst,itemCgst,itemSgst)
            check = 1
            for i in self.itemList:
                if i.name == itemName or i.code == itemCode:
                    check = 0
                    break
            if check == 0:
                self.dlg = QtWidgets.QMessageBox(3,"Repeated Item!","Item has been repeated! Please check code or name!")
                self.dlg.exec_()
            else:
                self.itemList.append(itemToAdd)
                myFile = Path("itemDetails.pkl")
                with open(myFile,"wb") as output:
                    pickle.dump(self.itemList,output,-1)
                self.dlg = QtWidgets.QMessageBox(1,"Successfully Added!","Successfully Added Item!")
                self.dlg.exec_()
                self.loadPage()
    def goToAddStock(self):
        addStock.reloadPage()
        addStock.reloadPage()
        widgetStack.setCurrentIndex(7)   
class StockDetails(QDialog):
    def __init__(self):
        super(StockDetails, self).__init__()
        loadUi("stockDetails.ui", self)
        self.label.setTextFormat(PyQt5.QtCore.Qt.RichText)
        self.label.setText("<h2><center>"+companyName.upper()+"</center></h2>")
        self.homeBtn.clicked.connect(self.goToHomepage)
        self.addStockBtn.clicked.connect(self.goToAddStock)
        self.addItemsBtn.clicked.connect(self.goToAddItems)
        self.companyBtn.clicked.connect(self.goToCompanyDetails)
        self.createInvoiceBtn.clicked.connect(self.goToCreateInvoice)
        self.applyBtn.clicked.connect(self.applyDetails)
        myFile = "stockDetails.pkl"
        if not os.path.exists(myFile):
            open(myFile,"wb")
            self.stockDetailsList = []
        else:
            try:
                with open(myFile,"rb") as input:
                    self.stockDetailsList = pickle.load(input)
            except EOFError:
                self.stockDetailsList = []
        self.itemNameList.clear()
        for i in addItems.itemList:
            self.itemNameList.addItem(i.name)
        self.fromDate.setDate(PyQt5.QtCore.QDate.currentDate())
        self.toDate.setDate(PyQt5.QtCore.QDate.currentDate())
        self.stockDetailsList = []
        self.caReportBtn.clicked.connect(self.goToCaReport)
        self.salesReportBtn.clicked.connect(self.goToSalesReport)
        self.addCustomersBtn.clicked.connect(self.goToAddCustomers)
        self.reloadPage()
    def goToAddCustomers(self):
        widgetStack.setCurrentIndex(10)
    def goToSalesReport(self):
        salesReport.reloadPage()
        widgetStack.setCurrentIndex(9)

    def applyDetails(self):
        myFile = "stockDetails.pkl"
        if not os.path.exists(myFile):
            open(myFile,"wb")
            self.stockDetailsList = []
        else:
            try:
                with open(myFile,"rb") as input:
                    self.stockDetailsList = pickle.load(input)
            except EOFError:
                self.stockDetailsList = []
        self.itemsToDisplay = []
        dateFrom = self.fromDate.date()
        dateTo = self.toDate.date()
        if(len(addItems.itemList)==0):
            return
        itemCode = addItems.itemList[self.itemNameList.currentIndex()].code
        
        for item in self.stockDetailsList:
            
            if(item.date>=dateFrom and item.date<=dateTo and item.code == itemCode):
                
                self.itemsToDisplay.append(item)
        self.tableView.setRowCount(len(self.itemsToDisplay))
        self.tableView.setColumnCount(6)
        self.tableView.setHorizontalHeaderLabels(['Supplier Name','Supplier Address','Supplier GSTIN','Date','Quantity Added','Price'])
        self.tableView.clearContents()
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableView.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        for i in range(len(self.itemsToDisplay)):
            item1 = QtWidgets.QTableWidgetItem(self.itemsToDisplay[i].supplier)
            self.tableView.setItem(i,0,item1)
            item1 = QtWidgets.QTableWidgetItem(self.itemsToDisplay[i].supplierAddress)
            self.tableView.setItem(i,1,item1)
            item1 = QtWidgets.QTableWidgetItem(self.itemsToDisplay[i].supplierGstin)
            self.tableView.setItem(i,2,item1)
            item1 = QtWidgets.QTableWidgetItem(self.itemsToDisplay[i].date.toString("dd MMM yyyy"))
            self.tableView.setItem(i,3,item1)
            item1 = QtWidgets.QTableWidgetItem(self.itemsToDisplay[i].qtyAdded)
            self.tableView.setItem(i,4,item1)
            item1 = QtWidgets.QTableWidgetItem(self.itemsToDisplay[i].newPrice)
            self.tableView.setItem(i,5,item1)
    def goToCaReport(self):
        widgetStack.setCurrentIndex(8)
    def goToHomepage(self):
        widgetStack.setCurrentIndex(2)
    def reloadPage(self):
        self.itemNameList.clear()
        for i in addItems.itemList:
            self.itemNameList.addItem(i.name)
        
        
    def goToHomepage(self):
        widgetStack.setCurrentIndex(2)
    def goToCompanyDetails(self):
        widgetStack.setCurrentIndex(3)
    def goToCreateInvoice(self):
        createInvoice.loadPage()
        widgetStack.setCurrentIndex(4)
    def goToAddItems(self):
        widgetStack.setCurrentIndex(5)
    def goToAddStock(self):
        addStock.reloadPage()
        addStock.reloadPage()
        widgetStack.setCurrentIndex(7)

class AddStock(QDialog):
    def __init__(self):
        super(AddStock, self).__init__()
        loadUi("addStock.ui", self)
        self.label.setTextFormat(PyQt5.QtCore.Qt.RichText)
        self.label.setText("<h2><center>"+companyName.upper()+"</center></h2>")
        self.homeBtn.clicked.connect(self.goToHomepage)
        self.companyBtn.clicked.connect(self.goToCompanyDetails)
        self.addItemsBtn.clicked.connect(self.goToAddItems)
        self.createInvoiceBtn.clicked.connect(self.goToCreateInvoice)
        self.stockDetailsBtn.clicked.connect(self.goToStockDetails)
        self.stockDetailsList = []
        self.caReportBtn.clicked.connect(self.goToCaReport)
        self.salesReportBtn.clicked.connect(self.goToSalesReport)
        self.addCustomersBtn.clicked.connect(self.goToAddCustomers)
        self.reloadPage()
    def goToAddCustomers(self):
        widgetStack.setCurrentIndex(10)
    def goToSalesReport(self):
        salesReport.reloadPage()
        widgetStack.setCurrentIndex(9)
    def goToCaReport(self):
        widgetStack.setCurrentIndex(8)
    def reloadPage(self):
        
        myFile = "stockDetails.pkl"
        if not os.path.exists(myFile):
            open(myFile,"wb")
        else:
            try:
                with open(myFile,"rb") as input:
                    self.stockDetailsList = pickle.load(input)
            except EOFError:
                self.stockDetailsList = []
        self.tableView.setRowCount(len(addItems.itemList))#
        self.tableView.setColumnCount(4)
        self.tableView.setHorizontalHeaderLabels(['Name','HSN/ASC','Stock','Add Stock'])
        self.tableView.clearContents()
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableView.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(len(addItems.itemList)):
            item1 = QtWidgets.QTableWidgetItem(addItems.itemList[i].name)
            self.tableView.setItem(i,0,item1)
            item2 = QtWidgets.QTableWidgetItem(addItems.itemList[i].code)
            self.tableView.setItem(i,1,item2)
            item3 = QtWidgets.QTableWidgetItem(str(addItems.itemList[i].stock))
            self.tableView.setItem(i,2,item3)
            self.btn_sell = QtWidgets.QPushButton('Add')
            self.btn_sell.clicked.connect(self.handleButtonClicked)
            self.tableView.setCellWidget(i,3,self.btn_sell)
        
       
    def handleButtonClicked(self):
        
        button = self.sender()
        index = self.tableView.indexAt(button.pos())
        if index.isValid():
            indexToAdd = index.row()
            dlg = EditStockDialog(self,indexToAdd)
            dlg.exec_()
            fileName = "itemDetails.pkl"
            with open(fileName,"wb") as output:
                pickle.dump(addItems.itemList,output,-1)
            addItems.loadPage()
            self.reloadPage()
    def goToHomepage(self):
        widgetStack.setCurrentIndex(2)
    def goToCompanyDetails(self):
        widgetStack.setCurrentIndex(3)
    def goToCreateInvoice(self):
        createInvoice.loadPage()
        widgetStack.setCurrentIndex(4)
    def goToAddItems(self):
        widgetStack.setCurrentIndex(5)
    def goToStockDetails(self):
        stockDetails.reloadPage()
        widgetStack.setCurrentIndex(6)

class CaReport(QDialog):
    def __init__(self):
        super(CaReport, self).__init__()
        loadUi("caReport.ui", self)
        self.label.setTextFormat(PyQt5.QtCore.Qt.RichText)
        self.label.setText("<h2><center>"+companyName.upper()+"</center></h2>")
        self.homeBtn.clicked.connect(self.goToHomepage)
        self.companyBtn.clicked.connect(self.goToCompanyDetails)
        self.addItemsBtn.clicked.connect(self.goToAddItems)
        self.addStockBtn.clicked.connect(self.goToAddStock)
        self.createInvoiceBtn.clicked.connect(self.goToCreateInvoice)
        self.stockDetailsBtn.clicked.connect(self.goToStockDetails)
        self.applyBtn.clicked.connect(self.loadPage)
        self.invoicesList = []
        self.fromDate.setDate(PyQt5.QtCore.QDate.currentDate())
        self.toDate.setDate(PyQt5.QtCore.QDate.currentDate())
        
        myFile = "invoiceDetails.pkl"
        if not os.path.exists(myFile):
            open(myFile,"wb")
            self.invoicesList = []
        else:
            try:
                with open(myFile,"rb") as input:
                    self.invoicesList = pickle.load(input)
            except EOFError:
                self.invoicesList = []
        self.salesReportBtn.clicked.connect(self.goToSalesReport)
        self.addCustomersBtn.clicked.connect(self.goToAddCustomers)
        self.loadPage()
    def goToAddCustomers(self):
        widgetStack.setCurrentIndex(10)
    def goToSalesReport(self):
        salesReport.reloadPage()
        widgetStack.setCurrentIndex(9)
    def loadPage(self):
        
        myFile = "invoiceDetails.pkl"
        if not os.path.exists(myFile):
            open(myFile,"wb")
            self.invoicesList = []
        else:
            try:
                with open(myFile,"rb") as input:
                    self.invoicesList = pickle.load(input)
            except EOFError:
                self.invoicesList = []
        dateFrom = self.fromDate.date()
        dateTo = self.toDate.date()
        gstPercentage = self.gstPercentageList.currentText()
        self.itemsToDisplay = []
        for item in (self.invoicesList):
            if(item.invoiceDate>=dateFrom and item.invoiceDate<=dateTo):
                self.itemsToDisplay.append(item)
        self.tableView.setRowCount(len(self.itemsToDisplay)+2)
        self.tableView.setColumnCount(3)
        self.tableView.setHorizontalHeaderLabels(['Invoice Number','Invoice Date','Total Amount'])
        self.tableView.clearContents()
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableView.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        netTotalAmount = 0
        i=0
        for i in range(len(self.itemsToDisplay)):
            item1 = QtWidgets.QTableWidgetItem(str(self.itemsToDisplay[i].invoiceNumber))
            self.tableView.setItem(i,0,item1)
            item1 = QtWidgets.QTableWidgetItem(self.itemsToDisplay[i].invoiceDate.toString("dd MMM yyyy"))
            self.tableView.setItem(i,1,item1)
            item1 = QtWidgets.QTableWidgetItem(str(self.itemsToDisplay[i].invoiceAmount))
            self.tableView.setItem(i,2,item1)
            netTotalAmount+= float(self.itemsToDisplay[i].invoiceAmount)
            
        i+=1
        item1 = QtWidgets.QTableWidgetItem("Grand Total")
        self.tableView.setItem(i,1,item1)
        item1 = QtWidgets.QTableWidgetItem("{:.2f}".format(netTotalAmount))
        self.tableView.setItem(i,2,item1)
        i+=1
        dataToDisplay = gstPercentage+ "% applied"
        item1 = QtWidgets.QTableWidgetItem(dataToDisplay)
        self.tableView.setItem(i,1,item1)
        gstAmount = netTotalAmount*float(gstPercentage)/100.0
        item1 = QtWidgets.QTableWidgetItem("{:.2f}".format(gstAmount))
        self.tableView.setItem(i,2,item1)
    def goToStockDetails(self):
        stockDetails.reloadPage()
        widgetStack.setCurrentIndex(6)
    def goToHomepage(self):
        widgetStack.setCurrentIndex(2)
    def goToCompanyDetails(self):
        widgetStack.setCurrentIndex(3)
    def goToCreateInvoice(self):
        createInvoice.loadPage()
        widgetStack.setCurrentIndex(4)
    def goToAddItems(self):
        widgetStack.setCurrentIndex(5)
    def goToAddStock(self):
        addStock.reloadPage()
        widgetStack.setCurrentIndex(7)

myFile = "itemDetails.pkl"
if(not os.path.exists(myFile)):
    fo = open(myFile,"wb")
    fo.close()
myFile = "invoiceDetails.pkl"
if(not os.path.exists(myFile)):
    fo = open(myFile,"wb")
    fo.close()
myFile = "stockDetails.pkl"
if(not os.path.exists(myFile)):
    fo = open(myFile,"wb")
    fo.close()
myFile = "companyDetails.pkl"
if(not os.path.exists(myFile)):
    fo = open(myFile,"wb")
    fo.close()
myFile = "customerDetails.pkl"
if(not os.path.exists(myFile)):
    fo = open(myFile,"wb")
    fo.close()
myFile = "salesDetails.pkl"
if(not os.path.exists(myFile)):
    fo = open(myFile,"wb")
    fo.close()
#Get company Details: 
try:
    companyDetailsList = CompanyDetailsData('','','','','','','','','','')
    with open("companyDetails.pkl","rb") as input:
        companyDetailsList = pickle.load(input)
        companyName = companyDetailsList.name
except EOFError:
    companyName = "Company Name"


class SalesReport(QDialog):
    def __init__(self):
        super(SalesReport, self).__init__()
        loadUi("salesReport.ui", self)
        self.label.setText("<h2><center>"+companyName.upper()+"</center></h2>")
        self.homeBtn.clicked.connect(self.goToHomepage)
        self.companyBtn.clicked.connect(self.goToCompanyDetails)
        self.addItemsBtn.clicked.connect(self.goToAddItems)
        self.addStockBtn.clicked.connect(self.goToAddStock)
        self.stockDetailsBtn.clicked.connect(self.goToStockDetails)
        self.createInvoiceBtn.clicked.connect(self.goToCreateInvoice)
        self.stockDetailsBtn.clicked.connect(self.goToStockDetails)
        self.caReportBtn.clicked.connect(self.goToCaReport)
        self.applyBtn.clicked.connect(self.applyDetails)
        self.fromDate.setDate(PyQt5.QtCore.QDate.currentDate())
        self.toDate.setDate(PyQt5.QtCore.QDate.currentDate())
        myFile = "salesReport.pkl"
        try:
            with open(myFile,"rb") as input:
                self.salesList = pickle.load(input)
        except EOFError:
            self.salesList = []
        except FileNotFoundError:
            open(myFile,"wb")
            self.salesList = []
        self.addCustomersBtn.clicked.connect(self.goToAddCustomers)
        self.reloadPage()
    def goToAddCustomers(self):
        widgetStack.setCurrentIndex(10)
    def reloadPage(self):
        self.itemNameList.clear()
        for i in addItems.itemList:
            self.itemNameList.addItem(i.name)
    def applyDetails(self):
        myFile = "salesReport.pkl"
        if not os.path.exists(myFile):
            open(myFile,"wb")
            self.salesList = []
        else:
            try:
                with open(myFile,"rb") as input:
                    self.salesList = pickle.load(input)
            except EOFError:
                self.salesList = []
        self.itemsToDisplay = []
        dateFrom = self.fromDate.date()
        dateTo = self.toDate.date()
        if(len(addItems.itemList)==0):
            return
        itemName = addItems.itemList[self.itemNameList.currentIndex()].name
        
        for item in self.salesList:
            print(item.dateOfSale,item.itemCode,itemName,item.quantity)
            print(dateFrom,dateTo)
            if(item.dateOfSale>=dateFrom and item.dateOfSale<=dateTo and item.itemCode == itemName):
                self.itemsToDisplay.append(item)
        print(len(self.itemsToDisplay))
        self.tableView.setRowCount(len(self.itemsToDisplay))
        self.tableView.setColumnCount(5)
        self.tableView.setHorizontalHeaderLabels(['Date','Invoice Number','Customer Name','Quantity Sold','Grand Total'])
        self.tableView.clearContents()
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableView.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(len(self.itemsToDisplay)):
            item1 = QtWidgets.QTableWidgetItem(self.itemsToDisplay[i].dateOfSale.toString())
            self.tableView.setItem(i,0,item1)
            item1 = QtWidgets.QTableWidgetItem(str(self.itemsToDisplay[i].invoiceNumber))
            self.tableView.setItem(i,1,item1)
            item1 = QtWidgets.QTableWidgetItem(str(self.itemsToDisplay[i].customerName))
            self.tableView.setItem(i,2,item1)
            item1 = QtWidgets.QTableWidgetItem(str(self.itemsToDisplay[i].quantity))
            self.tableView.setItem(i,3,item1)
            item1 = QtWidgets.QTableWidgetItem(str(self.itemsToDisplay[i].total))
            self.tableView.setItem(i,4,item1)
            # print(salesListItem.itemCode)
            # print(salesListItem.dateOfSale)
            # print(salesListItem.quantity)
    def goToHomepage(self):
        widgetStack.setCurrentIndex(2)
    def goToCaReport(self):
        widgetStack.setCurrentIndex(8)
    def goToStockDetails(self):
        stockDetails.reloadPage()
        widgetStack.setCurrentIndex(6)
    def goToCompanyDetails(self):
        widgetStack.setCurrentIndex(3)
    def goToCreateInvoice(self):
        createInvoice.loadPage()
        widgetStack.setCurrentIndex(4)
    def goToAddItems(self):
        widgetStack.setCurrentIndex(5)
    def goToAddStock(self):
        addStock.reloadPage()
        widgetStack.setCurrentIndex(7)


class AddCustomers(QDialog):
    def __init__(self):
        super(AddCustomers, self).__init__()
        loadUi("addCustomers.ui", self)
        self.homeBtn.clicked.connect(self.goToHomepage)
        self.addCustomerBtn.clicked.connect(self.addCustomer)
        myFile = Path("customerDetails.pkl")
        try:
            myPath = myFile.resolve(strict=True)
        except FileNotFoundError:
            open(myFile,"wb")
            self.customersList = []
        else:
            try:
                with open(myFile,"rb") as input:
                    self.customersList = pickle.load(input)
            except EOFError:
                self.customersList = []
        self.loadPage()
        self.companyBtn.clicked.connect(self.goToCompanyDetails)
        self.addItemsBtn.clicked.connect(self.goToAddItems)
        self.createInvoiceBtn.clicked.connect(self.goToCreateInvoice)
        self.stockDetailsBtn.clicked.connect(self.goToStockDetails)
        self.addStockBtn.clicked.connect(self.goToAddStock)
        self.caReportBtn.clicked.connect(self.goToCaReport)
        self.salesReportBtn.clicked.connect(self.goToSalesReport)
    
    def goToSalesReport(self):
        salesReport.reloadPage()
        widgetStack.setCurrentIndex(9)
    def goToCaReport(self):
        widgetStack.setCurrentIndex(8)
    def goToStockDetails(self):
        stockDetails.reloadPage()
        widgetStack.setCurrentIndex(6)
    def goToCompanyDetails(self):
        widgetStack.setCurrentIndex(3)
    def goToCreateInvoice(self):
        createInvoice.loadPage()
        widgetStack.setCurrentIndex(4)
    def goToAddItems(self):
        widgetStack.setCurrentIndex(5)
    def goToAddStock(self):
        addStock.reloadPage()
        widgetStack.setCurrentIndex(7)
    def addCustomer(self):
        customerName = self.customerNameText.text()
        customerAddress = self.customerAddressText.text()
        stateCode = self.stateCodeText.text()
        state = self.stateText.text()
        contactNumber = self.contactNumberText.text()
        gstin = self.gstinText.text()
        email = self.emailText.text()
        customerToAdd = CustomerDetailsData(customerName,customerAddress,stateCode,state,contactNumber,gstin,email)
        self.customersList.append(customerToAdd)
        myFile = "customerDetails.pkl"
        with open(myFile,"wb") as output:
            pickle.dump(self.customersList,output,-1)
        self.loadPage()
    def goToHomepage(self):
        widgetStack.setCurrentIndex(2)
    def loadPage(self):
        myFile = Path("customerDetails.pkl")
        try:
            myPath = myFile.resolve(strict=True)
        except FileNotFoundError:
            open(myFile,"wb")
            self.customersList = []
        else:
            try:
                with open(myFile,"rb") as input:
                    self.customersList = pickle.load(input)
            except EOFError:
                self.customersList = []
        #clear table
        self.tableView.clearContents()
        self.tableView.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.tableView.setRowCount(len(self.customersList))
        self.tableView.setColumnCount(8)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tableView.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tableView.setHorizontalHeaderLabels(['Name','Address','State Code','State','Contact Number','GSTIN','Email Address','Delete'])
        for i in range(len(self.customersList)):
            item2 = QtWidgets.QTableWidgetItem(self.customersList[i].name)
            self.tableView.setItem(i,0,item2)
            item3 = QtWidgets.QTableWidgetItem(str(self.customersList[i].address))
            self.tableView.setItem(i,1,item3)
            item3 = QtWidgets.QTableWidgetItem(str(self.customersList[i].stateCode))
            self.tableView.setItem(i,2,item3)
            item3 = QtWidgets.QTableWidgetItem(str(self.customersList[i].state))
            self.tableView.setItem(i,3,item3)
            item3 = QtWidgets.QTableWidgetItem(str(self.customersList[i].contact))
            self.tableView.setItem(i,4,item3)
            item3 = QtWidgets.QTableWidgetItem(str(self.customersList[i].gstin))
            self.tableView.setItem(i,5,item3)
            item3 = QtWidgets.QTableWidgetItem(str(self.customersList[i].email))
            self.tableView.setItem(i,6,item3)
            self.deleteBtn = QtWidgets.QPushButton('Delete')
            self.deleteBtn.clicked.connect(self.deleteCustomer)
            self.tableView.setCellWidget(i,7,self.deleteBtn)
    def deleteCustomer(self):
        button = self.sender()
        index = self.tableView.indexAt(button.pos())
        if index.isValid():
            i = index.row()
            del self.customersList[i]
        fileName = "customerDetails.pkl"
        with open(fileName,"wb") as output:
            pickle.dump(self.customersList,output,-1)
        self.dlg = QtWidgets.QMessageBox(1,"Successfully Deleted!","Successfully Deleted Customer!")
        self.dlg.exec_()
        self.loadPage()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    widgetStack = QtWidgets.QStackedWidget()
    ogMainWindow = OGMainWindow()
    mainWindow = MainWindow()
    homePage = HomePage()
    companyDetails = CompanyDetails()
    createInvoice = CreateInvoice()
    addItems = AddItems()
    stockDetails = StockDetails()
    addStock = AddStock()
    caReport = CaReport()
    salesReport = SalesReport()
    addCustomers = AddCustomers()
    widgetStack.addWidget(ogMainWindow) #0
    widgetStack.addWidget(mainWindow) #1
    widgetStack.addWidget(homePage) #2
    widgetStack.addWidget(companyDetails)  #3
    widgetStack.addWidget(createInvoice) #4
    widgetStack.addWidget(addItems) #5
    widgetStack.addWidget(stockDetails) #6 
    widgetStack.addWidget(addStock) #7
    widgetStack.addWidget(caReport) #8
    widgetStack.addWidget(salesReport) #9
    widgetStack.addWidget(addCustomers) #10
    widgetStack.setCurrentIndex(1)
    widgetStack.showMaximized()
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting")
else:
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    widgetStack = QtWidgets.QStackedWidget()
    ogMainWindow = OGMainWindow()
    mainWindow = MainWindow()
    homePage = HomePage()
    widgetStack.addWidget(ogMainWindow) 
    widgetStack.addWidget(mainWindow) 
    widgetStack.addWidget(homePage) 