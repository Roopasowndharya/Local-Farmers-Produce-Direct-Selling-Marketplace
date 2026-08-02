class Product:
    def __init__(self,product_id,name,category,price,quantity,farmer_id):
        self.product_id=product_id
        self.name=name
        self.category=category
        self.price=price
        self.quantity=quantity
        self.farmer_id=farmer_id
    def display_product(self):
        print("Product Id:",self.product_id)
        print("Name:",self.name)
        print("Category:",self.category)
        print("Price:",self.price)
        print("Quantity:",self.quantity)
        print("Farmer ID:",self.farmer_id)