from collections import defaultdict
from decimal import ROUND_CEILING, ROUND_HALF_EVEN, Decimal, localcontext
from functools import cmp_to_key, reduce
from typing import TYPE_CHECKING, Callable, Dict, Iterator, List, Tuple, Union

from _decimal import ROUND_DOWN
from moneyed import Currency, Money, get_currency

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


def distribute_reduction(
    *, total: Money, distributed_amount: Money, line_values: "LineMoneyMap"
) -> "LineMoneyMap":
    """
    Given an amount to discount from a set of line items, remove it proportionally from
    each line item.
    """
    reductions = {}
    for line, original_value in line_values.items():
        # Don't apply reductions to discounts, as that would be nonsense.
        if original_value < Money(0, total.currency):
            continue
        if total.amount == Decimal("0"):
            multiplier = Decimal("1.00") / len(line_values)
        else:
            multiplier = original_value / total
        reductions[line] = Money(distributed_amount.amount * multiplier, total.currency)
    return reductions


@half_even_context
def priority_total(
    current: (Money, Money, "LineMoneyMap"), priority_set: List["Line"]
) -> (Money, "LineMoneyMap"):
    """
    Get the effect on the total of a priority set. First runs any percentage increase,
    then adds in the static amount. Calculates the difference of each separately to make
    sure they're not affecting each other.
    """
    current_total, discount, subtotals = current
    working_subtotals = {}
    summable_totals = {}
    reductions: List["LineMoneyMap"] = []
    for line in priority_set:
        cascaded_amount = Money(0, current_total.currency)
        added_amount = Money(0, current_total.currency)
        if line.cascade_amount:
            cascaded_amount += line.amount
        else:
            added_amount += line.amount
        # Percentages with equal priorities should not stack.
        multiplier = Decimal(".01") * line.percentage
        if line.back_into_percentage:
            if line.cascade_percentage:
                working_amount = (
                    current_total / (multiplier + Decimal("1.00"))
                ) * multiplier
            else:
                factor = Decimal("1.00") / (Decimal("1.00") - multiplier)
                additional = Money(0, current_total.currency)
                if not line.cascade_amount:
                    additional = line.amount
                initial_amount = current_total + additional
                working_amount = (initial_amount * factor) - initial_amount
        else:
            working_amount = current_total * multiplier
        if line.cascade_percentage:
            cascaded_amount += working_amount
        else:
            added_amount += working_amount
        working_amount += line.amount
        if cascaded_amount:
            line_values = {}
            for key in subtotals.keys():
                if key.priority < line.priority:
                    line_values[key] = subtotals.get(key)
            reductions.append(
                distribute_reduction(
                    total=current_total - discount,
                    distributed_amount=cascaded_amount,
                    line_values=line_values,
                )
            )
        if added_amount:
            summable_totals[line] = added_amount
        working_subtotals[line] = working_amount
        if working_amount < Money(0, working_amount.currency):
            discount += working_amount
    new_subtotals = {**subtotals}
    for reduction_set in reductions:
        for line, reduction in reduction_set.items():
            new_subtotals[line] = new_subtotals[line] - reduction
    add_on = sum(summable_totals.values())
    new_totals = {**new_subtotals, **working_subtotals}
    return (
        current_total + add_on,
        discount,
        new_totals,
    )


@down_context
def to_distribute(total: Money, money_map: "LineMoneyMap") -> Money:
    combined_sum = sum(
        [value.round(digits(total.currency)) for value in money_map.values()]
    ) or Money("0", total.currency)
    return total.round(digits(total.currency)) - combined_sum


def redistribution_priority(
    ascending_priority: bool,
    item: Tuple["LineItem", Money],
    item2: Tuple["LineItem", Money],
) -> Union[float, int]:
    item_line, item_amount = item
    item2_line, item2_amount = item2
    if item_line.priority != item2_line.priority:
        if ascending_priority:
            return item2_line.priority - item_line.priority
        return item_line.priority - item2_line.priority
    if item_amount == item2_amount:
        lines = sorted([item_line, item2_line], key=lambda x: str(x.id))
        # Ids could be something other than integers, but this should work the same as
        # it did before, when I made the assumption they would be.
        return float(lines.index(item2_line) - lines.index(item_line))
    return float(item2_amount.amount - item_amount.amount)


@down_context
def distribute_difference(
    difference: Money, money_map: "LineMoneyMap"
) -> "LineMoneyMap":
    """
    So. We have a few leftover pennies. To figure out where we should allocate them,
    we need to zero out everything but the remainder (that is, everything but what's
    beyond the cents place), and then compare what remains. The largest numbers are the
    numbers that were closest to rolling over into another penny, so we put them there
    first.

    We also floor all the amounts to make sure that the discrete total of all values
    will be the correct target, and each value will be representable as a real monetary
    value-- that is, something no more fractionalized than cents.
    """
    updated_map = {
        key: value.round(digits(value.currency)) for key, value in money_map.items()
    }
    sorted_values = [(key, value) for key, value in updated_map.items()]
    sorted_values.sort(
        key=cmp_to_key(
            lambda a, b: redistribution_priority(
                difference > Money("0", difference.currency), a, b
            )
        ),
    )
    current_values = [*sorted_values]
    remaining = difference
    if remaining > Money("0", remaining.currency):
        amount = Money("0.01", remaining.currency)
    else:
        amount = Money("-0.01", remaining.currency)
    while remaining != Money("0.00", remaining.currency):
        if not len(current_values):  # pragma: no cover
            current_values = [*sorted_values]
        key = current_values.pop(0)[0]
        updated_map[key] += amount
        remaining -= amount
    return updated_map


@down_context
def normalized_lines(
    priority_sets: List[List[Union["LineItem", "LineItemSim"]]],
    currency=get_currency("USD"),
):
    zero = zero_amount(currency)
    total, discount, subtotals = reduce(
        priority_total,
        priority_sets,
        (zero, zero, {}),
    )
    total = total.round(digits(total.currency))
    subtotals = {
        key: value.round(digits(total.currency)) for key, value in subtotals.items()
    }
    difference = to_distribute(total, subtotals)
    if difference != Money("0", difference.currency):
        subtotals = distribute_difference(difference, subtotals)
    return total, discount, subtotals


@down_context
def get_totals(
    lines: Iterator["Line"], currency=get_currency("USD")
) -> (Money, Money, "LineMoneyMap"):
    priority_sets = lines_by_priority(lines)
    return normalized_lines(priority_sets, currency=currency)


def reckon_lines(lines, currency=get_currency("USD")) -> Money:
    """
    Reckons all line items to produce a total value.
    """
    value, discount, _subtotals = get_totals(lines, currency=currency)
    return value.round(digits(currency))


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
    assert amount == amount.round(digits(amount.currency))
    target_amount = amount / divisor
    target_amount = target_amount.round(digits(amount.currency))
    difference = amount - (target_amount * divisor).round(digits(amount.currency))
    difference *= target_amount.currency.sub_unit
    difference = int(difference.amount)
    result = [target_amount] * divisor
    penny = penny_amount(target_amount.currency)
    assert difference >= 0
    # It's probably not possible for it to loop around again, but I'm not a confident
    # enough mathematician to disprove it, especially since I'm unsure how having
    # discrete values factors in for edge cases. If someone else can be more assured,
    # I'm good with simplifying this loop.
    while difference:
        for index, item in enumerate(result):
            result[index] += penny
            difference -= 1
            if not difference:
                break
    return result


def digits(currency: Currency) -> int:
    return len(str(currency.sub_unit)) - 1
