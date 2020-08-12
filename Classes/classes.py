class Person():
    """Created Person to serialize them later"""
    def __init__(self, name, pan):
        self.name = name
        self.pan = pan
        self.holdings = 0
        self.investments = {}


class Investment:
    """Created Investment to serialize them later"""

    def __init__(self):
        self.timestamp = dt.datetime.now()


class Stock(Investment):

    def __init__(self, company_name, quantity, price=None):
        super().__init__()
        self.name = company_name
        self.quantity = quantity
        if not price:
            self.price = self.get_price()
        else:
            self.price = price

    def get_price(self):
        pass