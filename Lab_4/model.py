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

    def has_any_active_orders(self):
        for order in self.orders:
            for item in order.items:
                if item.has_been_ordered() and not item.has_been_served():
                    return True
        return False

    def has_order_for(self, seat):
        return bool(self.orders[seat].items)

    def order_for(self, seat):
        return self.orders[seat]


class Order:

    def __init__(self):
        self.items = []

    def add_item(self, menu_item):
        item = OrderItem(menu_item)
        self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)

    def place_new_orders(self):
        for item in self.unordered_items():
            item.mark_as_ordered()
            item.state = State.PLACED

    def remove_unordered_items(self):
        for item in self.unordered_items():
            self.items.remove(item)

    def unordered_items(self):
        return [item for item in self.items if not item.has_been_ordered()]

    def total_cost(self):
        return sum((item.details.price for item in self.items))


class OrderItem:

    # TODO: need to represent item state, not just ordered
    def __init__(self, menu_item):
        self.details = menu_item
        self.state = State.REQUESTED

    def next_state(self):
        states = list(State)
        next_state_index = (states.index(self.state) + 1) % len(states)
        self.state = states[next_state_index]

    def has_been_ordered(self):
        return self.state != State.REQUESTED

    def mark_as_ordered(self):
        self.state = State.PLACED

    def has_been_served(self):
        return self.state == State.SERVED

    def can_be_cancelled(self):
        return self.state == State.PLACED or self.state == State.REQUESTED

class State(Enum):

    REQUESTED = 1
    PLACED = 2
    COOKING = 3
    READY = 4
    SERVED = 5

class MenuItem:

    def __init__(self, name, price):
        self.name = name
        self.price = price
