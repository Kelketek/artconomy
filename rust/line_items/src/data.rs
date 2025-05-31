#[cfg(feature = "python")]
use pyo3::prelude::*;
use rust_decimal::Decimal;
use serde::{Deserialize, Serialize};
use std::collections::{HashMap};
use std::fmt;
use std::fmt::{Debug, Formatter};
use std::hash::Hash;
#[cfg(feature = "python")]
use dict_derive::IntoPyObject;
#[cfg(feature = "wasm")]
use wasm_bindgen::{JsError, JsValue};

/// Serializable Error we can return to the calling applications.
#[derive(Serialize, Clone, Debug, PartialEq)]
pub enum TabulationError {
    /// Standard-form error with string message.
    ErrorString(String),
}

// Note: These 'enums' are constructed as structs with constant
// values so that they serialize and deserialize correctly.
/// Line item types. Line items can have different types that explain their
/// purpose. Some line items are the base price of a product/deliverable,
/// some are extras, and some are various fees like shield or cross-border
/// transfer fees.
#[non_exhaustive]
pub struct LineType;
impl LineType {
    /// Base price
    pub const BASE_PRICE: u16 = 0;
    /// Add-on or discount
    pub const ADD_ON: u16 = 1;
    /// Artconomy's escrow service fee.
    pub const SHIELD: u16 = 2;
    /// Deprecated contingency bonus amount when using Landscape.
    /// Should not actually be used anymore.
    pub const BONUS: u16 = 3;
    /// Amount a commissioner is tipping an artist.
    pub const TIP: u16 = 4;
    /// Additional fee levied when we're running the virtual table.
    pub const TABLE_SERVICE: u16 = 5;
    /// Taxes.
    pub const TAX: u16 = 6;
    /// At the virtual table, if someone wants to buy merch at the same time
    /// as they buy a commission, it goes under this line item.
    pub const EXTRA: u16 = 7;
    /// Fees for premium subscriptions, such as Landscape.
    pub const PREMIUM_SUBSCRIPTION: u16 = 8;
    /// Any other uncategorized fee.
    pub const OTHER_FEE: u16 = 9;
    /// Fee levied for tracking an order but not handling escrow for it.
    pub const DELIVERABLE_TRACKING: u16 = 10;
    /// Fee for processing a transaction where there's no other specific
    /// value-add from us-- such as a tip.
    pub const PROCESSING: u16 = 11;
    /// Line item type that indicates the discrepency between an externally
    /// managed invoice and our expected amount (such as with PayPal
    /// invoicing)
    pub const RECONCILIATION: u16 = 12;
    /// Line item that represents what we expect Stripe to charge us for
    /// this transaction, factoring in the possibility of international
    /// card fees.
    pub const CARD_FEE: u16 = 13;
    /// Line item that covers the expected Stripe fees for transferring to
    /// the artist if they are international.
    pub const CROSS_BORDER_TRANSFER_FEE: u16 = 14;
    /// Line item that covers Stripe's fees for sending a payout to the
    /// artist.
    pub const PAYOUT_FEE: u16 = 15;
    /// Fee assessed by Stripe for maintaining a connected account that is
    /// active in any given month.
    pub const CONNECT_FEE: u16 = 16;
}

/// Categories for transactions. LineItems refer to these in order to make
/// bundling them and creating later transactions easier.
#[non_exhaustive]
pub struct Category;
impl Category {
    /// Artconomy's service fee for escrow payments.
    pub const SHIELD_FEE: u16 = 400;
    /// Amount to be held in escrow
    pub const ESCROW_HOLD: u16 = 401;
    /// Amount to be released from escrow
    pub const ESCROW_RELEASE: u16 = 402;
    /// Amount to be returned to commissioner from escrow
    pub const ESCROW_REFUND: u16 = 403;
    /// Transaction was for subscription dues
    pub const SUBSCRIPTION_DUES: u16 = 404;
    /// Transaction was a refund on subscription dues
    pub const SUBSCRIPTION_REFUND: u16 = 405;
    /// Transaction was a payout
    pub const CASH_WITHDRAWAL: u16 = 406;
    /// Transaction was a fee from a third party service provider
    pub const THIRD_PARTY_FEE: u16 = 408;
    /// The extra money earned for subscribing to premium services and
    /// completing a sale. This is no longer used, we just give a lower
    /// percentage for shield on those sales.
    pub const PREMIUM_BONUS: u16 = 409;
    /// 'Catch all' for any transfers between accounts.
    pub const INTERNAL_TRANSFER: u16 = 410;
    /// Refunds from third party services.
    pub const THIRD_PARTY_REFUNDS: u16 = 411;
    /// For when we make a mistake and need to correct it somehow.
    pub const CORRECTION: u16 = 412;
    /// For fees levied at conventions
    pub const TABLE_HANDLING: u16 = 413;
    /// Taxes
    pub const TAXES: u16 = 414;
    /// For things like inventory items sold at tables alongside the commission, like a pop
    /// socket.
    pub const EXTRA_ITEM: u16 = 415;
    /// For times when we're manually sending money to others for specific services that the
    /// platform itself is paying for.
    pub const VENDOR_PAYMENT: u16 = 416;
    /// Payout reversals
    pub const PAYOUT_REVERSAL: u16 = 417;
    /// Used on items where we collect a slight processing fee, but not shield-level.
    pub const PROCESSING_FEE: u16 = 418;
    /// For tips. Given a slightly different name to make sure it's a distinct value from the
    /// TIP and TIPPING consts.
    pub const TIP_SEND: u16 = 419;
    /// Client charges a card or sends cash as one transaction before forking elsewhere.
    pub const PAYMENT: u16 = 420;
    /// Money added to the Stripe account to cover any fees not otherwise
    /// accounted for, or to pay out vendors for specific services.
    pub const TOP_UP: u16 = 421;
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
#[cfg_attr(feature = "python", derive(FromPyObject))]
#[derive(Serialize, Deserialize, PartialEq, Eq, Hash, Debug, Clone)]
pub struct LineItem {
    /// All line items must have a unique ID, or else they will be clobbered.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub id: i32,
    /// All line items have a priority. This is used for determining which line items this line
    /// item's value effects. For instance, high priority percentages are calculated based on the
    /// value of lower-priority lines.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub priority: i16,
    /// The category of line item this is, such as the base price, an add-on, or some fee.
    #[serde(rename = "type")]
    pub kind: u16,
    /// A static amount this line item represents. Starts as a float to be converted into decimal.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub amount: String,
    /// A (possibly empty) string describing the line item on an invoice.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub description: String,
    /// A previous version of the line item calculations may have already run. If this happens,
    /// we will perform all operations with this frozen value. All line items should have this set
    /// if any do.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub frozen_value: Option<String>,
    /// Used for percentage-based line items, such as proportional fees/discounts. Can be used in
    /// conjunction with amount to add a static amount on top of the percentage.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub percentage: String,
    /// Used for determining the category of line items. This is primarily used by the backend for
    /// later annotation of transactions.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub category: u16,
    /// Whether the percentage calculated should be based on a target amount rather than added on
    /// top. That is, calculate all lower priority items to get their total, then find out the line
    /// item's percentage of that amount. Once found, remove that amount proportionally from all
    /// lower line items so that the total amount doesn't change, but this line item's percentage is
    /// accounted for.
    ///
    /// This is useful for things like credit card fees, where we are charged a percent amount based
    /// on what we ran through the system, and no assumption is made about the line items
    /// of the relevant invoice.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub cascade_percentage: bool,
    /// In contrast to the method used by 'cascade_percentage' on its own, this assumes that the
    /// percentage amount would have been pre-applied to the lower line items and the result is the
    /// total. This is how taxes are normally done-- you have a base amount, and the tax is run on
    /// top of it, as opposed to the other method where the percentage is deducted from whatever
    /// the total ended up being.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub back_into_percentage: bool,
    /// Whether the amount is to be pulled out of lower priority line items rather than added on
    /// top.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub cascade_amount: bool,
}

/// LineItem struct. LineItems have several fields which affect their resolved value.
#[cfg_attr(feature = "python", derive(FromPyObject))]
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct ServicePlan {
    /// The ID of the service plan.
    pub id: i32,
    /// The name of the service plan.
    pub name: String,
    /// Whether the client would be charged the connection fee from Stripe.
    pub connection_fee_waived: bool,
    /// How much we charge for each deliverable we're tracking. Only used when escrow is disabled.
    pub per_deliverable_price: String,
    /// The static portion of the shield price.
    pub shield_static_price: String,
    /// The percentage portion of the shield price.
    pub shield_percentage_price: String,
}

/// Pricing context information. Used to inform the line item generators how they should behave.
#[cfg_attr(feature = "python", derive(FromPyObject))]
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Pricing {
    /// The available plans in the system.
    pub plans: Vec<ServicePlan>,
    /// The minimum price any deliverable with escrow may be.
    pub minimum_price: String,
    /// The service fee percentage for table transactions.
    pub table_percentage: String,
    /// The service fee static amount for table transactions.
    pub table_static: String,
    /// The tax rate for table transactions.
    pub table_tax: String,
    /// The percentage amount for converting to the artist's native currency.
    pub international_conversion_percentage: String,
    /// The preferred service plan. At the time of writing, this is 'Landscape'.
    /// Used in comparisons.
    pub preferred_plan: String,
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
                kind: LineType::ADD_ON,
                frozen_value: None,
                description: String::from(""),
                percentage: String::from("0"),
                category: Category::CORRECTION,
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
#[cfg_attr(feature = "python", derive(IntoPyObject))]
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
