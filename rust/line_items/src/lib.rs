//! Common line item handling code between Artconomy's frontend and backend.
//!
//! Allows for consistent, fast handling of financial data. Quantizes currency
//! values so that no extra/missing pennies are found, and provides flexible distribution
//! of amounts/percentages between line items.
//!

#![warn(missing_docs)]
extern crate console_error_panic_hook;
extern crate core;
extern crate serde_json;
#[cfg(feature = "wasm")]
extern crate wasm_bindgen;

/// Data structures used in line item calculations.
pub mod data;

mod test;

#[cfg(feature = "wasm")]
macro_rules! set_trace {
    () => {
        if thread::panicking() {
            return Err(TabulationError::from(
                "WASM memory corrupted. Refusing to continue.",
            ));
        }
        if cfg!(debug_assertions) {
            panic::set_hook(Box::new(console_error_panic_hook::hook));
        }
    };
}

/// Line item calculation functions used for determining amounts on invoices.
pub mod funcs {
    #[cfg(any(feature = "python", feature = "wasm"))]
    use crate::data::Calculation;
    use crate::data::{
        Account, Category, DeliverableLinesContext, InvoiceLinesContext, LineType, Pricing,
        TipLinesContext,
    };
    use crate::data::{LineDecimalMap, LineItem, TabulationError};
    use crate::{dec_from_string, s};
    #[cfg(feature = "wasm")]
    use js_sys::JsString;
    #[cfg(feature = "python")]
    use pyo3::exceptions::PyValueError;
    #[cfg(feature = "python")]
    use pyo3::prelude::*;
    use rust_decimal::prelude::ToPrimitive;
    use rust_decimal::Decimal;
    use rust_decimal_macros::dec;
    #[cfg(feature = "wasm")]
    use serde::Serialize;
    #[cfg(feature = "wasm")]
    use serde_wasm_bindgen::Serializer;
    use std::cmp::Ordering;
    use std::collections::HashMap;
    use std::error::Error;
    #[cfg(feature = "wasm")]
    use std::panic;
    #[cfg(feature = "wasm")]
    use std::thread;
    #[cfg(feature = "wasm")]
    use wasm_bindgen::prelude::wasm_bindgen;
    #[cfg(feature = "wasm")]
    use wasm_bindgen::JsValue;

    /// Takes a list of line items, and builds them into lists of equal priority.
    pub fn lines_by_priority(lines: Vec<LineItem>) -> Result<Vec<Vec<LineItem>>, TabulationError> {
        let mut priority_sets: HashMap<i16, Vec<LineItem>> = HashMap::new();
        for line in lines.into_iter() {
            if line.priority < line.cascade_under {
                return Err(TabulationError::from(format!(
                    "Line ID {} has higher cascade_under ({}) than priority ({}).",
                    line.id, line.cascade_under, line.priority
                )));
            }
            let priority: i16 = line.priority;
            priority_sets.entry(priority).or_default().push(line);
        }
        let mut prioritized_lines: Vec<Vec<LineItem>> = Vec::new();
        for (_, set) in priority_sets.into_iter() {
            prioritized_lines.push(set);
        }
        prioritized_lines.sort_by(|entry_a, entry_b| entry_a[0].priority.cmp(&entry_b[0].priority));
        Ok(prioritized_lines)
    }

    /// Return a quantized zero-value Money struct with a specific number of zeroes past the
    /// decimal.
    pub fn quantized_zero(quantization: u32) -> Decimal {
        Decimal::new(0, quantization)
    }

    /// Return a Decimal struct with a value of one past a specific number of decimal places.
    /// For example, 1 would be .1, 2 would be .01, and 0 would be 1.
    pub fn quantum(quantization: u32) -> Decimal {
        Decimal::new(1, quantization)
    }

    /// Truncates a Decimal value down to a currency-quantized value. For instance,
    /// 2.034 would become 2.03 with a quantization of 2.
    pub fn quantize(amount: &Decimal, quantization: u32) -> Decimal {
        amount.round_dp_with_strategy(quantization, rust_decimal::RoundingStrategy::ToZero)
    }

    /// Returns a string with the quantized decimal value of the decimal object for precise
    /// reconstruction.
    pub fn value_string(amount: &Decimal, quantization: u32) -> String {
        quantize(amount, quantization).to_string()
    }

    /// Given a total, and an amount that needs to be proportionally pulled from the lines (such as a
    /// discount amount, or a calculated fee based on the total), and a current LineMoneyMap, produces
    /// a new, revalued LineMoneyMap with the Money amounts reduced proportionally in a way that adds
    /// up to the distributed_amount. Note that this reduction is not quantized or rounded.
    fn distribute_reduction(
        total: Decimal,
        distributed_amount: Decimal,
        cascade_under: i16,
        line_values: LineDecimalMap,
    ) -> Result<LineDecimalMap, TabulationError> {
        let mut reductions = LineDecimalMap::new();
        let zero = dec!(0);
        let mut applicable_values = LineDecimalMap::new();
        let mut proxy_total = total;
        for (key, value) in line_values {
            if key.priority < cascade_under {
                applicable_values.insert(key, value);
            } else {
                // Percentage allocations must be proportional to the applicable amount,
                // so total must be reduced.
                proxy_total -= value;
            }
        }
        for (line, original_value) in applicable_values.iter() {
            if original_value < &zero {
                continue;
            }
            let multiplier = if total == zero {
                match applicable_values.len().to_i64() {
                    Some(denominator) => Ok(dec!(1) / Decimal::new(denominator, 0)),
                    None => Err(TabulationError::from(
                        "Way too many lines to distribute to!",
                    )),
                }
            } else {
                Ok(*original_value / proxy_total)
            };
            reductions.insert(line.clone(), distributed_amount * multiplier?);
        }
        Ok(reductions)
    }

    /// Determine the total value of a set of a 'priority set' of lines.
    /// Line items are arranged in a vector of vectors. The outer vector is sorted according to
    /// priority by the 'lines_by_priority' function. They are then folded using this function to
    /// produce a final LineMoneyMap that has resolved all monetary values for all lines.
    #[allow(clippy::ptr_arg)]
    fn priority_total(
        current: (Decimal, Decimal, LineDecimalMap),
        quantization: u32,
        priority_set: Vec<LineItem>,
    ) -> Result<(Decimal, Decimal, LineDecimalMap), TabulationError> {
        /*
        Get the effect on the total of a priority set. First runs any percentage increase,
        then adds in the static amount. Calculates the difference of each separately to make
        sure they're not affecting each other.
        */
        let (current_total, mut discount, subtotals) = current;
        let mut working_subtotals: LineDecimalMap = HashMap::new();
        let mut summable_totals: LineDecimalMap = HashMap::new();
        let mut reductions: Vec<LineDecimalMap> = Vec::new();
        let zero = quantized_zero(quantization);
        let one = dec!(1);
        for line in priority_set.into_iter() {
            let line_amount = dec_from_string!(&line.amount);
            let mut cascaded_amount = quantized_zero(quantization);
            let mut added_amount = quantized_zero(quantization);
            let mut working_amount: Decimal;
            if line.cascade_amount {
                cascaded_amount += line_amount;
            } else {
                added_amount += line_amount;
            }
            let multiplier = dec!(0.01) * dec_from_string!(line.percentage);
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
                cascaded_amount += working_amount;
            } else {
                added_amount += working_amount;
            }
            working_amount += line_amount;
            if cascaded_amount != zero {
                let mut line_values: LineDecimalMap = HashMap::new();
                for key in subtotals.keys() {
                    if key.priority < line.priority {
                        line_values.insert(
                            key.clone(),
                            *subtotals.get(key).ok_or(TabulationError::from(
                                "Line item missing from Subtotals hash. How?",
                            ))?,
                        );
                    }
                }
                let output = distribute_reduction(
                    current_total - discount,
                    cascaded_amount,
                    line.cascade_under,
                    line_values,
                )?;
                reductions.push(output)
            }
            if added_amount != zero {
                summable_totals.insert(line.clone(), added_amount);
            }
            working_subtotals.insert(line, working_amount);
            if working_amount < zero {
                discount += working_amount;
            }
        }
        let mut new_subtotals = subtotals.clone();
        for reduction_set in reductions.iter() {
            for (line, reduction) in reduction_set.iter() {
                new_subtotals.insert(line.clone(), new_subtotals[line] - *reduction);
            }
        }
        let mut add_on: Decimal = zero;
        for operand in summable_totals.values() {
            add_on += *operand;
        }
        let mut new_totals = new_subtotals.clone();
        for (key, value) in working_subtotals.iter() {
            new_totals.insert(key.clone(), *value);
        }
        Ok((
            current_total + quantize(&add_on, quantization),
            discount,
            new_totals,
        ))
    }

    fn redistribution_priority(
        ascending_priority: bool,
        item: &(LineItem, Decimal),
        item2: &(LineItem, Decimal),
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
        (item2_amount - item_amount).to_f64().unwrap()
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
    fn distribute_difference(
        difference: Decimal,
        mut decimal_map: LineDecimalMap,
        quantization: u32,
    ) -> Result<LineDecimalMap, TabulationError> {
        let zero = quantized_zero(quantization);
        let mut sorted_values: Vec<(LineItem, Decimal)> = decimal_map
            .iter()
            .map(|(line, amount)| (line.clone(), *amount))
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
        let amount: Decimal = if remaining > zero {
            quantum(quantization)
        } else {
            zero - quantum(quantization)
        };
        // Values must be in the reverse order of how we want to apply the changes,
        // since we're popping from the end of the vector in the loop below.
        sorted_values.sort_by(|a, b| cmp_to_key(redistribution_priority(difference > zero, a, b)));
        let mut current_values = sorted_values.clone();
        if current_values.is_empty() && remaining != zero {
            return Err(TabulationError::from(
                "No line items to distribute difference to. You may be missing a base price line \
                item, which should be included even if the base price would be zero.",
            ));
        }
        while remaining != zero {
            if current_values.is_empty() {
                current_values.clone_from(&sorted_values)
            }
            let key = current_values.pop().unwrap().0;
            decimal_map.insert(
                key.clone(),
                decimal_map
                    .get(&key)
                    .ok_or(TabulationError::from("Missing key from decimal map. How?"))?
                    + amount,
            );
            remaining -= amount;
        }
        Ok(decimal_map)
    }

    /// Given a quantized total and quantized LineMoneyMap, determines how many quantum units are left
    /// over and returns them as a money amount to be distributed among the line items.
    fn to_distribute(total: &Decimal, money_map: &LineDecimalMap, quantization: u32) -> Decimal {
        assert_eq!(*total, quantize(total, quantization));
        let combined_sum = money_map
            .values()
            .fold(quantized_zero(quantization), |accumulation, value| {
                accumulation + quantize(value, quantization)
            });
        *total - combined_sum
    }

    /// Given a vector of LineItem vectors sorted by priority, fold them using the priority_total
    /// function, then quantize them, and distribute any leftover quanta.
    fn normalized_lines(
        priority_sets: Vec<Vec<LineItem>>,
        quantization: u32,
    ) -> Result<(Decimal, Decimal, LineDecimalMap), TabulationError> {
        let zero = quantized_zero(quantization);
        let mut total = zero;
        let mut discount = zero;
        let mut base_subtotals = LineDecimalMap::new();
        for priority in priority_sets.into_iter() {
            (total, discount, base_subtotals) =
                priority_total((total, discount, base_subtotals), quantization, priority)?;
        }
        let mut subtotals = LineDecimalMap::new();
        for (key, value) in base_subtotals.drain() {
            subtotals.insert(key, quantize(&value, quantization));
        }
        let difference = to_distribute(&total, &subtotals, quantization);
        if difference != zero {
            subtotals = distribute_difference(difference, subtotals, quantization)?;
        }
        Ok((total, discount, subtotals))
    }

    /// Get the total, discounted amount, and full LineMoneyMap with resultant amount for
    /// each line item. If you just need the total, use reckon_lines instead.
    pub fn get_totals(
        lines: Vec<LineItem>,
        quantization: u32,
    ) -> Result<(Decimal, Decimal, LineDecimalMap), TabulationError> {
        let priority_sets = lines_by_priority(lines)?;
        normalized_lines(priority_sets, quantization)
    }

    /// Given a set of line items, get the total amount.
    pub fn reckon_lines(
        lines: Vec<LineItem>,
        quantization: u32,
    ) -> Result<Decimal, Box<dyn Error>> {
        let (value, _discount, _subtotals) = get_totals(lines, quantization)?;
        Ok(value)
    }

    /// Javascript-callable function binding for reckon_lines.
    #[cfg(feature = "wasm")]
    #[wasm_bindgen]
    pub fn js_reckon_lines(
        source_lines: JsValue,
        quantization: u32,
    ) -> Result<JsString, TabulationError> {
        set_trace!();
        let lines = match serde_wasm_bindgen::from_value(source_lines) {
            Ok(result) => result,
            Err(error) => return Err(TabulationError::from(error.to_string())),
        };
        let result = reckon_lines(lines, quantization);
        match result {
            Ok(total) => Ok(JsString::from(total.to_string())),
            Err(error) => Err(TabulationError::from(error.to_string())),
        }
    }

    /// Javascript-callable function binding for get_totals.
    #[cfg(feature = "wasm")]
    #[wasm_bindgen]
    pub fn js_get_totals(
        source_lines: JsValue,
        quantization: u32,
    ) -> Result<JsValue, TabulationError> {
        set_trace!();
        let lines = match serde_wasm_bindgen::from_value(source_lines) {
            Ok(result) => result,
            Err(error) => return Err(TabulationError::from(error.to_string())),
        };
        let (total, discount, source_map) = match get_totals(lines, quantization) {
            Ok(result) => result,
            Err(error) => return Err(TabulationError::from(error.to_string())),
        };
        let mut subtotals = HashMap::<i32, String>::new();
        for (key, value) in source_map.into_iter() {
            subtotals.insert(key.id, value.to_string());
        }
        let result = Calculation {
            total: value_string(&total, quantization),
            discount: value_string(&discount, quantization),
            subtotals,
        };
        match serde_wasm_bindgen::to_value(&result) {
            Ok(result) => Ok(result),
            Err(err) => Err(TabulationError::from(err.to_string())),
        }
    }

    #[cfg(feature = "python")]
    #[pyfunction]
    fn py_get_totals(lines: Vec<LineItem>, quantization: u32) -> PyResult<Calculation> {
        let (total, discount, source_map) = match get_totals(lines, quantization) {
            Ok(result) => result,
            Err(error) => return Err(PyValueError::new_err(error.to_string())),
        };
        let mut subtotals = HashMap::<i32, String>::new();
        for (key, value) in source_map.into_iter() {
            subtotals.insert(key.id, value.to_string());
        }
        Ok(Calculation {
            total: value_string(&total, quantization),
            discount: value_string(&discount, quantization),
            subtotals,
        })
    }

    #[cfg(feature = "python")]
    #[pyfunction]
    fn py_reckon_lines(lines: Vec<LineItem>, quantization: u32) -> PyResult<String> {
        let result = reckon_lines(lines, quantization);
        match result {
            Ok(total) => Ok(total.to_string()),
            Err(error) => Err(PyValueError::new_err(error.to_string())),
        }
    }

    /// A Python module implemented in Rust. The name of this function must match
    /// the `lib.name` setting in the `Cargo.toml`, else Python will not be able to
    /// import the module.
    #[cfg(feature = "python")]
    #[pymodule]
    fn line_items(m: &Bound<'_, PyModule>) -> PyResult<()> {
        m.add_function(wrap_pyfunction!(py_get_totals, m)?)?;
        m.add_function(wrap_pyfunction!(py_reckon_lines, m)?)?;
        m.add_function(wrap_pyfunction!(py_divide_amount, m)?)?;
        m.add_function(wrap_pyfunction!(py_deliverable_lines, m)?)?;
        m.add_function(wrap_pyfunction!(py_tip_fee_lines, m)?)?;
        m.add_class::<LineType>()?;
        m.add_class::<Account>()?;
        m.add_class::<Category>()?;
        Ok(())
    }

    /// Splits an amount into a number of equal amounts, or as close as possible
    /// if there is a remainder.
    pub fn divide_amount(
        amount: Decimal,
        divisor: u16,
        quantization: u32,
    ) -> Result<Vec<Decimal>, TabulationError> {
        if amount != quantize(&amount, quantization) {
            return Err(TabulationError::from(
                "Amount is improperly quantized. Cannot divide.",
            ));
        }
        if divisor == 0 {
            return Err(TabulationError::from("Cannot divide by zero."));
        }
        let factor = Decimal::from(divisor);
        let target_amount = quantize(&(amount / factor), quantization);
        let mut difference = amount - quantize(&(target_amount * factor), quantization);
        let step = if difference.is_sign_positive() {
            quantum(quantization)
        } else {
            -quantum(quantization)
        };
        let zero = quantized_zero(quantization);
        let mut result: Vec<Decimal> = vec![];
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
                    difference -= step;
                    *entry + step
                })
                .collect();
        }
        Ok(result)
    }

    #[cfg(feature = "python")]
    #[pyfunction]
    fn py_divide_amount(
        source_amount: String,
        divisor: u16,
        quantization: u32,
    ) -> PyResult<Vec<String>> {
        let amount = match Decimal::from_str_exact(&source_amount) {
            Ok(result) => result,
            Err(err) => return Err(PyValueError::new_err(err.to_string())),
        };
        let mut entries = match divide_amount(amount, divisor, quantization) {
            Ok(result) => result,
            Err(err) => return Err(PyValueError::new_err(err.to_string())),
        };
        let mut result: Vec<String> = vec![];
        for entry in entries.drain(..) {
            result.push(value_string(&entry, quantization))
        }
        Ok(result)
    }

    /// Line items expected to be on an initialized tip invoice, excluding the tip itself.
    pub fn tip_fee_lines(tip_context: TipLinesContext) -> Result<Vec<LineItem>, TabulationError> {
        let pricing = match tip_context.pricing {
            Some(x) => x,
            None => return Err(TabulationError::from("Pricing not specified.")),
        };
        let mut processing_percentage = dec_from_string!(pricing.processing_percentage);
        if tip_context.international {
            processing_percentage += dec_from_string!(pricing.international_conversion_percentage)
        }
        let mut lines = vec![
            LineItem {
                id: -1,
                priority: 300,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_under: 201,
                kind: LineType::Processing,
                percentage: processing_percentage.to_string(),
                amount: pricing.processing_static,
                cascade_amount: true,
                cascade_percentage: true,
                description: s!(""),
                frozen_value: None,
                category: Category::ProcessingFee,
                back_into_percentage: false,
            },
            LineItem {
                id: -7,
                priority: 350,
                cascade_under: 201,
                amount: pricing.stripe_blended_rate_static,
                percentage: pricing.stripe_blended_rate_percentage,
                cascade_amount: true,
                cascade_percentage: true,
                kind: LineType::CardFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                description: s!(""),
                frozen_value: None,
                category: Category::ThirdPartyFee,
                back_into_percentage: false,
            },
            LineItem {
                id: -9,
                priority: 325,
                cascade_under: 201,
                amount: pricing.stripe_payout_static,
                percentage: pricing.stripe_payout_percentage,
                cascade_amount: true,
                cascade_percentage: true,
                back_into_percentage: false,
                frozen_value: None,
                category: Category::ThirdPartyFee,
                kind: LineType::PayoutFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                description: s!(""),
            },
        ];
        if tip_context.international {
            lines.push(LineItem {
                id: -8,
                priority: 325,
                cascade_under: 201,
                amount: s!("0"),
                percentage: pricing.stripe_payout_cross_border_percentage,
                category: Category::ThirdPartyFee,
                kind: LineType::CrossBorderTransferFee,
                cascade_percentage: true,
                cascade_amount: true,
                back_into_percentage: false,
                destination_user_id: None,
                destination_account: Account::Fund,
                description: s!(""),
                frozen_value: None,
            })
        }
        Ok(lines)
    }

    /// Convenience function for previewing line items that would be given for a particular
    /// product.
    pub fn invoice_lines(
        lines_context: InvoiceLinesContext,
    ) -> Result<Vec<LineItem>, TabulationError> {
        let mut add_on_price: Decimal = match Decimal::from_str_exact(&lines_context.value) {
            Ok(some) => some,
            Err(err) => {
                if lines_context.allow_soft_failure {
                    return Ok(vec![]);
                }
                return Err(TabulationError::from(err.to_string()));
            }
        };
        let base_price: Decimal;
        let table_product: bool;
        let zero = quantized_zero(lines_context.quantization);
        match lines_context.product {
            Some(value) => {
                base_price = match Decimal::from_str_exact(&value.base_price) {
                    Ok(some) => some,
                    Err(err) => {
                        let mut error_string = s!("Could not derive product price. ");
                        error_string.push_str(&err.to_string());
                        return Err(TabulationError::from(&error_string));
                    }
                };
                table_product = value.table_product;
                add_on_price = add_on_price - base_price
            }
            None => {
                base_price = add_on_price;
                add_on_price = zero;
                table_product = false;
            }
        }
        let mut extra_lines = vec![];
        if add_on_price != zero {
            extra_lines.push(LineItem {
                id: -2,
                priority: 100,
                cascade_under: 100,
                kind: LineType::AddOn,
                category: Category::EscrowHold,
                amount: value_string(&add_on_price, lines_context.quantization),
                description: s!(""),
                cascade_amount: false,
                cascade_percentage: false,
                back_into_percentage: false,
                frozen_value: None,
                percentage: s!("0"),
                destination_user_id: Some(lines_context.user_id),
                destination_account: Account::Escrow,
            })
        }
        deliverable_lines(DeliverableLinesContext {
            base_price: value_string(&base_price, lines_context.quantization),
            extra_lines,
            table_product,
            cascade: lines_context.cascade,
            escrow_enabled: lines_context.escrow_enabled,
            international: lines_context.international,
            plan_name: lines_context.plan_name,
            pricing: lines_context.pricing,
            allow_soft_failure: lines_context.allow_soft_failure,
            user_id: lines_context.user_id,
            quantization: lines_context.quantization,
        })
    }

    /// Returns the expected line items for a deliverable.
    pub fn deliverable_lines(
        mut lines_context: DeliverableLinesContext,
    ) -> Result<Vec<LineItem>, TabulationError> {
        let mut lines: Vec<LineItem> = vec![];
        let plan_name: String;

        match lines_context.plan_name {
            Some(name) => {
                plan_name = name;
            }
            None => {
                if lines_context.allow_soft_failure {
                    return Ok(lines);
                }
                return Err(TabulationError::from("No plan name specified."));
            }
        }
        let pricing: Pricing;
        match lines_context.pricing {
            Some(price_spec) => pricing = price_spec,
            None => {
                if lines_context.allow_soft_failure {
                    return Ok(lines);
                }
                return Err(TabulationError::from("Pricing specification not provided."));
            }
        }
        let plan = match pricing.plans.iter().find(|entry| entry.name == plan_name) {
            Some(inner) => inner,
            None => {
                return if lines_context.allow_soft_failure {
                    Ok(lines)
                } else {
                    Err(TabulationError::from(format!(
                        "Could not find {plan_name} in plan list."
                    )))
                }
            }
        };
        // Sanity check.
        match Decimal::from_str_exact(&lines_context.base_price) {
            Ok(_) => {}
            Err(err) => {
                return if lines_context.allow_soft_failure {
                    Ok(lines)
                } else {
                    Err(TabulationError::from(err.to_string()))
                }
            }
        };
        let per_deliverable_price = match Decimal::from_str_exact(&plan.per_deliverable_price) {
            Err(err) => return Err(TabulationError::from(err.to_string())),
            Ok(result) => result,
        };
        if !lines_context
            .extra_lines
            .iter()
            .any(|line| line.kind == LineType::BasePrice)
        {
            lines.push(LineItem {
                id: -1,
                priority: 0,
                cascade_under: 0,
                kind: LineType::BasePrice,
                category: Category::EscrowHold,
                frozen_value: None,
                amount: lines_context.base_price,
                percentage: s!("0"),
                description: s!(""),
                cascade_amount: false,
                cascade_percentage: false,
                back_into_percentage: false,
                destination_account: Account::Escrow,
                destination_user_id: Some(lines_context.user_id),
            });
        }
        let mut calc_lines = lines.clone();
        calc_lines.extend(lines_context.extra_lines.clone());
        let total = match reckon_lines(calc_lines, lines_context.quantization) {
            Ok(some) => some,
            Err(err) => return Err(TabulationError::from(err.to_string())),
        };
        // Escrow is always enabled for table products, though we handle it a bit differently,
        // since for table events we're actually willing to refund the full amount. That means
        // we're not selling the escrow service in such cases-- we're selling the art. It also means
        // we have to add a tax line, since selling art is taxable while selling payment services
        // isn't.
        let escrow_enabled = if total <= quantized_zero(lines_context.quantization) {
            false
        } else {
            lines_context.escrow_enabled || lines_context.table_product
        };
        if lines_context.table_product {
            // TODO: Table changes to numbers now that we're tabulating
            // ours separately from the card charger's.
            lines.push(LineItem {
                id: -3,
                priority: 400,
                cascade_under: 201,
                kind: LineType::TableService,
                category: Category::TableHandling,
                cascade_percentage: lines_context.cascade,
                cascade_amount: true,
                amount: pricing.table_static,
                frozen_value: None,
                description: s!(""),
                percentage: pricing.table_percentage,
                back_into_percentage: false,
                destination_account: Account::Reserve,
                destination_user_id: None,
            });
            lines.push(LineItem {
                id: -4,
                priority: 700,
                cascade_under: 201,
                kind: LineType::Tax,
                description: s!(""),
                category: Category::Taxes,
                cascade_percentage: lines_context.cascade,
                cascade_amount: lines_context.cascade,
                percentage: pricing.table_tax,
                back_into_percentage: true,
                amount: s!("0"),
                frozen_value: None,
                // TODO: Do these staging accounts actually help us or just make accounting
                // more complicated? Ask the accountant. It may be especially useless for table
                // cases.
                destination_account: Account::MoneyHoleStage,
                destination_user_id: None,
            })
        } else if escrow_enabled {
            let mut shield_percentage_price = dec_from_string!(&plan.shield_percentage_price);
            // We include the extra bump onto our shield price for international artists.
            // This allows us to incorperate any additional conversion fees that may be there.
            // We could have made this a separate line, but to do so, we would need to mark it for
            // our primary concern, foreign exchange fees. However, just because a user is
            // international, doesn't mean there's a conversion.
            //
            // For example, there are several countries that have 'dollarized'. This means they use
            // the US dollar locally to some degree, which means such a fee wouldn't make sense.
            // It's also possible that there are US dollar accounts in countries that normally don't
            // have them, which would be an edge case, but I can't rule it out. Hopefully, we won't
            // have any domestic accounts with foreign currency-- which is the one case we aren't
            // covering here.
            //
            // Due to the ambiguity of circumstances, we just say we add on an international
            // surcharge of 1% from our end, rather than trying to certainly earmark it.
            if lines_context.international {
                let international_conversion_percentage =
                    dec_from_string!(&pricing.international_conversion_percentage);
                shield_percentage_price += international_conversion_percentage
            }
            lines.push(LineItem {
                id: -5,
                priority: 330,
                cascade_under: 201,
                kind: LineType::Shield,
                description: s!(""),
                category: Category::ShieldFee,
                cascade_percentage: lines_context.cascade,
                cascade_amount: lines_context.cascade,
                amount: plan.shield_static_price.clone(),
                frozen_value: None,
                percentage: shield_percentage_price.to_string(),
                back_into_percentage: false,
                destination_account: Account::Fund,
                destination_user_id: None,
            })
        } else if per_deliverable_price > dec!(0) {
            lines.push(LineItem {
                id: -6,
                priority: 300,
                cascade_under: 201,
                kind: LineType::DeliverableTracking,
                description: s!(""),
                category: Category::SubscriptionDues,
                cascade_percentage: lines_context.cascade,
                cascade_amount: lines_context.cascade,
                amount: plan.per_deliverable_price.clone(),
                frozen_value: None,
                percentage: s!("0"),
                back_into_percentage: false,
                destination_account: Account::Fund,
                destination_user_id: None,
            })
        }
        // If any escrow/payment handling is done, we need to add the lines for upstream fees.
        if escrow_enabled {
            lines.push(LineItem {
                id: -7,
                priority: 350,
                cascade_under: 201,
                amount: pricing.stripe_blended_rate_static,
                percentage: pricing.stripe_blended_rate_percentage,
                cascade_amount: lines_context.cascade,
                cascade_percentage: lines_context.cascade,
                kind: LineType::CardFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                description: s!(""),
                frozen_value: None,
                category: Category::ThirdPartyFee,
                back_into_percentage: false,
            });
            lines.push(LineItem {
                id: -9,
                priority: 325,
                cascade_under: 201,
                amount: pricing.stripe_payout_static,
                percentage: pricing.stripe_payout_percentage,
                cascade_amount: lines_context.cascade,
                cascade_percentage: lines_context.cascade,
                back_into_percentage: false,
                frozen_value: None,
                category: Category::ThirdPartyFee,
                kind: LineType::PayoutFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                description: s!(""),
            });
            if lines_context.international {
                lines.push(LineItem {
                    id: -8,
                    priority: 325,
                    cascade_under: 201,
                    amount: s!("0"),
                    percentage: pricing.stripe_payout_cross_border_percentage,
                    category: Category::ThirdPartyFee,
                    kind: LineType::CrossBorderTransferFee,
                    cascade_percentage: lines_context.cascade,
                    cascade_amount: lines_context.cascade,
                    back_into_percentage: false,
                    destination_user_id: None,
                    destination_account: Account::Fund,
                    description: s!(""),
                    frozen_value: None,
                })
            }
            if !plan.connection_fee_waived {
                lines.push(LineItem {
                    id: -10,
                    priority: 325,
                    cascade_under: 201,
                    amount: pricing.stripe_active_account_monthly_fee,
                    percentage: s!("0"),
                    category: Category::ThirdPartyFee,
                    kind: LineType::ConnectFee,
                    destination_user_id: None,
                    destination_account: Account::Fund,
                    cascade_percentage: lines_context.cascade,
                    cascade_amount: lines_context.cascade,
                    back_into_percentage: false,
                    description: s!(""),
                    frozen_value: None,
                })
            }
        }
        for entry in lines_context.extra_lines.drain(..) {
            lines.push(entry)
        }
        Ok(lines)
    }

    /// JavaScript binding for invoice_lines
    #[cfg(feature = "wasm")]
    #[wasm_bindgen]
    pub fn js_invoice_lines(provided_lines_context: JsValue) -> Result<JsValue, TabulationError> {
        set_trace!();
        let lines_context: InvoiceLinesContext =
            match serde_wasm_bindgen::from_value(provided_lines_context) {
                Ok(result) => result,
                Err(error) => return Err(TabulationError::from(error.to_string())),
            };
        let lines = invoice_lines(lines_context);
        let serializer = Serializer::json_compatible();
        match Serialize::serialize(&lines, &serializer) {
            Ok(result) => Ok(result),
            Err(err) => Err(TabulationError::from(err.to_string())),
        }
    }

    /// JavaScript binding for deliverable_lines
    #[cfg(feature = "wasm")]
    #[wasm_bindgen]
    pub fn js_deliverable_lines(
        provided_lines_context: JsValue,
    ) -> Result<JsValue, TabulationError> {
        set_trace!();
        let lines_context: DeliverableLinesContext =
            match serde_wasm_bindgen::from_value(provided_lines_context) {
                Ok(result) => result,
                Err(error) => return Err(TabulationError::from(error.to_string())),
            };
        let lines = deliverable_lines(lines_context);
        let serializer = Serializer::json_compatible();
        match Serialize::serialize(&lines, &serializer) {
            Ok(result) => Ok(result),
            Err(err) => Err(TabulationError::from(err.to_string())),
        }
    }

    /// Python binding for deliverable_lines
    #[cfg(feature = "python")]
    #[pyfunction]
    pub fn py_deliverable_lines(
        provided_lines_context: DeliverableLinesContext,
    ) -> PyResult<Vec<LineItem>> {
        match deliverable_lines(provided_lines_context) {
            Ok(some) => Ok(some),
            Err(error) => Err(PyValueError::new_err(error.to_string())),
        }
    }

    /// Python binding for tip_fee_lines
    #[cfg(feature = "python")]
    #[pyfunction]
    pub fn py_tip_fee_lines(provided_lines_context: TipLinesContext) -> PyResult<Vec<LineItem>> {
        match tip_fee_lines(provided_lines_context) {
            Ok(some) => Ok(some),
            Err(error) => Err(PyValueError::new_err(error.to_string())),
        }
    }

    /// Sum values in a vector, returning the result. Quantization sets the zero-level quantization,
    /// but if an input has a higher level of precision, the output may be normalized to that.
    pub fn sum(values: Vec<String>, quantization: u32) -> Result<Decimal, TabulationError> {
        let mut total = quantized_zero(quantization);
        for entry in values {
            total += dec_from_string!(entry)
        }
        Ok(total)
    }

    /// JS binding for sum
    #[cfg(feature = "wasm")]
    #[wasm_bindgen]
    pub fn js_sum(raw_values: JsValue, quantization: u32) -> Result<JsString, TabulationError> {
        let values: Vec<String> = match serde_wasm_bindgen::from_value(raw_values) {
            Ok(result) => result,
            Err(err) => return Err(TabulationError::from(err.to_string())),
        };
        match sum(values, quantization) {
            Ok(val) => Ok(JsString::from(val.to_string())),
            Err(err) => Err(err),
        }
    }
}

#[cfg(test)]
mod func_tests {
    use crate::data::{LineItem, TabulationError};
    use crate::funcs::{lines_by_priority, sum};
    use crate::s;
    use pretty_assertions::assert_eq;
    use rust_decimal_macros::dec;

    #[test]
    fn test_line_sort() {
        let input = vec![
            LineItem {
                amount: s!("5"),
                priority: 1,
                id: 0,
                ..Default::default()
            },
            LineItem {
                amount: s!("6"),
                priority: 2,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: s!("7"),
                priority: 3,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: s!("8"),
                priority: 3,
                id: 3,
                ..Default::default()
            },
            LineItem {
                amount: s!("9"),
                priority: 2,
                id: 4,
                ..Default::default()
            },
            LineItem {
                amount: s!("10"),
                priority: 0,
                id: 5,
                ..Default::default()
            },
        ];
        let priority_set = lines_by_priority(input.clone()).unwrap();
        assert_eq!(priority_set[0], vec![input[5].clone()]);
        assert_eq!(priority_set[1], vec![input[0].clone()]);
        assert_eq!(priority_set[2], vec![input[1].clone(), input[4].clone()]);
        assert_eq!(priority_set[3], vec![input[2].clone(), input[3].clone()]);
    }

    #[test]
    fn test_sanity_check() {
        let input = vec![
            LineItem {
                amount: s!("10.00"),
                priority: 0,
                cascade_under: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: s!("5.00"),
                priority: 100,
                cascade_under: 100,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: s!("2.00"),
                priority: 200,
                cascade_under: 300,
                cascade_amount: true,
                id: 3,
                ..Default::default()
            },
        ];
        let result = lines_by_priority(input);
        assert_eq!(
            result,
            Err(TabulationError::from(
                "Line ID 3 has higher cascade_under (300) than priority (200)."
            )),
        );
    }

    #[test]
    fn test_sum() {
        let result = sum(vec![s!("5.00"), s!("10.00"), s!("2.56")], 2);
        assert_eq!(result, Ok(dec!(17.56)))
    }

    #[test]
    fn test_sum_invalid_string() {
        let result = sum(vec![s!("5.00"), s!("bork"), s!("2.56")], 2);
        assert_eq!(
            result,
            Err(TabulationError::from("Invalid decimal: unknown character"))
        )
    }

    #[test]
    fn test_sum_zero() {
        let result = sum(vec![], 2);
        assert_eq!(
            result.expect("Had an error when summing.").to_string(),
            s!("0.00"),
        )
    }

    #[test]
    fn test_sum_larger_precision_than_quantized() {
        let result = sum(vec![s!("0.123")], 2);
        assert_eq!(
            result.expect("Had an error when summing.").to_string(),
            s!("0.123"),
        )
    }
}
