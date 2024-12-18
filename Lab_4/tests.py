import unittest
from enum import Enum, auto

from controller import RestaurantController, TableController, OrderController
from model import Restaurant, OrderItem, State


class UI(Enum):
    """
    Used by ServerViewMock to represent the last user interface that was
    drawn.
    """
    RESTAURANT = auto()
    TABLE = auto()
    ORDER = auto()


class ServerViewMock:
    """
    A non-graphical replacement for `oorms.ServerView`, used for testing. Allows
    tests to check what was the last user interface rendered. Fully replicates the
    public interface of `ServerView`. The `set_controller` and `update` methods
    are exact copies of those in `oorms.RestaurantView`.
    """

    def __init__(self, restaurant):
        self.controller = None
        self.last_UI_created = None
        self.restaurant = restaurant
        self.set_controller(RestaurantController(self, self.restaurant))
        self.update()

    def set_controller(self, controller):
        self.controller = controller

    def update(self):
        self.controller.create_ui()

    def create_restaurant_ui(self):
        self.last_UI_created = UI.RESTAURANT

    def create_table_ui(self, table):
        self.last_UI_created = (UI.TABLE, table)

    def create_order_ui(self, order):
        self.last_UI_created = (UI.ORDER, order)


class OORMSTestCase(unittest.TestCase):

    def setUp(self):
        self.restaurant = Restaurant()
        self.view = ServerViewMock(self.restaurant)
        self.restaurant.add_view(self.view)

    def test_initial_state(self):
        self.assertEqual(UI.RESTAURANT, self.view.last_UI_created)
        self.assertIsInstance(self.view.controller, RestaurantController)

    def test_restaurant_controller_touch_table(self):
        self.view.controller.table_touched(3)
        self.assertIsInstance(self.view.controller, TableController)
        self.assertEqual(self.view.controller.table, self.restaurant.tables[3])
        self.assertEqual((UI.TABLE, self.restaurant.tables[3]), self.view.last_UI_created)

    def test_table_controller_done(self):
        self.view.controller.table_touched(5)
        self.view.controller.done()
        self.assertIsInstance(self.view.controller, RestaurantController)
        self.assertEqual(UI.RESTAURANT, self.view.last_UI_created)

    def test_table_controller_seat_touched(self):
        self.view.controller.table_touched(4)
        self.view.controller.seat_touched(0)
        self.assertIsInstance(self.view.controller, OrderController)
        self.assertEqual(self.view.controller.table, self.restaurant.tables[4])
        the_order = self.restaurant.tables[4].order_for(0)
        self.assertEqual(self.view.controller.order, the_order)
        self.assertEqual((UI.ORDER, the_order), self.view.last_UI_created)

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
        self.assertEqual((UI.ORDER, the_order), self.view.last_UI_created)
        self.assertEqual(1, len(the_order.items))
        self.assertIsInstance(the_order.items[0], OrderItem)
        self.assertEqual(the_order.items[0].details, the_menu_item)
        self.assertFalse(the_order.items[0].has_been_ordered())

    def test_order_controller_update_order(self):
        the_order, the_menu_item = self.order_an_item()
        self.view.last_UI_created = None
        self.view.controller.update_order()
        self.assertEqual((UI.TABLE, self.restaurant.tables[2]), self.view.last_UI_created)
        self.assertEqual(1, len(the_order.items))
        self.assertIsInstance(the_order.items[0], OrderItem)
        self.assertEqual(the_order.items[0].details, the_menu_item)
        self.assertTrue(the_order.items[0].has_been_ordered())

    def test_order_controller_cancel(self):
        the_order, the_menu_item = self.order_an_item()
        self.view.last_UI_created = None
        self.view.controller.cancel_changes()
        self.assertEqual((UI.TABLE, self.restaurant.tables[2]), self.view.last_UI_created)
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

    # TODO: To write our own tests, we will run our entire program and test everything along the way

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
        self.assertEqual(State.REQUESTED, cancelled_item.state)
        self.view.controller.remove_item(cancelled_item)
        self.assertEqual(2, len(the_order.items))
        self.assertEqual(False, cancelled_item in the_order.items)

        # Now we check whether we can cancel a PLACED item by pressing X
        self.view.controller.add_item(self.restaurant.menu_items[5])
        self.view.controller.update_order()
        self.view.controller.seat_touched(7)
        the_order = self.restaurant.tables[6].order_for(7)
        cancelled_item = the_order.items[2]
        self.view.controller.remove_item(cancelled_item)
        self.assertEqual(2, len(the_order.items))
        self.assertEqual(False, cancelled_item in the_order.items)

        # Now we check whether you can cancel a COOKING item
        # There are currently two items in the order
        the_order = self.restaurant.tables[6].order_for(7)
        the_order.items[0].next_state()
        item = the_order.items[0]
        self.assertEqual(State.COOKING, item.state)
        self.assertEqual(False, item.can_be_cancelled())
        # This shows us that a COOKING item cannot be cancelled, the red X won't appear

        # Now let's verify for other states
        item.next_state()
        self.assertEqual(State.READY, item.state)
        self.assertEqual(False, item.can_be_cancelled())

        item.next_state()
        self.assertEqual(State.SERVED, item.state)
        self.assertEqual(False, item.can_be_cancelled())
        # Conclusion: the red X should only appear when the item is in REQUESTED or PLACED state

    # TODO: We will test whether the next_state() method has the correct functionality.
    # TODO: We will also test whether each state has the appropriate behavior.

    def test_next_state(self):

        # We start by touching seat 7 of table 6 and adding an item to the order.
        self.view.controller.table_touched(6)
        self.view.controller.seat_touched(7)
        self.view.controller.add_item(self.restaurant.menu_items[0])
        the_order = self.restaurant.tables[6].order_for(7)
        item = the_order.items[0]

        # We test the behavior of the REQUESTED state of the item when it's added to the order
        self.assertEqual(State.REQUESTED, item.state)
        self.assertEqual(False, item.has_been_ordered())
        self.assertEqual(False, item.has_been_served())
        self.assertEqual(True, item.can_be_cancelled())

        # Once REQUESTED state behaves correctly, we move to the PLACED state by updating the order
        self.view.controller.update_order()
        self.assertEqual(State.PLACED, item.state)
        self.assertEqual(True, item.has_been_ordered())
        self.assertEqual(False, item.has_been_served())
        self.assertEqual(True, item.can_be_cancelled())

        # Once PLACED state behaves correctly, we move to the COOKING state by pressing 'Start Cooking' which calls next_state()
        item.next_state()
        self.assertEqual(State.COOKING, item.state)
        self.assertEqual(True, item.has_been_ordered())
        self.assertEqual(False, item.has_been_served())
        self.assertEqual(False, item.can_be_cancelled())

        # Once COOKING state behaves correctly, we move to the READY state by pressing 'Mark as Ready' which calls next_state()
        item.next_state()
        self.assertEqual(State.READY, item.state)
        self.assertEqual(True, item.has_been_ordered())
        self.assertEqual(False, item.has_been_served())
        self.assertEqual(False, item.can_be_cancelled())

        # Once READY state behaves correctly, we move to the READY state by pressing 'Mark as Served' which calls next_state()
        item.next_state()
        self.assertEqual(State.SERVED, item.state)
        self.assertEqual(True, item.has_been_ordered())
        self.assertEqual(True, item.has_been_served())
        self.assertEqual(False, item.can_be_cancelled())

        # Now that each state behaves correctly, we should test whether next_state() can raise an IndexError
        item.next_state()
        self.assertEqual(State.REQUESTED, item.state)
        # The item state loops back to the first state in the sequence, the method works





