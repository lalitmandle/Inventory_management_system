#start with product class where we mention all about our product
import datetime
from fpdf import FPDF

# Product class represents product in the inventory.
class Product:
    # Initialize all new product, product_id, name, category, price, quantity
    def __init__(self, product_id, name, category, price, quantity):
        self.product_id = product_id
        self.name = name
        self.category = category
        self.price = price
        self.quantity = quantity

    # Update product quantity   
    def update_quantity(self,quantity):
        self.quantity = quantity
    
    #update product price
    def update_price(self, price):
        self.price = price
    
    #update product category
    def update_category(self,category):
        self.category = category
#Product Inventory manage where add, remove, and update product
class Inventory:

    def __init__(self):
        self.products = {} #empty product dictionary

    def add_product(self,product): #add product to the dictionarinventory
        self.products[product.product_id]  = product
    
    def update_product(self,product_id, **kwargs):#update existing product in the inventory
        if product_id in self.products:
            product = self.products[product_id]
            if 'quantity' in kwargs:
                product.update_quantity(kwargs['quantity'])
            if 'price' in kwargs:
                product.update_price(kwargs['price'])
            if 'category' in kwargs:
                product.update_category(kwargs['category'])

    def remove_product(self,product_id): #remove product from the inventory by product id
        if product_id in self.products:
            del self.products[product_id]

    def view_all_products(self): # see the products are available
        for product_id, product in self.products.items():
            print(f"ID: {product_id}, Name: {product.name}, Category: {product.category}, Price: {product.price}, Quantity: {product.quantity}")


    def find_product(self, product_id): #search product by it's id
        return self.products.get(product_id,None)

#transaction recorde   
class Transaction:
    #Initializes a new transaction by its transaction_id, product_id, quantity and price
    def __init__(self,transaction_id, product_id, quantity, price, date):
        self.transaction_id = transaction_id
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
        self.date = date 

#Sale Recorde
class Sale(Transaction):
    def __init__(self, transaction_id, product_id, quantity, price, date):
        super().__init__(transaction_id, product_id, quantity, price, date)
        self.total_amount = self.calculate_total()
    
    #calculate the total amount of the sale
    def calculate_total(self):
        return self.quantity * self.price

#Return transaction record
class Returns(Transaction):
    #Initializes all required parameters
    def __init__(self, transaction_id, product_id, quantity, price, date, reason):
        super().__init__(transaction_id, product_id, quantity, price, date)
        self.reason = reason

#invoice for counting multiple transactions
class Invoice:
    #Initializes a new invoice
    def __init__(self, invoice_id, transactions, date):
        self.invoice_id = invoice_id
        self.transactions = transactions
        self.total_amount = sum(transaction.total_amount for transaction in transactions)
        self.date = date

    #method for Generates a PDF file for the invoice
    def generate_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial",size=12)
        pdf.cell(200,10,txt=f"Invoice ID: {self.invoice_id}", ln=True,align="L")
        pdf.cell(200,10,txt=f"Date: {self.date}",ln=True,align="L")
        pdf.ln(10)

        for transaction in self.transactions:
            pdf.cell(200,10,txt=f"Product ID: {transaction.product_id}, Quantity: {transaction.quantity}, Price: {transaction.price}, Total: {transaction.total_amount}", ln=True, align="L")
        pdf.cell(200, 10, txt=f"Total Amount: {self.total_amount}", ln=True, align="L")
        pdf.output(f"Invoice_{self.invoice_id}.pdf")
    
    #Lists all invoices for a specific product
    @staticmethod
    def list_invoices_for_product(product_id, invoices):
        return [invoice for invoice in invoices if any(transaction.product_id == product_id for transaction in invoice.transactions)]

#class for manages the entire inventory system including products, sales, returns, and invoices
class InventoryManagementSystem:
    #Initializes the inventory management system with empty inventory, sales, returns, and invoices lists.
    def __init__(self):
        self.inventory = Inventory()
        self.sales = []
        self.returns = []
        self.invoices = []
    
    #Add new product to the inventory
    def add_product(self, product_id, name, category, price, quantity):
        product = Product(product_id, name, category, price, quantity)
        self.inventory.add_product(product)
    
    #Updates existing product in the inventory.
    def update_product(self, product_id, **kwargs):
        self.inventory.update_product(product_id, **kwargs)

    #Remove a product fromthe inventory
    def remove_product(self,product_id):
        self.inventory.remove_product(product_id)
    
    #view all the product in the inventory
    def view_all_products(self):
        self.inventory.view_all_products()

    #Records a sale transaction and updates the inventory.
    def record_sale(self, transaction_id, product_id, quantity, price):
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sale = Sale(transaction_id, product_id, quantity, price, date)
        self.sales.append(sale)
        product = self.inventory.find_product(product_id)
        if product:
            product.update_quantity(product.quantity - quantity)

    #Records a return transaction and updates the inventory.
    def record_return(self, transaction_id, product_id, quantity, price, reason):
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return_transaction = Returns(transaction_id, product_id, quantity, price, date, reason)
        self.returns.append(return_transaction)
        product = self.inventory.find_product(product_id)
        if product:
            product.update_quantity(product.quantity + quantity)

    # Creates an invoice for a list of transactions and generates a PDF.
    def create_invoice(self, invoice_id, transaction_ids):
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        transactions = [sale for sale in self.sales if sale.transaction_id in transaction_ids]
        invoice = Invoice(invoice_id, transactions, date)
        self.invoices.append(invoice)
        invoice.generate_pdf()

    #Lists all invoices for a specific product.
    def list_invoices_for_product(self, product_id):
        return Invoice.list_invoices_for_product(product_id, self.invoices)

    # CLI methods to handle commands
    def cli_add_product(self, args):
        self.add_product(args.product_id, args.name, args.category, args.price, args.quantity)

    def cli_update_product(self, args):
        self.update_product(args.product_id, quantity=args.quantity, price=args.price, category=args.category)

    def cli_remove_product(self, args):
        self.remove_product(args.product_id)

    def cli_view_all_products(self, args):
        self.view_all_products()

    def cli_record_sale(self, args):
        self.record_sale(args.transaction_id, args.product_id, args.quantity, args.price)

    def cli_record_return(self, args):
        self.record_return(args.transaction_id, args.product_id, args.quantity, args.price, args.reason)

    def cli_create_invoice(self, args):
        self.create_invoice(args.invoice_id, args.transaction_ids)


if __name__ == "__main__":
    import argparse

    ims = InventoryManagementSystem()

    parser = argparse.ArgumentParser(description="Advanced Inventory Management System with Invoicing")
    subparsers = parser.add_subparsers()

    # Command to add a new product
    parser_add = subparsers.add_parser("add_product", help="Add a new product")
    parser_add.add_argument("product_id", type=str, help="Product ID")
    parser_add.add_argument("name", type=str, help="Product name")
    parser_add.add_argument("category", type=str, help="Product category")
    parser_add.add_argument("price", type=float, help="Product price")
    parser_add.add_argument("quantity", type=int, help="Product quantity")
    parser_add.set_defaults(func=ims.cli_add_product)

    # Command to update an existing product
    parser_update = subparsers.add_parser("update_product", help="Update an existing product")
    parser_update.add_argument("product_id", type=str, help="Product ID")
    parser_update.add_argument("--quantity", type=int, help="New quantity")
    parser_update.add_argument("--price", type=float, help="New price")
    parser_update.add_argument("--category", type=str, help="New category")
    parser_update.set_defaults(func=ims.cli_update_product)

    # Command to remove an existing product
    parser_remove = subparsers.add_parser("remove_product", help="Remove an existing product")
    parser_remove.add_argument("product_id", type=str, help="Product ID")
    parser_remove.set_defaults(func=ims.cli_remove_product)

    # Command to view all products
    parser_view = subparsers.add_parser("view_all_products", help="View all products")
    parser_view.set_defaults(func=ims.cli_view_all_products)

    # Command to record a sale
    parser_sale = subparsers.add_parser("record_sale", help="Record a sale")
    parser_sale.add_argument("transaction_id", type=str, help="Transaction ID")
    parser_sale.add_argument("product_id", type=str, help="Product ID")
    parser_sale.add_argument("quantity", type=int, help="Quantity sold")
    parser_sale.add_argument("price", type=float, help="Sale price")
    parser_sale.set_defaults(func=ims.cli_record_sale)

    # Command to record a return
    parser_return = subparsers.add_parser("record_return", help="Record a return")
    parser_return.add_argument("transaction_id", type=str, help="Transaction ID")
    parser_return.add_argument("product_id", type=str, help="Product ID")
    parser_return.add_argument("quantity", type=int, help="Quantity returned")
    parser_return.add_argument("price", type=float, help="Return price")
    parser_return.add_argument("reason", type=str, help="Reason for return")
    parser_return.set_defaults(func=ims.cli_record_return)

    # Command to create an invoice
    parser_invoice = subparsers.add_parser("create_invoice", help="Create an invoice")
    parser_invoice.add_argument("invoice_id", type=str, help="Invoice ID")
    parser_invoice.add_argument("transaction_ids", type=str, nargs='+', help="Transaction IDs")
    parser_invoice.set_defaults(func=ims.cli_create_invoice)

    args = parser.parse_args()
    args.func(args)