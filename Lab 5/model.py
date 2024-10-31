"""
Provides the model classes representing the state of the OORMS
system.

Submitting lab group: [your names here]
Submission date: [date here]

Original code by EEE320 instructors.
"""

from constants import TABLES, MENU_ITEMS
from enum import Enum

class Restaurant:

    def __init__(self):
        super().__init__()
        self.tables = [Table(seats, loc) for seats, loc in TABLES]
        self.menu_items = [MenuItem(name, price) for name, price in MENU_ITEMS]
        self.views = []

    def add_view(self, view):
        self.views.append(view)

    def notify_views(self):
        for view in self.views:
            view.update()


class Table:

    def __init__(self, seats, location):
        self.n_seats = seats
        self.location = location
        self.orders = [Order() for _ in range(seats)]
        self.bills = []

    def has_any_active_orders(self):
        for order in self.orders:
            if order.state == State.PLACED or order.state == State.SELECTED:
                return True
        return False

    def has_selected_orders(self):
        for order in self.orders:
            if order.state == State.SELECTED:
                return True
        return False

    def select(self,seat_number):
        if self.has_order_for(seat_number):
            self.orders[seat_number].select()

    def new_bill(self):
        bill=Bill()
        for order in self.orders:
            if order.state == State.SELECTED:
                for items in order.items:
                    bill.add_item(items)
                order.delete_all_items()
                order.unselect()
                order.state = State.EMPTY
        if not bill.is_empty():
            self.bills.append(bill)

    def has_order_for(self, seat):
        return bool(self.orders[seat].items)

    def selected(self, seat):
        return self.orders[seat].state == State.SELECTED

    def order_for(self, seat):
        return self.orders[seat]

    def reset_table(self):
        del self.orders
        self.orders = [Order() for _ in range(self.n_seats)]


class Order:
    def __init__(self):
        self.items = []
        #self.on_bill=False
        self.selected=False
        self.state = State.EMPTY

    def select(self):
        self.state = State.SELECTED

    def unselect(self):
        self.state = State.PLACED

    def add_item(self, menu_item):
        item = OrderItem(menu_item)
        self.items.append(item)

    def remove_item(self, order_item):
        self.items.remove(order_item)

    def place_new_orders(self):
        for item in self.unordered_items():
            item.mark_as_ordered()
        self.state = State.PLACED

    def remove_unordered_items(self):
        for item in self.unordered_items():
            self.items.remove(item)

    def unordered_items(self):
        return [item for item in self.items if not item.has_been_ordered()]

    def total_cost(self):
        return sum((item.details.price for item in self.items))

    def delete_all_items(self):
        del self.items
        self.items=[]

    def is_empty(self):
        return not self.items




class Bill:
    def __init__(self):
        self.items=[]
        self.total=0

    def is_empty(self):
        return not self.items

    def add_item(self,menu_item):
        self.items.append(menu_item)
        self.total += menu_item.details.price


class OrderItem:

    # TODO: need to represent item state, not just 'ordered', all methods will need modifying
    def __init__(self, menu_item):
        self.details = menu_item
        self.ordered = False

    def mark_as_ordered(self):
        self.ordered = True

    def has_been_ordered(self):
        return self.ordered

    def has_been_served(self):
        # TODO: correct implementation based on item state
        return False

    def can_be_cancelled(self):
        # TODO: correct implementation based on item state
        return True

class State(Enum):

    EMPTY = 0
    PLACED = 1
    SELECTED = 2


class MenuItem:

    def __init__(self, name, price):
        self.name = name
        self.price = price
