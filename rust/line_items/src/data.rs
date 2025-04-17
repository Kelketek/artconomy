#[cfg(feature = "python")]
use pyo3::prelude::*;
use rust_decimal::Decimal;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap};
use std::fmt;
use std::fmt::{Debug, Formatter};
use std::hash::Hash;
#[cfg(feature = "wasm")]
use wasm_bindgen::{JsError, JsValue};

/// Serializable Error we can return to the calling applications.
#[derive(Serialize, Clone, Debug, PartialEq)]
pub enum TabulationError {
    /// Standard-form error with string message.
    ErrorString(String),
}

#[cfg(feature = "wasm")]
impl From<TabulationError> for JsValue {
    fn from(val: TabulationError) -> Self {
        JsValue::from(JsError::from(val))
    }
}

impl<S> From<S> for TabulationError
where
    S: Into<String>,
{
    #[inline]
    fn from(from: S) -> Self {
        Self::ErrorString(from.into())
    }
}

impl std::error::Error for TabulationError {}

impl core::fmt::Display for TabulationError {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        match *self {
            Self::ErrorString(ref err) => f.pad(err),
        }
    }
}

/// LineItem struct. LineItems have several fields which affect their resolved value.
#[cfg_attr(feature = "python", pyclass)]
#[derive(Serialize, Deserialize, PartialEq, Eq, Hash, Debug, Clone)]
pub struct LineItem {
    /// All line items must have a unique ID, or else they will be clobbered.
    pub id: i32,
    /// All line items have a priority. This is used for determining which line items this line
    /// item's value effects. For instance, high priority percentages are calculated based on the
    /// value of lower-priority lines.
    pub priority: i16,
    /// A static amount this line item represents. Starts as a float to be converted into decimal.
    pub amount: String,
    /// A previous version of the line item calculations may have already run. If this happens,
    /// we will perform all operations with this frozen value. All line items should have this set
    /// if any do.
    pub frozen_value: Option<String>,
    /// Used for percentage-based line items, such as proportional fees/discounts. Can be used in
    /// conjunction with amount to add a static amount on top of the percentage.
    pub percentage: String,
    /// Whether the percentage calculated should be based on a target amount rather than added on
    /// top. That is, calculate all lower priority items to get their total, then find out the line
    /// item's percentage of that amount. Once found, remove that amount proportionally from all
    /// lower line items so that the total amount doesn't change, but this line item's percentage is
    /// accounted for.
    ///
    /// This is useful for things like credit card fees, where we are charged a percent amount based
    /// on what we ran through the system, and no assumption is made about the line items
    /// of the relevant invoice.
    pub cascade_percentage: bool,
    /// In contrast to the method used by 'cascade_percentage' on its own, this assumes that the
    /// percentage amount would have been pre-applied to the lower line items and the result is the
    /// total. This is how taxes are normally done-- you have a base amount, and the tax is run on
    /// top of it, as opposed to the other method where the percentage is deducted from whatever
    /// the total ended up being.
    pub back_into_percentage: bool,
    /// Whether the amount is to be pulled out of lower priority line items rather than added on
    /// top.
    pub cascade_amount: bool,
}

/// Only used in tests, so this should not have an opportunity to roll over.
static mut COUNTER: i32 = 0;

impl Default for LineItem {
    fn default() -> Self {
        unsafe {
            COUNTER += 1;
            LineItem {
                id: COUNTER,
                priority: 0,
                amount: String::from("0"),
                frozen_value: None,
                percentage: String::from("0"),
                cascade_percentage: false,
                back_into_percentage: false,
                cascade_amount: false,
            }
        }
    }
}

impl fmt::Display for LineItem {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        Debug::fmt(&self, f)
    }
}

/// LineDecimalMaps are hashes that relate LineItem references to the Decimal values they've
/// resolved to via the functions in this library.
pub type LineDecimalMap = HashMap<LineItem, Decimal>;

/// Intermediate map used for serializing to the frontend.
pub type IdToMoneyVal = HashMap<i32, String>;

/// 'Calculation' structure used as the basis of the return value for JS-based calls to the line
/// item functions.
#[derive(Serialize, Deserialize)]
#[cfg_attr(feature = "python", pyclass)]
pub struct Calculation {
    /// Total value of the reckoned line items
    pub total: String,
    /// Total value of all applied discounts
    pub discount: String,
    /// Map of line item IDs to string values representing the amount each line item reckons to.
    pub subtotals: IdToMoneyVal,
}

/// Shorthand for String::from, which is used often in tests, especially.
#[macro_export]
macro_rules! s {
    ($str: expr) => {
        String::from($str)
    };
}
