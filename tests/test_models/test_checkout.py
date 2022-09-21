"""
Test for YenePay checkout
"""
import os
import random
import unittest

import validators
from faker import Faker

from yenepay.constants import CART, EXPRESS
from yenepay.exceptions import CheckoutError
from yenepay.models.checkout import Checkout as AbstractCheckout, Item

fake = Faker()


def get_random_price():
    """return random price value."""
    return round(random.random() * 10e5, 2)


class Checkout(AbstractCheckout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TestItem(unittest.TestCase):
    """Test item model."""

    def setUp(self):
        self.name = fake.name()
        self.id = fake.uuid4()
        self.unit_price = get_random_price()
        self.quantity = random.randint(1, 10e2)

        self.item = Item(
            name=self.name,
            unit_price=self.unit_price,
            quantity=self.quantity,
            item_id=self.id,
        )

    def test_item_id(self):
        """test item id."""
        self.assertEqual(self.item.id, self.id)
        self.assertEqual(self.item.itemId, self.id)

    def test_item_id_setter(self):
        """test item id setter."""
        item_id = fake.uuid4()
        self.item.id = item_id

        self.assertEqual(self.item.id, item_id)
        self.assertEqual(self.item.itemId, item_id)

    def test_item_name(self):
        """test item name."""
        self.assertEqual(self.item.name, self.name)
        self.assertEqual(self.item.itemName, self.name)

    def test_item_name_setter(self):
        """test item name setter."""
        item_name = fake.name()
        self.item.name = item_name

        self.assertEqual(self.item.name, item_name)
        self.assertEqual(self.item.itemName, item_name)

    def test_item_unit_price(self):
        """test item unit price."""
        self.assertEqual(self.item.unit_price, self.unit_price)
        self.assertEqual(self.item.unitPrice, self.unit_price)

    def test_unit_price_setter(self):
        """test unit price setter."""
        unit_price = get_random_price()
        self.item.unit_price = unit_price

        self.assertEqual(self.item.unit_price, unit_price)
        self.assertEqual(self.item.unitPrice, unit_price)

    def test_item_quantity(self):
        """test item quantity."""
        self.assertEqual(self.item.quantity, self.quantity)

    def test_item_representation(self):
        """test item representation."""
        self.assertEqual(self.item.__repr__(), f"<Item '{self.item.name}'>")

    def test_item_string_representation(self):
        """test item string representation."""
        self.assertEqual(str(self.item), self.item.__repr__())

    def test_to_dict(self):
        """test item to dict."""
        data = {
            "itemId": self.item.itemId,
            "itemName": self.item.itemName,
            "unitPrice": self.item.unitPrice,
            "quantity": self.item.quantity,
        }

        self.assertEqual(self.item.to_dict(), data)


class TestCheckoutWithRequiredAttributes(unittest.TestCase):
    """Test checkout model using requied attribute only."""

    def setUp(self):
        self.merchant_id = "0000"
        self.single_item = [
            Item(
                fake.name(),
                get_random_price(),
                1,
            ),
        ]
        self.multiple_items = [
            Item(
                fake.name(),
                get_random_price(),
                1,
            ),
            Item(
                fake.name(),
                get_random_price(),
                1,
            ),
        ]

        self.cart_checkout = self.get_cart_checkout()
        self.express_checkout = self.get_express_checkout()

    def get_cart_checkout(self, **kwargs):
        kwargs.setdefault("merchant_id", self.merchant_id)
        kwargs.setdefault("items", self.multiple_items)
        return Checkout(CART, **kwargs)

    def get_express_checkout(self, **kwargs):
        kwargs.setdefault("merchant_id", self.merchant_id)
        kwargs.setdefault("items", self.single_item)
        return Checkout(EXPRESS, **kwargs)

    def test_process(self):
        """test process."""
        self.assertEqual(
            self.cart_checkout.process, self.cart_checkout._process
        )
        self.assertEqual(
            self.express_checkout.process, self.express_checkout._process
        )

    def test_merchant_id(self):
        """test merchant id."""
        self.assertEqual(self.cart_checkout.merchant_id, self.merchant_id)
        self.assertEqual(self.express_checkout.merchant_id, self.merchant_id)
        self.assertEqual(self.cart_checkout.merchantId, self.merchant_id)
        self.assertEqual(self.express_checkout.merchantId, self.merchant_id)

    def test_merchant_id_setter(self):
        """test merchant id setter."""
        merchant_id = "111"
        self.cart_checkout.merchant_id = merchant_id
        self.express_checkout.merchant_id = merchant_id

        self.assertEqual(self.cart_checkout.merchantId, merchant_id)
        self.assertEqual(self.express_checkout.merchantId, merchant_id)

    def test_items(self):
        """test items."""
        self.assertEqual(self.express_checkout.items, self.single_item)
        self.assertEqual(self.cart_checkout.items, self.multiple_items)

    def test_validation_with_no_process(self):
        """test checkout model with None value of process type."""

        with self.assertRaises(ValueError):
            Checkout(None, self.merchant_id, self.single_item)

        with self.assertRaises(ValueError):
            Checkout(None, self.merchant_id, self.multiple_items)

    def test_validation_with_invalid_process(self):
        """test checkout model with invalid process type."""

        process = fake.name()

        with self.assertRaises(ValueError):
            Checkout(process, self.merchant_id, self.single_item)

        with self.assertRaises(ValueError):
            Checkout(process, self.merchant_id, self.multiple_items)

    def test_process_is_readonly(self):
        """test process is readonly."""
        with self.assertRaises(AttributeError):
            checkout = self.get_cart_checkout()
            checkout._process = CART

        with self.assertRaises(AttributeError):
            checkout = self.get_cart_checkout()
            checkout._process = EXPRESS

        with self.assertRaises(AttributeError):
            checkout = self.get_express_checkout()
            checkout._process = CART

        with self.assertRaises(AttributeError):
            checkout = self.get_express_checkout()
            checkout._process = EXPRESS

    def test_items_with_string_value(self):
        """test items with iteratable string value."""
        items = fake.name()

        with self.assertRaises(TypeError):
            self.get_cart_checkout(items=items)

        with self.assertRaises(TypeError):
            self.get_express_checkout(items=items)

    def test_items_with_dict_value(self):
        """test items with iteratable dictionary value."""
        with self.assertRaises(TypeError):
            self.get_cart_checkout(items={})

        with self.assertRaises(TypeError):
            self.get_express_checkout(items={})

    def test_items_with_int_value(self):
        """test items with iteratable int value."""
        with self.assertRaises(TypeError):
            self.get_cart_checkout(items=0)

        with self.assertRaises(TypeError):
            self.get_express_checkout(items=0)

    def test_items_with_none_value(self):
        """test items with None value."""

        with self.assertRaises(TypeError):
            self.get_cart_checkout(items=None)

        with self.assertRaises(TypeError):
            self.get_express_checkout(items=None)

    def test_items_with_empty_list(self):
        """test items with empty list."""
        with self.assertRaises(ValueError):
            self.get_express_checkout(items=[])

        with self.assertRaises(ValueError):
            self.get_express_checkout(items=[])

    def test_items_with_empty_tuple(self):
        """test items with empty tuple."""
        with self.assertRaises(ValueError):
            self.get_express_checkout(items=())

        with self.assertRaises(ValueError):
            self.get_express_checkout(items=())

    def test_items_with_empty_set(self):
        """test items with empty tuple."""
        with self.assertRaises(ValueError):
            self.get_express_checkout(items=set())

        with self.assertRaises(ValueError):
            self.get_express_checkout(items=set())

    def test_items_with_invalid_single_item_type(self):
        """test items with invalid single item type."""
        int_item = [1]
        str_item = ["1"]
        dict_item = [{}]
        none_item = [None]

        with self.assertRaises(TypeError):
            self.get_express_checkout(items=int_item)

        with self.assertRaises(TypeError):
            self.get_express_checkout(items=str_item)

        with self.assertRaises(TypeError):
            self.get_express_checkout(items=dict_item)

        with self.assertRaises(TypeError):
            self.get_express_checkout(items=none_item)

    def test_items_with_invalid_multiple_items_type(self):
        """test items with invalid multiple items type."""
        int_items = [1, 2, 3]
        str_items = ["1", "2", "3"]
        dict_items = [{}, {}, {}]
        none_items = [None, None, None]
        mixed_items = [1, "2", {}, None]
        valid_with_invlaid_items = [*self.single_item, *self.multiple_items, 0]

        with self.assertRaises(TypeError):
            self.get_cart_checkout(items=int_items)

        with self.assertRaises(TypeError):
            self.get_cart_checkout(items=str_items)

        with self.assertRaises(TypeError):
            self.get_cart_checkout(items=dict_items)

        with self.assertRaises(TypeError):
            self.get_cart_checkout(items=none_items)

        with self.assertRaises(TypeError):
            self.get_cart_checkout(items=mixed_items)

        with self.assertRaises(TypeError):
            self.get_cart_checkout(items=valid_with_invlaid_items)

    def test_items_with_express_and_multiple_items(self):
        """test items with express process and multiple items."""
        with self.assertRaises(ValueError):
            Checkout(EXPRESS, self.merchant_id, self.multiple_items)

    def test_to_dict_with_cart_process(self):
        """test to dict with process type Cart."""

        data = {
            "process": CART,
            "merchantId": self.cart_checkout.merchantId,
            "items": [item.to_dict() for item in self.cart_checkout.items],
            "expiresInDays": 1,  # Default value
        }
        cart_dict = self.cart_checkout.to_dict()

        self.assertEqual(cart_dict, data)

    def test_to_dict_with_express_process(self):
        """test to dict with process type Express."""

        data = {
            "process": EXPRESS,
            "merchantId": self.express_checkout.merchantId,
            "items": [item.to_dict() for item in self.express_checkout.items],
            "expiresInDays": 1,  # Default value
        }
        express_dict = self.express_checkout.to_dict()

        self.assertEqual(express_dict, data)

    def test_checkout_representation(self):
        """test checkout representation."""
        self.assertEqual(
            self.cart_checkout.__repr__(),
            f"<CartCheckout: None - {self.cart_checkout.merchant_id}>",
        )
        self.assertEqual(
            self.express_checkout.__repr__(),
            f"<ExpressCheckout: None - {self.express_checkout.merchant_id}>",
        )

    def test_checkout_string_representation(self):
        """test checkout string reprsentaiton."""

        self.assertEqual(
            str(self.cart_checkout), self.cart_checkout.__repr__()
        )
        self.assertEqual(
            str(self.express_checkout), self.express_checkout.__repr__()
        )

    def test_get_url_with_cart_process(self):
        """test get url with cart process."""
        merchant_id = os.environ.get("YENEPAY_MERCHANT_ID", self.merchant_id)

        checkout = self.get_cart_checkout(merchant_id=merchant_id)
        url = checkout.get_url()

        self.assertTrue(validators.url(url))

    def test_get_url_with_express_process(self):
        """test get url with express process."""
        merchant_id = os.environ.get("YENEPAY_MERCHANT_ID", self.merchant_id)

        checkout = self.get_express_checkout(merchant_id=merchant_id)
        url = checkout.get_url()

        self.assertTrue(validators.url(url))

    def test_get_url_with_invalid_data(self):
        """test get url with invalid data."""
        cart_checkout = Checkout(
            CART, merchant_id=None, items=self.multiple_items
        )
        express_checkout = Checkout(
            EXPRESS, merchant_id=None, items=self.single_item
        )

        with self.assertRaises(CheckoutError):
            cart_checkout.get_url()

        with self.assertRaises(CheckoutError):
            express_checkout.get_url()