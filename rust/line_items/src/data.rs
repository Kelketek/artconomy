#[cfg(feature = "python")]
use pyo3::prelude::*;
use rust_decimal::Decimal;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
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

/// Distinct accounts that line items may deposit into.
#[non_exhaustive]
pub struct Account;
impl Account {
    /// Account types
    pub const CARD: u16 = 300;
    /// Payout account on the payout provider. This is the artist's Stripe account, at
    /// present.
    pub const PAYOUT_ACCOUNT: u16 = 301;
    /// Escrow holdings account for a particular user.
    pub const ESCROW: u16 = 302;
    /// Finalized earnings, available for withdrawal.
    pub const HOLDINGS: u16 = 303;
    /// DEPRECATED: This used to be true and is no longer so. We now determine at the time of
    /// payment whether the amount to be taken is more or less due to landscape service.
    /// OLD NOTE, NO LONGER CORRECT: All fees put the difference for premium bonus into
    /// reserve until an order is complete. When complete, these amounts are deposited into
    /// either the cash account of Artconomy, or added to the user's holdings.
    pub const RESERVE: u16 = 304;
    /// Earnings for which we have not yet subtracted card/bank transfer fees. DEPRECATED:
    /// Use FUND instead.
    pub const UNPROCESSED_EARNINGS: u16 = 305;
    /// These two fee types will be used to keep track of fees that have been paid out to card
    /// processors.
    pub const CARD_TRANSACTION_FEES: u16 = 306;
    /// Card fees that aren't directly related to a specific transaction.
    pub const CARD_MISC_FEES: u16 = 307;

    /// Fees from performing bank transfers.
    pub const BANK_TRANSFER_FEES: u16 = 308;
    /// Fees for other ACH-related items, like customer onboarding fees.
    pub const BANK_MISC_FEES: u16 = 309;

    /// Tax held here until order finalized
    pub const MONEY_HOLE_STAGE: u16 = 310;

    /// Where taxes go
    pub const MONEY_HOLE: u16 = 311;

    /// Similar to money hole, when money is stolen and there's no getting it back,
    /// but a private actor instead of a public one. :/
    pub const FRAUD_LOSS: u16 = 312;

    /// Staging account where the actual transaction coming in (like a card payment) is sent
    /// before splitting into different accounts from there.
    pub const FUND: u16 = 313;

    /// Used to keep track of money that landed in the user's stripe account and which they
    /// are trying to withdraw.
    pub const PAYOUT_EXTRACT: u16 = 314;

    /// For when a customer gives us cash, like at an event.
    pub const CASH_DEPOSIT: u16 = 407;

    // These next accounts are used to generate reports about what money was actually
    // deposited into the payee's currency for tax purposes.

    /// The balance of this account will always be negative (or zero) and potentially
    /// incalculable because the currency could vary.
    pub const PAYOUT_MIRROR_SOURCE: u16 = 500;
    /// The balance of this account will always be positive (or zero) and potentially
    /// incalculable because the currency could vary.
    pub const PAYOUT_MIRROR_DESTINATION: u16 = 501;
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
#[cfg_attr(feature = "python", derive(FromPyObject, IntoPyObject))]
#[derive(Serialize, Deserialize, PartialEq, Eq, Hash, Debug, Clone)]
pub struct LineItem {
    /// All line items must have a unique ID, or else they will be clobbered.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub id: i32,
    /// All line items have a priority. This is used for determining atop which this line item's
    /// value is calculated. So if the percentage is 5% and the lines at lower priority total to
    /// 100, this line would be 5%, before any other modifiers applied by 'cascade_from'
    #[cfg_attr(feature = "python", pyo3(item))]
    pub priority: i16,
    /// Any line whose priority is lower than this value will be taken from if cascading is
    /// enabled through cascade_amount and/or cascade_percentage as applicable.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub cascade_under: i16,
    /// The category of line item this is, such as the base price, an add-on, or some fee.
    #[serde(rename = "type")]
    #[cfg_attr(feature = "python", pyo3(item))]
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
    /// Destination user ID for the line item. This is None if the destination account is the
    /// platform, and an int if it's any other user. For some testing calculations, we might set
    /// this to -1.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub destination_user_id: Option<i64>,
    /// Account type for the destination user to credit this to, such as their escrow account or
    /// their holdings.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub destination_account: u16,
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

/// Products. They are listings in our marketplace.
#[cfg_attr(feature = "python", derive(FromPyObject))]
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Product {
    /// The ID of the product.
    pub id: u32,
    /// The name of the product.
    pub name: String,
    /// The base price of the product.
    pub base_price: String,
    /// Whether the product is intended to be sold at the virtual table.
    pub table_product: bool,
    /// Whether the fees for the product should be cascaded.
    pub cascade_fees: bool,
    /// Whether the product can be upgraded for escrow.
    pub escrow_upgradable: bool,
    /// Whether the product is on escrow by default.
    pub escrow_enabled: bool,
}

/// ServicePlan struct. ServicePlans define pricing structures for individual users.
#[cfg_attr(feature = "python", derive(FromPyObject))]
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct ServicePlan {
    /// The ID of the service plan.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub id: i32,
    /// The name of the service plan.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub name: String,
    /// Whether the client would be charged the connection fee from Stripe.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub connection_fee_waived: bool,
    /// How much we charge for each deliverable we're tracking. Only used when escrow is disabled.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub per_deliverable_price: String,
    /// How many orders can be simultaneously tracked on this plan.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub max_simultaneous_orders: u16,
    /// Whether waitlisting is permitted with this plan.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub waitlisting: bool,
    /// Whether the plan permits invoicing through PayPal.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub paypal_invoicing: bool,
    /// The static portion of the shield price.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub shield_static_price: String,
    /// The percentage portion of the shield price.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub shield_percentage_price: String,
}

/// DeliverableLinesContext. Used as the arguments for the deliverable_line_items function.
#[cfg_attr(feature = "python", derive(FromPyObject))]
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct DeliverableLinesContext {
    /// The default base price for a deliverable, if a base price line isn't included in the
    /// extra_lines field.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub base_price: String,
    /// Whether the associated product is a table product.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub table_product: bool,
    /// Whether the seller's fees should be cascaded from the total, rather than applied atop.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub cascade: bool,
    /// Whether escrow is enabled for this deliverable.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub escrow_enabled: bool,
    /// Whether there's international interchange fees that will be due for this product.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub international: bool,
    /// Any lines to add in for the result. If a BASE_PRICE type line item is included,
    /// No BASE_PRICE line item will be produced, nor will the existing one be updated.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub extra_lines: Vec<LineItem>,
    /// The name of the plan to derive fee structures from.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub plan_name: Option<String>,
    /// Pricing variables and context, including available plans.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub pricing: Option<Pricing>,
    /// The ID of the user that is issuing the invoice.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub user_id: i64,
    /// Allows return of an empty vector if base_price is invalid,
    /// plan_name is unset or pricing isn't set.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub allow_soft_failure: bool,
    /// The level of after-decimal precision desired in calculations.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub quantization: u32,
}

/// DeliverableLinesContext. Used as the arguments for the deliverable_line_items function.
#[cfg_attr(feature = "python", derive(FromPyObject))]
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct InvoiceLinesContext {
    /// The name of the plan to derive fee structures from.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub plan_name: Option<String>,
    /// Pricing variables and context, including available plans.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub pricing: Option<Pricing>,
    /// Base price for a deliverable.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub value: String,
    /// Whether there's international interchange fees that will be due for this product.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub international: bool,
    /// Whether escrow is enabled for this deliverable.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub escrow_enabled: bool,
    /// Whether the seller's fees should be cascaded from the total, rather than applied atop.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub product: Option<Product>,
    /// Whether the seller's fees should be cascaded from the total.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub cascade: bool,
    /// The ID of the user that is issuing the invoice.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub user_id: i64,
    /// Allows return of an empty vector if base_price is invalid,
    /// plan_name is unset or pricing isn't set.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub allow_soft_failure: bool,
    /// The level of after-decimal precision desired in calculations.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub quantization: u32,
}

/// Pricing context information. Used to inform the line item generators how they should behave.
#[cfg_attr(feature = "python", derive(FromPyObject))]
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct Pricing {
    /// The available plans in the system.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub plans: Vec<ServicePlan>,
    /// The minimum price any deliverable with escrow may be.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub minimum_price: String,
    /// The service fee percentage for table transactions.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub table_percentage: String,
    /// The service fee static amount for table transactions.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub table_static: String,
    /// The tax rate for table transactions.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub table_tax: String,
    /// The percentage amount for converting to the artist's native currency.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub international_conversion_percentage: String,
    /// The preferred service plan. At the time of writing, this is 'Landscape'.
    /// Used in comparisons.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub preferred_plan: String,
    /// A blended percentage rate that we expect Stripe to collect. It can vary based on various
    /// circumstances, such as which card the country is from. This represents our historical
    /// average.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub stripe_blended_rate_percentage: String,
    /// The static amount that is part of Stripe's charge fee. This includes static add-ons like the
    /// radar fee from their end.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub stripe_blended_rate_static: String,
    /// The percentage additional that Stripe collects on top for international conversion of
    /// money they transfer overseas.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub stripe_payout_cross_border_percentage: String,
    /// The amount of money stripe collects for each active account each month.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub stripe_active_account_monthly_fee: String,
    /// Static amount levied on payouts.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub stripe_payout_static: String,
    /// Percentage amount levied on payouts.
    #[cfg_attr(feature = "python", pyo3(item))]
    pub stripe_payout_percentage: String,
}

/// Only used in tests, so this should not have an opportunity to roll over.
static mut LINE_COUNTER: i32 = 0;

impl Default for LineItem {
    fn default() -> Self {
        unsafe {
            LINE_COUNTER += 1;
            LineItem {
                id: LINE_COUNTER,
                priority: 0,
                cascade_under: 0,
                amount: String::from("0"),
                kind: LineType::ADD_ON,
                frozen_value: None,
                description: String::from(""),
                percentage: String::from("0"),
                category: Category::CORRECTION,
                cascade_percentage: false,
                back_into_percentage: false,
                cascade_amount: false,
                destination_user_id: None,
                destination_account: 0,
            }
        }
    }
}

/// Only used in tests, so this should not have an opportunity to roll over.
static mut PRODUCT_COUNTER: u32 = 0;

impl Default for Product {
    fn default() -> Self {
        unsafe {
            Product {
                id: PRODUCT_COUNTER,
                name: String::from("Test Product"),
                base_price: String::from("10.00"),
                table_product: false,
                cascade_fees: true,
                escrow_upgradable: false,
                escrow_enabled: true,
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

/// Quick conversion macro that early returns a TabulationError upon failure.
#[macro_export]
macro_rules! dec_from_string {
    ($str: expr) => {
        match Decimal::from_str_exact(&$str) {
            Ok(some) => some,
            Err(err) => return Err(TabulationError::from(err.to_string())),
        }
    };
}
