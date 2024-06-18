//! Common line item handling code between Artconomy's frontend and backend.
//!
//! Allows for consistent, fast handling of financial data. Quantizes currency
//! values so that no extra/missing pennies are found, and provides flexible distribution
//! of amounts/percentages between line items.
//!

#![warn(missing_docs)]
extern crate serde_json;
extern crate wasm_bindgen;
use wasm_bindgen::prelude::*;

#[macro_use]
extern crate serde_derive;

/// Data structures used in line item calculations.
pub mod data;

mod test;

/// Line item calculation functions used for determining amounts on invoices.
pub mod funcs {
    use crate::data::{Currency, LineItem, LineMoneyMap, Money};
    use rust_decimal::prelude::ToPrimitive;
    use rust_decimal::Decimal;
    use rust_decimal_macros::dec;
    use std::cmp::Ordering;
    use std::collections::HashMap;
    use wasm_bindgen::prelude::wasm_bindgen;

    /// Takes a list of line items, and builds them into lists of equal priority.
    pub fn lines_by_priority(lines: Vec<&LineItem>) -> Vec<Vec<&LineItem>> {
        let mut priority_sets: HashMap<i16, Vec<&LineItem>> = HashMap::new();
        for line in lines.iter() {
            let priority = line.priority;
            priority_sets.entry(priority).or_default().push(line);
        }
        let mut prioritized_lines: Vec<Vec<&LineItem>> = Vec::new();
        for (_, set) in priority_sets.drain() {
            prioritized_lines.push(set);
        }
        prioritized_lines.sort_by(|entry_a, entry_b| entry_a[0].priority.cmp(&entry_b[0].priority));
        prioritized_lines
    }

    /// Given a total, and an amount that needs to be proportionally pulled from the lines (such as a
    /// discount amount, or a calculated fee based on the total), and a current LineMoneyMap, produces
    /// a new, revalued LineMoneyMap with the Money amounts reduced proportionally in a way that adds
    /// up to the distributed_amount. Note that this reduction is not quantized or rounded.
    fn distribute_reduction(
        total: Money,
        distributed_amount: Money,
        line_values: LineMoneyMap,
    ) -> LineMoneyMap {
        let mut reductions = LineMoneyMap::new();
        let zero = total.currency().zero();
        for (line, original_value) in line_values.iter() {
            if original_value < &zero {
                continue;
            }
            let multiplier = if total == zero {
                total
                    .currency()
                    .money_from_dec(dec!(1) / Decimal::new(line_values.len().to_i64().unwrap(), 0))
            } else {
                *original_value / total
            };
            reductions.insert(line, distributed_amount * multiplier);
        }
        reductions
    }

    /// Determine the total value of a set of a 'priority set' of lines.
    /// Line items are arranged in a vector of vectors. The outer vector is sorted according to
    /// priority by the 'lines_by_priority' function. They are then folded using this function to
    /// produce a final LineMoneyMap that has resolved all monetary values for all lines.
    fn priority_total<'a>(
        current: (Money, Money, LineMoneyMap<'a>),
        priority_set: &Vec<&'a LineItem>,
    ) -> (Money, Money, LineMoneyMap<'a>) {
        /*
        Get the effect on the total of a priority set. First runs any percentage increase,
        then adds in the static amount. Calculates the difference of each separately to make
        sure they're not affecting each other.
        */
        let (current_total, mut discount, subtotals) = current;
        let mut working_subtotals: LineMoneyMap = HashMap::new();
        let mut summable_totals: LineMoneyMap = HashMap::new();
        let mut reductions: Vec<LineMoneyMap> = Vec::new();
        let currency = current_total.currency();
        let zero = currency.zero();
        let one = currency.money_from_dec(dec!(1));
        for line in priority_set.iter() {
            let line_amount = currency.money_from_string(line.amount);
            let mut cascaded_amount = current_total.currency().zero();
            let mut added_amount = current_total.currency().zero();
            let mut working_amount: Money;
            if line.cascade_amount {
                cascaded_amount = cascaded_amount + line_amount;
            } else {
                added_amount = added_amount + line_amount;
            }
            let multiplier = Money::new(dec!(0.01) * Decimal::from_str_exact(line.percentage).unwrap(), *current_total.currency());
            if line.back_into_percentage {
                let divisor = multiplier + one;
                if line.cascade_percentage {
                    working_amount = (current_total / divisor) * multiplier;
                } else {
                    let factor = one / (one - multiplier);
                    let mut additional = zero;
                    if !line.cascade_amount {
                        additional = line_amount;
                    }
                    let initial_amount = current_total + additional;
                    working_amount = (initial_amount * factor) - initial_amount;
                }
            } else {
                working_amount = current_total * multiplier;
            }
            if line.cascade_percentage {
                cascaded_amount = cascaded_amount + working_amount;
            } else {
                added_amount = added_amount + working_amount;
            }
            working_amount = working_amount + line_amount;
            if cascaded_amount != zero {
                let mut line_values: LineMoneyMap = HashMap::new();
                for key in subtotals.keys() {
                    if key.priority < line.priority {
                        line_values.insert(key, subtotals[key]);
                    }
                }
                let output =
                    distribute_reduction(current_total - discount, cascaded_amount, line_values);
                reductions.push(output)
            }
            if added_amount != zero {
                summable_totals.insert(line, added_amount);
            }
            working_subtotals.insert(line, working_amount);
            if working_amount < zero {
                discount = discount + working_amount;
            }
        }
        let mut new_subtotals = subtotals.clone();
        for reduction_set in reductions.iter() {
            for (line, reduction) in reduction_set.iter() {
                new_subtotals.insert(line, new_subtotals[line] - *reduction);
            }
        }
        let mut add_on: Money = zero;
        for operand in summable_totals.values() {
            add_on = add_on + *operand;
        }
        let mut new_totals = new_subtotals.clone();
        for (key, value) in working_subtotals.iter() {
            new_totals.insert(key, *value);
        }
        (current_total + add_on.quantized(), discount, new_totals)
    }

    fn redistribution_priority(
        ascending_priority: bool,
        item: (&LineItem, Money),
        item2: (&LineItem, Money),
    ) -> f64 {
        let (item_line, item_amount) = item;
        let (item2_line, item2_amount) = item2;
        if item_line.priority != item2_line.priority {
            if ascending_priority {
                return (item_line.priority - item2_line.priority).to_f64().unwrap();
            }
            return (item2_line.priority - item_line.priority).to_f64().unwrap();
        }
        if item_amount == item2_amount {
            return item2_line.id.to_f64().unwrap() - item_line.id.to_f64().unwrap();
        }
        return (item2_amount.amount() - item_amount.amount())
            .to_f64()
            .unwrap();
    }

    fn cmp_to_key(result: f64) -> Ordering {
        if result < 0.0 {
            return Ordering::Less;
        } else if result > 0.0 {
            return Ordering::Greater;
        }
        Ordering::Equal
    }

    /// So. We have a few leftover quanta (pennies). The largest numbers are the
    /// numbers that were closest to rolling over into another penny, so we put them there
    /// first.
    ///
    /// We roll over as needed to keep distributing cents until all the remaining quanta in the
    /// difference argument are accounted for.
    ///
    fn distribute_difference(difference: Money, mut money_map: LineMoneyMap) -> LineMoneyMap {
        let zero = difference.currency().zero();
        let mut sorted_values: Vec<(&LineItem, Money)> = money_map
            .iter()
            .map(|(line, amount)| (*line, *amount))
            // Only add to the values when the values are already signed positive, or subtract
            // when negative.
            .filter(|(_line, money)| {
                if difference > zero {
                    money > &zero
                } else {
                    money < &zero
                }
            })
            .collect();
        let mut remaining = difference;
        let amount: Money = if remaining > zero {
            remaining.currency().quantum()
        } else {
            zero - remaining.currency().quantum()
        };
        // Values must be in the reverse order of how we want to apply the changes,
        // since we're popping from the end of the vector in the loop below.
        sorted_values
            .sort_by(|a, b| cmp_to_key(redistribution_priority(difference > zero, *a, *b)));
        let mut current_values = sorted_values.clone();
        while remaining != zero {
            if current_values.is_empty() {
                current_values.clone_from(&sorted_values)
            }
            let key = current_values.pop().unwrap().0;
            money_map.insert(key, money_map[key] + amount);
            remaining = remaining - amount;
        }
        money_map
    }

    /// Given a quantized total and quantized LineMoneyMap, determines how many quantum units are left
    /// over and returns them as a money amount to be distributed among the line items.
    fn to_distribute(total: &Money, money_map: &LineMoneyMap) -> Money {
        assert_eq!(total, &total.quantized());
        let combined_sum = money_map
            .values()
            .fold(total.currency().zero(), |accumulation, value| {
                accumulation + value.quantized()
            });
        *total - combined_sum
    }

    /// Given a vector of LineItem vectors sorted by priority, fold them using the priority_total
    /// function, then quantize them, and distribute any leftover quanta.
    fn normalized_lines(
        priority_sets: Vec<Vec<&LineItem>>,
        currency: Currency,
    ) -> (Money, Money, LineMoneyMap) {
        let zero = currency.zero();
        let (total, discount, mut base_subtotals) = priority_sets
            .iter()
            .fold((zero, zero, LineMoneyMap::new()), priority_total);
        let mut subtotals = LineMoneyMap::new();
        for (key, value) in base_subtotals.drain() {
            subtotals.insert(key, value.quantized());
        }
        let difference = to_distribute(&total, &subtotals);
        if difference != zero {
            subtotals = distribute_difference(difference, subtotals)
        }
        (total, discount, subtotals)
    }

    /// Get the total, discounted amount, and full LineMoneyMap with resultant amount for
    /// each line item. If you just need the total, use reckon_lines instead.
    pub fn get_totals(lines: Vec<LineItem>, currency: Currency) -> (Money, Money, LineMoneyMap) {
        let priority_sets = lines_by_priority(lines);
        return normalized_lines(priority_sets, currency);
    }

    /// Given a set of line items, get the total amount. 
    #[wasm_bindgen]
    pub fn reckon_lines(lines: Vec<LineItem>, currency: Currency) -> Money {
        let (value, _discount, _subtotals) = get_totals(lines, currency);
        value
    }

    /// Splits an amount into a number of equal amounts, or as close as possible
    /// if there is a remainder.
    pub fn divide_amount(amount: Money, divisor: u16) -> Vec<Money> {
        assert_eq!(amount, amount.quantized());
        let currency = amount.currency();
        let factor = currency.money_from_dec(Decimal::from(divisor));
        let target_amount = (amount / factor).quantized();
        let mut difference = amount - (target_amount * factor).quantized();
        let step = if difference.amount().is_sign_positive() {
            currency.quantum()
        } else {
            -currency.quantum()
        };
        let zero = currency.zero();
        let mut result: Vec<Money> = vec![];
        for _i in 0..divisor {
            result.push(target_amount);
        }
        /*
        It's probably not possible for it to loop around again, but I'm not a confident
        enough mathematician to disprove it, especially since I'm unsure how having
        discrete values factors in for edge cases. If someone else can be more assured,
        I'm good with simplifying this loop.
         */
        while difference != zero {
            result = result
                .iter()
                .map(|entry| {
                    if difference == zero {
                        return *entry;
                    }
                    difference = difference - step;
                    *entry + step
                })
                .collect();
        }
        result
    }
}

#[cfg(test)]
mod func_tests {
    use crate::data::{LineItem, Money, USD};
    use crate::funcs::lines_by_priority;
    use crate::money;
    use rust_decimal_macros::dec;

    #[test]
    fn test_line_sort() {
        let source = vec![
            LineItem {
                amount: "5",
                priority: 1,
                id: 0,
                ..Default::default()
            },
            LineItem {
                amount: "6",
                priority: 2,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: "7",
                priority: 3,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: "8",
                priority: 3,
                id: 3,
                ..Default::default()
            },
            LineItem {
                amount: "9",
                priority: 2,
                id: 4,
                ..Default::default()
            },
            LineItem {
                amount: "10",
                priority: 0,
                id: 5,
                ..Default::default()
            },
        ];
        let priority_set = lines_by_priority(source.iter().collect());
        assert_eq!(priority_set[0], vec![&source[5]],);
        assert_eq!(priority_set[1], vec![&source[0]]);
        assert_eq!(priority_set[2], vec![&source[1], &source[4]],);
        assert_eq!(priority_set[3], vec![&source[2], &source[3]],);
    }
}
