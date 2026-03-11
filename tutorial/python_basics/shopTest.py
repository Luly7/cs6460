"""Test script for the FruitShop class."""
from shop import FruitShop


def main() -> None:
    """Run test cases for FruitShop class."""
    # Test first shop
    shop_name = 'Berkeley Bowl'
    fruit_prices = {'apples': 1.00, 'oranges': 1.50, 'pears': 1.75}
    berkeley_shop = FruitShop(shop_name, fruit_prices)
    apple_price = berkeley_shop.get_cost_per_pound('apples')
    print(f'Apples cost ${apple_price:.2f} at {shop_name}.')

    # Test second shop
    other_name = 'Stanford Mall'
    other_fruit_prices = {'kiwis': 6.00, 'apples': 4.50, 'peaches': 8.75}
    other_fruit_shop = FruitShop(other_name, other_fruit_prices)
    other_price = other_fruit_shop.get_cost_per_pound('apples')
    print(f'Apples cost ${other_price:.2f} at {other_name}.')
    print("My, that's expensive!")


if __name__ == '__main__':
    main()