from controller import RestaurantController, TableController, OrderController
from constants import MENU_ITEMS
from model import Restaurant, Table, Order, OrderItem

import unittest

RESTAURANT_UI = 'restaurant UI'
TABLE_UI = 'table UI'
ORDER_UI = 'order UI'


class ServerViewMock:
    """
    Replaces the graphical server view (oorms.ServerView) for testing purposes.
    Contains just enough test logic for the controller layer to function. Tracks
    which UI was last created so UI changes can be tested.
    """

    def __init__(self, restaurant):
        self.controller = None
        self.last_UI_created = None
        self.restaurant = restaurant
        self.set_controller(RestaurantController(self, self.restaurant))

    def set_controller(self, controller):
        self.controller = controller
        self.controller.create_ui()

    def create_restaurant_ui(self):
        self.last_UI_created = RESTAURANT_UI

    def create_table_ui(self, table):
        self.last_UI_created = (TABLE_UI, table)

    def create_order_ui(self, order):
        self.last_UI_created = (ORDER_UI, order)


class OORMSTestCase(unittest.TestCase):

    def setUp(self):
        self.restaurant = Restaurant()
        self.view = ServerViewMock(self.restaurant)

    def test_initial_state(self):
        self.assertEqual(RESTAURANT_UI, self.view.last_UI_created)
        self.assertIsInstance(self.view.controller, RestaurantController)

    def test_restaurant_controller_touch_table(self):
        self.view.controller.table_touched(3)
        self.assertIsInstance(self.view.controller, TableController)
        self.assertEqual(self.view.controller.table, self.restaurant.tables[3])
        self.assertEqual((TABLE_UI, self.restaurant.tables[3]), self.view.last_UI_created)

    def test_table_controller_done(self):
        self.view.controller.table_touched(5)
        self.view.controller.done()
        self.assertIsInstance(self.view.controller, RestaurantController)
        self.assertEqual(RESTAURANT_UI, self.view.last_UI_created)

    def test_table_controller_seat_touched(self):
        self.view.controller.table_touched(4)
        self.view.controller.seat_touched(0)
        self.assertIsInstance(self.view.controller, OrderController)
        self.assertEqual(self.view.controller.table, self.restaurant.tables[4])
        the_order = self.restaurant.tables[4].order_for(0)
        self.assertEqual(self.view.controller.order, the_order)
        self.assertEqual((ORDER_UI, the_order), self.view.last_UI_created)

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
        self.assertEqual((ORDER_UI, the_order), self.view.last_UI_created)
        self.assertEqual(1, len(the_order.items))
        self.assertIsInstance(the_order.items[0], OrderItem)
        self.assertEqual(the_order.items[0].details, the_menu_item)
        self.assertFalse(the_order.items[0].ordered)

    def test_order_controller_update_order(self):
        the_order, the_menu_item = self.order_an_item()
        self.view.last_UI_created = None
        self.view.controller.update_order()
        self.assertEqual((TABLE_UI, self.restaurant.tables[2]), self.view.last_UI_created)
        self.assertEqual(1, len(the_order.items))
        self.assertIsInstance(the_order.items[0], OrderItem)
        self.assertEqual(the_order.items[0].details, the_menu_item)
        self.assertTrue(the_order.items[0].ordered)

    def test_order_controller_cancel(self):
        the_order, the_menu_item = self.order_an_item()
        self.view.last_UI_created = None
        self.view.controller.cancel()
        self.assertEqual((TABLE_UI, self.restaurant.tables[2]), self.view.last_UI_created)
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
        self.view.controller.cancel()

        self.assertEqual(3, len(the_order.items))
        check_first_three_items(self.restaurant.menu_items, the_order.items)

        add_two_more(self.restaurant.menu_items, self.view)
        self.view.controller.update_order()

        self.assertEqual(5, len(the_order.items))
        check_first_three_items(self.restaurant.menu_items, the_order.items)
        self.assertEqual(self.restaurant.menu_items[1], the_order.items[3].details)
        self.assertEqual(self.restaurant.menu_items[2], the_order.items[4].details)
