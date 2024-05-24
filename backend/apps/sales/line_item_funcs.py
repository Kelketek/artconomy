from collections import defaultdict
from decimal import ROUND_CEILING, ROUND_HALF_EVEN, Decimal, localcontext
from typing import TYPE_CHECKING, Callable, Dict, Iterator, List, Union

from _decimal import ROUND_DOWN
from moneyed import Currency, Money, get_currency

from line_items import py_get_totals, py_reckon_lines, py_divide_amount

if TYPE_CHECKING:  # pragma: no cover
    from apps.sales.models import LineItem, LineItemSim

    Line = Union[LineItem, LineItemSim]
    LineMoneyMap = Dict[Line, Money]


def down_context(wrapped: Callable):
    def wrapper(*args, **kwargs):
        with localcontext() as ctx:
            ctx.rounding = ROUND_DOWN
            return wrapped(*args, **kwargs)

    return wrapper


def ceiling_context(wrapped: Callable):
    def wrapper(*args, **kwargs):
        with localcontext() as ctx:
            ctx.rounding = ROUND_CEILING
            return wrapped(*args, **kwargs)

    return wrapper


def half_even_context(wrapped: Callable):
    def wrapper(*args, **kwargs):
        with localcontext() as ctx:
            ctx.rounding = ROUND_HALF_EVEN
            return wrapped(*args, **kwargs)

    return wrapper


def lines_by_priority(
    lines: Iterator[Union["LineItem", "LineItemSim"]]
) -> List[List[Union["LineItem", "LineItemSim"]]]:
    """
    Groups line items by priority.
    """
    priority_sets = defaultdict(list)
    for line in lines:
        priority_sets[line.priority].append(line)
    return [priority_set for _, priority_set in sorted(priority_sets.items())]


@down_context
def get_totals(
    lines: Iterator["Line"], currency=get_currency("USD")
) -> (Money, Money, "LineMoneyMap"):
    from apps.sales.serializers import LineItemCalculationSerializer

    result = py_get_totals(
        LineItemCalculationSerializer(many=True, instance=lines).data, digits(currency)
    )
    return (
        Money(result["total"], currency),
        Money(result["discount"], currency),
        {line: Money(result["subtotals"][line.id], currency) for line in lines},
    )


def reckon_lines(lines, currency=get_currency("USD")) -> Money:
    """
    Reckons all line items to produce a total value.
    """
    from apps.sales.serializers import LineItemCalculationSerializer

    result = py_reckon_lines(
        LineItemCalculationSerializer(many=True, instance=lines).data, digits(currency)
    )
    return Money(result, currency)


def penny_amount(currency: Currency):
    if not digits(currency):
        return Money("1", currency)
    return Money(
        Decimal("0." + ("0" * (digits(currency) - 1)) + "1"),
        currency,
    )


def zero_amount(currency: Currency):
    if not digits(currency):
        return Money("0", currency)
    return Money(
        Decimal("0." + ("0" * digits(currency))),
        currency,
    )


@down_context
def divide_amount(amount: Money, divisor: int) -> List[Money]:
    """
    Takes an amount of money, and divides it as evenly as possible according to divisor.
    Then, allocate remaining 'pennies' of the currency to the entries until the total
    number of discrete values is accounted for.

    Not used in the normal price calculator, but used in creating estimated costs
    per transactions in reports.
    """
    return [
        Money(entry, amount.currency)
        for entry in py_divide_amount(
            str(amount.amount), divisor, digits(amount.currency)
        )
    ]


def digits(currency: Currency) -> int:
    return len(str(currency.sub_unit)) - 1
