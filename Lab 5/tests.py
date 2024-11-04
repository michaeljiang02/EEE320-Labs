"""
Test cases for the OORMS system.

Submitting lab group: [your names here]
Submission date: [date here]

Original code by EEE320 instructors.
"""

import unittest
from enum import Enum, auto
from controller import RestaurantController, TableController, OrderController, BillController
from model import Restaurant, OrderItem, Bill, State


class UI(Enum):
    restaurant = auto()
    table = auto()
    order = auto()
    bill = auto()


class ServerViewMock:

    def __init__(self, restaurant):
        self.controller = None
        self.last_UI_created = None
        self.restaurant = restaurant
        restaurant.add_view(self)
        self.set_controller(RestaurantController(self, self.restaurant))

    def set_controller(self, controller):
        self.controller = controller
        self.controller.create_ui()

    def create_restaurant_ui(self):
        self.last_UI_created = UI.restaurant

    def create_table_ui(self, table):
        self.last_UI_created = (UI.table, table)

    def create_order_ui(self, order):
        self.last_UI_created = (UI.order, order)

    def create_bill_ui(self, table):
        self.last_UI_created = UI.bill

    def update(self):
        self.controller.create_ui()


class OORMSTestCase(unittest.TestCase):

    def setUp(self):
        self.restaurant = Restaurant()
        self.view = ServerViewMock(self.restaurant)

    def test_initial_state(self):
        self.assertEqual(UI.restaurant, self.view.last_UI_created)
        self.assertIsInstance(self.view.controller, RestaurantController)

    def test_restaurant_controller_touch_table(self):
        self.view.controller.table_touched(3)
        self.assertIsInstance(self.view.controller, TableController)
        self.assertEqual(self.view.controller.table, self.restaurant.tables[3])
        self.assertEqual((UI.table, self.restaurant.tables[3]), self.view.last_UI_created)

    def test_table_controller_done(self):
        self.view.controller.table_touched(5)
        self.view.controller.done()
        self.assertIsInstance(self.view.controller, RestaurantController)
        self.assertEqual(UI.restaurant, self.view.last_UI_created)

    def test_table_controller_seat_touched(self):
        self.view.controller.table_touched(4)
        self.view.controller.seat_touched(0)
        self.assertIsInstance(self.view.controller, OrderController)
        self.assertEqual(self.view.controller.table, self.restaurant.tables[4])
        the_order = self.restaurant.tables[4].order_for(0)
        self.assertEqual(self.view.controller.order, the_order)
        self.assertEqual((UI.order, the_order), self.view.last_UI_created)

    def order_an_item(self):
        """
        Starting from the restaurant UI, orders one instance of item 0
        for table 2, seat 4
        """
        self.view.controller.table_touched(2)
        self.view.controller.seat_touched(4)
        the_menu_item = self.restaurant.menu_items[0]
        self.view.last_UI_created = None
        self.view.controller.add_item(the_menu_item)
        return self.restaurant.tables[2].order_for(4), the_menu_item

    def test_order_controller_add_item(self):
        the_order, the_menu_item = self.order_an_item()
        self.assertIsInstance(self.view.controller, OrderController)
        self.assertEqual((UI.order, the_order), self.view.last_UI_created)
        self.assertEqual(1, len(the_order.items))
        self.assertIsInstance(the_order.items[0], OrderItem)
        self.assertEqual(the_order.items[0].details, the_menu_item)
        self.assertFalse(the_order.items[0].has_been_ordered())

    def test_order_controller_update_order(self):
        the_order, the_menu_item = self.order_an_item()
        self.view.last_UI_created = None
        self.view.controller.update_order()
        self.assertEqual((UI.table, self.restaurant.tables[2]), self.view.last_UI_created)
        self.assertEqual(1, len(the_order.items))
        self.assertIsInstance(the_order.items[0], OrderItem)
        self.assertEqual(the_order.items[0].details, the_menu_item)
        self.assertTrue(the_order.items[0].has_been_ordered())

    def test_order_controller_cancel(self):
        the_order, the_menu_item = self.order_an_item()
        self.view.last_UI_created = None
        self.view.controller.cancel_changes()
        self.assertEqual((UI.table, self.restaurant.tables[2]), self.view.last_UI_created)
        self.assertEqual(0, len(the_order.items))

    def test_order_controller_update_several_then_cancel(self):
        self.view.controller.table_touched(6)
        self.view.controller.seat_touched(7)
        the_order = self.restaurant.tables[6].order_for(7)
        self.view.controller.add_item(self.restaurant.menu_items[0])
        self.view.controller.add_item(self.restaurant.menu_items[3])
        self.view.controller.add_item(self.restaurant.menu_items[5])
        self.view.controller.update_order()

        def check_first_three_items(menu_items, items):
            self.assertEqual(menu_items[0], items[0].details)
            self.assertEqual(menu_items[3], items[1].details)
            self.assertEqual(menu_items[5], items[2].details)

        self.assertEqual(3, len(the_order.items))
        check_first_three_items(self.restaurant.menu_items, the_order.items)

        def add_two_more(menu_items, view):
            view.controller.seat_touched(7)
            view.controller.add_item(menu_items[1])
            view.controller.add_item(menu_items[2])

        add_two_more(self.restaurant.menu_items, self.view)
        self.view.controller.cancel_changes()

        self.assertEqual(3, len(the_order.items))
        check_first_three_items(self.restaurant.menu_items, the_order.items)

        add_two_more(self.restaurant.menu_items, self.view)
        self.view.controller.update_order()

        self.assertEqual(5, len(the_order.items))
        check_first_three_items(self.restaurant.menu_items, the_order.items)
        self.assertEqual(self.restaurant.menu_items[1], the_order.items[3].details)
        self.assertEqual(self.restaurant.menu_items[2], the_order.items[4].details)

    # TODO: This test makes sure that the red X that cancels an order item still works fine in this lab
    def test_cancel_item(self):

        # We start our program by touching seat 7 of table 6 and adding three items to the order
        self.view.controller.table_touched(6)
        self.view.controller.seat_touched(7)
        self.view.controller.add_item(self.restaurant.menu_items[0])
        self.view.controller.add_item(self.restaurant.menu_items[3])
        self.view.controller.add_item(self.restaurant.menu_items[5])

        # Now we test whether we can cancel a REQUESTED item by pressing X
        the_order = self.restaurant.tables[6].order_for(7)
        cancelled_item = the_order.items[2]
        self.view.controller.remove(cancelled_item)
        self.assertEqual(2, len(the_order.items))
        self.assertEqual(False, cancelled_item in the_order.items)

        # Now we check whether we can cancel a PLACED item by pressing X
        self.view.controller.add_item(self.restaurant.menu_items[5])
        self.view.controller.update_order()
        self.view.controller.seat_touched(7)
        the_order = self.restaurant.tables[6].order_for(7)
        cancelled_item = the_order.items[2]
        self.view.controller.remove(cancelled_item)
        self.assertEqual(2, len(the_order.items))
        self.assertEqual(False, cancelled_item in the_order.items)

    # TODO: Now we will test the bill functionality of this lab
    def test_bill(self):

        # We start our program by touching 3 seats in table 6, placing an order of 3 items in each of them
        self.view.controller.table_touched(6)
        self.view.controller.seat_touched(7)
        self.view.controller.add_item(self.restaurant.menu_items[0])
        self.view.controller.add_item(self.restaurant.menu_items[3])
        self.view.controller.add_item(self.restaurant.menu_items[5])
        self.view.controller.update_order()

        self.view.controller.seat_touched(3)
        self.view.controller.add_item(self.restaurant.menu_items[2])
        self.view.controller.add_item(self.restaurant.menu_items[4])
        self.view.controller.add_item(self.restaurant.menu_items[7])
        self.view.controller.update_order()

        self.view.controller.seat_touched(1)
        self.view.controller.add_item(self.restaurant.menu_items[4])
        self.view.controller.add_item(self.restaurant.menu_items[5])
        self.view.controller.add_item(self.restaurant.menu_items[8])
        self.view.controller.update_order()

        # Now we can test the "Settle up" button, which basically splits the orders of each table into respective bills
        # In our program, this button calls the make_bills() method
        self.view.controller.make_bills()

        # The following tests confirm that we're in the right UI and that we have the right controller
        self.assertIsInstance(self.view.controller, BillController)
        self.assertEqual(UI.bill, self.view.last_UI_created)

        # Now we get to select the orders that we want to group into Bill 1
        # Let's start by placing orders of seat 1 and 3 into Bill 1
        self.view.controller.select(1)
        self.view.controller.select(3)
        the_order = self.restaurant.tables[6].order_for(1)
        self.assertEqual(self.restaurant.tables[6].has_order_for(1), True)
        self.assertEqual(State.SELECTED, the_order.state)

        # Test whether we can unselect a seat on the Bill UI and check order State
        self.view.controller.unselect(1)
        self.assertEqual(State.PLACED, the_order.state)

        # Add orders of seat 1 and 3 again to Bill 1 and create new Bill
        self.view.controller.select(1)
        self.view.controller.new_bill()

        # When we create a new bill, this means that our orders were added to bill 1, let's test that.
        bills = self.view.controller.table.bills
        self.assertEqual(1, len(bills))
        orders = bills[0].items
        # Since we have two orders of 3 items each, there should be 6 items on the bill.
        self.assertEqual(6, len(orders))

        # Add orders of seat 7 to Bill 2 and print bills
        self.view.controller.select(7)
        self.view.controller.new_bill()




