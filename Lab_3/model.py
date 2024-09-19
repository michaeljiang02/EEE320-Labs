from constants import TABLES, MENU_ITEMS


class Restaurant:

    def __init__(self):
        self.tables = [Table(seats, loc) for seats, loc in TABLES]
        # TODO: uncomment next line
        self.menu_items = [MenuItem(name, price) for name, price in MENU_ITEMS]

class Table:

    def __init__(self, seats, location):
        self.n_seats = seats
        self.location = location
        # TODO: Uncomment next line
        self.orders = [Order() for _ in range(seats)]

    def order_for(self, seat_number):
        return self.orders[seat_number]

    def has_order_for(self, seat_number):
        if not self.orders[seat_number]:
            return False
        return True

class Order:

    def __init__(self):
        self.items = []

    def add_item(self, menu_item):
        self.items.append(OrderItem(menu_item))

    def unordered_items(self):
        return [item for item in self.items if item.ordered == False]

    def place_new_orders(self):
        for item in self.unordered_items():
            item.mark_as_ordered()

    def remove_unordered_items(self):
        for item in self.unordered_items():
            self.items.remove(item)

    def total_cost(self):
        sum = 0
        for item in self.items:
            sum += item.details.price
        return sum

class OrderItem:

    def __init__(self, menu_item):
        self.ordered = False
        self.details = menu_item

    def mark_as_ordered(self):
        self.ordered = True

class MenuItem:

    def __init__(self, name, price):
        self.name = name
        self.price = price
