
class InvoiceItemData():
    def __init__(self,name,code,unit,price,qty,subAmount,cgstAmount,cgst,sgstAmount,sgst,igstAmount,igst,totalAmount):
        self.name = name
        self.code = code
        self.price = price
        self.unit = unit
        self.qty = qty
        self.subAmount = subAmount
        self.cgstAmount = cgstAmount
        self.cgst = cgst
        self.sgstAmount = sgstAmount
        self.sgst = sgst
        self.igstAmount = igstAmount
        self.igst = igst
        self.totalAmount = totalAmount

class CompanyDetailsData():
    def __init__(self,name,address,contact1,contact2,bankName,ifscCode,upiId,acNumber,logo,barCode):
        self.name = name
        self.address = address
        self.contact1 = contact1
        self.contact2 = contact2
        self.bankName = bankName
        self.ifscCode = ifscCode
        self.upiId = upiId
        self.acNumber = acNumber
        self.barCode = barCode
        self.logo = logo
    
class itemDetailsData():
    def __init__(self,name,price,code,igst,cgst,sgst):
        self.name = name
        self.price = price
        self.code = code
        self.igst = igst
        self.cgst = cgst
        self.sgst = sgst
        self.stock = 0

class CustomerDetailsData():
    def __init__(self,name,address,stateCode,state,contact,gstin,email):
        self.name = name
        self.address = address
        self.stateCode = stateCode
        self.state = state
        self.contact = contact
        self.gstin = gstin
        self.email = email

class SalesDetailsData():
    def __init__(self,dateOfSale,customerName,qty,itemCode,invoiceNumber,total):
        self.itemCode = itemCode
        self.customerName = customerName
        self.quantity = qty
        self.dateOfSale = dateOfSale
        self.invoiceNumber = invoiceNumber
        self.total = total
class invoiceDetailsData():
    def __init__(self,invoiceNumber,invoiceDate,totalAmount):
        self.invoiceNumber = invoiceNumber
        self.invoiceDate = invoiceDate
        self.invoiceAmount = totalAmount

class StockDetailsData():
    def __init__(self,code,supplier,supplierGstin,supplierAddress,date,qtyAdded,newPrice):
        self.code = code
        self.supplier = supplier
        self.supplierGstin = supplierGstin
        self.supplierAddress = supplierAddress
        self.date = date
        self.qtyAdded = qtyAdded
        self.newPrice = newPrice
