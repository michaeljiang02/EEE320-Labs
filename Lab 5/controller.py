"""
Provides the controller layer for the OORMS system.

Submitting lab group: [your names here]
Submission date: [date here]

Original code by EEE320 instructors.
"""
from model import State

class Controller:

    def __init__(self, view, restaurant):
        self.view = view
        self.restaurant = restaurant


class RestaurantController(Controller):

    def create_ui(self):
        self.view.create_restaurant_ui()

    def table_touched(self, table_number):
        self.view.set_controller(TableController(self.view, self.restaurant,
                                                 self.restaurant.tables[table_number]))
        self.view.update()


class TableController(Controller):

    def __init__(self, view, restaurant, table):
        super().__init__(view, restaurant)
        self.table = table

    def create_ui(self):
        self.view.create_table_ui(self.table)

    def seat_touched(self, seat_number):
        self.view.set_controller(OrderController(self.view, self.restaurant, self.table, seat_number))
        self.view.update()

    def make_bills(self):
        self.view.set_controller(BillController(self.view, self.restaurant, self.table))
        self.view.update()

    def done(self):
        self.view.set_controller(RestaurantController(self.view, self.restaurant))
        self.view.update()


class BillController(Controller):

    def __init__(self, view, restaurant, table):
        super().__init__(view, restaurant)
        self.table = table

    def create_ui(self):
        self.view.create_bill_ui(self.table)

    def select(self, seat_number):
        self.table.select(seat_number)
        self.view.update()

    def unselect(self, seat_number):
        self.table.unselect(seat_number)
        self.view.update()

    def create_bill(self):
        self.table.create_bill()
        self.view.update()

    def cancel_bills(self):
        self.table.cancel_bills()
        self.view.set_controller(TableController(self.view, self.restaurant, self.table))
        self.view.update()

    def print_bills(self,printer):
        printer.print(f'Set up bills for table {self.restaurant.tables.index(self.table)}'.center(40))
        bill_count=0
        for bill in self.table.bills:
            bill_count += 1
            printer.print("\n")
            printer.print(f'Bill #{bill_count}\n'.center(40))
            for item in bill.items:
                printer.print(f'{item.details.name}:      {item.details.price:.2f}  '.rjust(40))
            printer.print("=" * 40)
            printer.print(f'Total:      {bill.total:.2f}  '.rjust(40))
            printer.print("-" * 40)
        self.view.set_controller(RestaurantController(self.view, self.restaurant))
        self.table.reset_table()
        self.view.update()



class OrderController(Controller):
    def __init__(self, view, restaurant, table, seat_number):
        super().__init__(view, restaurant)
        self.table = table
        self.order = self.table.order_for(seat_number)

    def create_ui(self):
        self.view.create_order_ui(self.order)

    def add_item(self, menu_item):
        self.order.add_item(menu_item)
        self.restaurant.notify_views()

    def remove(self, order_item):
        self.order.remove_item(order_item)
        self.restaurant.notify_views()

    def update_order(self):
        self.order.place_new_orders()
        self.view.set_controller(TableController(self.view, self.restaurant, self.table))
        self.restaurant.notify_views()

    def cancel_changes(self):
        self.order.remove_unordered_items()
        self.view.set_controller(TableController(self.view, self.restaurant, self.table))
        self.restaurant.notify_views()
