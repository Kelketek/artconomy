from collections import defaultdict
from decimal import (
    ROUND_CEILING,
    ROUND_DOWN,
    ROUND_HALF_EVEN,
    Decimal,
    localcontext,
    ROUND_HALF_UP,
)
from typing import TYPE_CHECKING, Callable, Dict, Iterator, List, Union

from django.conf import settings
from moneyed import Currency, Money, get_currency

from line_items import (
    py_get_totals,
    py_reckon_lines,
    py_divide_amount,
    py_deliverable_lines,
    py_tip_fee_lines,
)

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


def half_up_context(wrapped: Callable):
    def wrapper(*args, **kwargs):
        with localcontext() as ctx:
            ctx.rounding = ROUND_HALF_UP
            return wrapped(*args, **kwargs)

    return wrapper


def lines_by_priority(
    lines: Iterator[Union["LineItem", "LineItemSim"]],
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


def tip_lines(*, international: bool):
    from apps.sales.utils import pricing_spec

    return py_tip_fee_lines(
        {
            "pricing": pricing_spec(),
            "international": international,
            "quantization": digits(settings.PROCESSING_STATIC.currency),
        }
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


def deliverable_lines(
    *,
    base_price: Money,
    table_product: bool,
    cascade: bool,
    escrow_enabled: bool,
    international: bool,
    extra_lines: list["LineItem"],
    user_id: int,
    plan_name: str,
):
    from apps.sales.serializers import LineItemCalculationSerializer
    from apps.sales.utils import pricing_spec

    return py_deliverable_lines(
        {
            "base_price": str(base_price.amount),
            "table_product": table_product,
            "cascade": cascade,
            "escrow_enabled": escrow_enabled,
            "international": international,
            "user_id": user_id,
            "extra_lines": LineItemCalculationSerializer(
                many=True, instance=extra_lines
            ).data,
            "allow_soft_failure": False,
            "pricing": pricing_spec(),
            "plan_name": plan_name,
            "quantization": digits(base_price.currency),
        }
    )
