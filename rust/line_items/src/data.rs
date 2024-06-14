use derive_getters::Getters;
use rust_decimal::Decimal;
use rust_decimal_macros::dec;
use std::cmp::{Ordering, PartialOrd};
use std::collections::HashMap;
use std::fmt;
use std::fmt::{Debug, Formatter};
use std::ops::{Add, Div, Mul, Neg, Sub};
use serde::Serialize;

/// Currency definition struct. Currency definitions determine how currencies are displayed
/// and how they are quantized.
#[derive(Copy, Clone, Hash, Getters, Serialize, Deserialize)]
pub struct Currency {
    code: &'static str,
    prefix: Option<&'static str>,
    quantization: u32,
}

impl Currency {
    /// Creates a new Currency definition struct. Currency definition structs should always be
    /// instantiated with static lifetime values for their codes and prefixes. We may eventually
    /// require Currency structs themselves to be in the static lifetime, since they are unchanging
    /// and frequently referenced.
    pub fn new(code: &'static str, prefix: Option<&'static str>, quantization: u32) -> Currency {
        Currency {
            code,
            prefix,
            quantization,
        }
    }
    /// Truncates a Decimal value down to a currency-quantized value. For instance,
    /// $2.034 would become $2.03.
    pub fn quantize(&self, amount: &Decimal) -> Decimal {
        // Truncate the decimal amount to a value that is valid for the current currency type.
        amount.round_dp_with_strategy(self.quantization, rust_decimal::RoundingStrategy::ToZero)
    }
    /// Return a quantized zero-value Money struct for this currency. For instance, dollars would
    /// return $0.00.
    pub fn zero(&self) -> Money {
        Money {
            amount: Decimal::new(0, self.quantization),
            currency: *self,
        }
    }
    /// Convert a decimal amount into a Money struct based on this currency. Does not quantize.
    pub fn to_money(&self, amount: Decimal) -> Money {
        Money {
            amount,
            currency: *self,
        }
    }
    /// Return a Money struct containing one quantum of this currency. For instance, dollars would
    /// return $.01.
    pub fn quantum(&self) -> Money {
        Money {
            amount: Decimal::new(1, self.quantization),
            currency: *self,
        }
    }
}

/// USD is the 'default' currency for our site, so it is provided for convenience, especially in
/// tests.
pub const USD: Currency = Currency {
    code: "USD",
    prefix: Some("$"),
    quantization: 2,
};

/// Money struct. Represents an amount of a specific currency. This amount will not be automatically
/// quantized, allowing you to perform mathematical operations with more precision until it is time
/// to resolve them.
#[derive(Copy, Clone, Hash, Getters)]
pub struct Money {
    currency: Currency,
    amount: Decimal,
}


/// LineItem struct. LineItems have several fields which affect their resolved value.
#[derive(Hash, Eq, PartialEq, Debug, Serialize, Deserialize)]
pub struct LineItem {
    /// All line items must have a unique ID, or else they will be clobbered.
    pub id: u32,
    /// All line items have a priority. This is used for determining which line items this line
    /// item's value effects. For instance, high priority percentages are calculated based on the
    /// value of lower-priority lines.
    pub priority: i16,
    /// A static amount this line item represents.
    pub amount: Decimal,
    /// A previous version of the line item calculations may have already run. If this happens,
    /// we will perform all operations with this frozen value. All line items should have this set
    /// if any do.
    pub frozen_value: Option<Decimal>,
    /// Used for percentage-based line items, such as proportional fees/discounts. Can be used in
    /// conjunction with amount to add a static amount on top of the percentage.
    pub percentage: Decimal,
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
static mut COUNTER: u32 = 0;

impl Default for LineItem {
    fn default() -> Self {
        unsafe {
            COUNTER += 1;
            LineItem {
                id: COUNTER,
                priority: 0,
                amount: dec!(0),
                frozen_value: None,
                percentage: dec!(0),
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

/// LineMoneyMaps are hashes that relate LineItem references to the Money values they've resolved to
/// via the functions in this library.
pub type LineMoneyMap<'a> = HashMap<&'a LineItem, Money>;

impl Money {
    /// Creates a new Money struct. Does not quantize the decimal amount.
    pub fn new(amount: Decimal, currency: Currency) -> Money {
        Money { amount, currency }
    }
    /// Returns a new Money struct with a truncated, quantized amount appropriate for the Money
    /// struct's currency.
    pub fn quantized(&self) -> Money {
        Money {
            currency: self.currency,
            amount: self.currency.quantize(&self.amount),
        }
    }
}

impl Neg for Money {
    type Output = Self;
    fn neg(self) -> Self::Output {
        Money {
            currency: self.currency,
            amount: -self.amount,
        }
    }
}

impl fmt::Display for Money {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        match self.currency.prefix {
            Some(prefix) => {
                write!(
                    f,
                    "{}{}{}",
                    if self.amount.is_sign_negative() {
                        "-"
                    } else {
                        ""
                    },
                    prefix,
                    self.amount.abs()
                )
            }
            None => {
                write!(f, "{} {}", self.amount, self.currency.code)
            }
        }
    }
}

impl Debug for Money {
    fn fmt(&self, f: &mut Formatter<'_>) -> fmt::Result {
        fmt::Display::fmt(&self, f)
    }
}

macro_rules! impl_math_ops {
    ($trait:ident, $method:ident) => {
        impl $trait for Money {
            type Output = Money;

            fn $method(self, rhs: Self) -> Self::Output {
                if self.currency.code != rhs.currency.code {
                    panic!(
                        "Attempted mathematical operation between disparate currencies: {} and {}",
                        self.currency.code, rhs.currency.code
                    );
                }

                Money {
                    currency: self.currency,
                    amount: self.amount.$method(rhs.amount),
                }
            }
        }
    };
}

macro_rules! impl_cmp_op {
    ($method:ident) => {
        fn $method(&self, rhs: &Money) -> bool {
            if self.currency.code != rhs.currency.code {
                panic!(
                    "Attempted mathematical operation between disparate currencies: {} and {}",
                    self.currency.code, rhs.currency.code
                );
            }
            self.amount.$method(rhs.amount())
        }
    };
}

/// Short, readable macro for creating a Money struct. money!(1.25, USD). USD must be a currency
/// struct in scope.
#[macro_export]
macro_rules! money {
    ($amount:expr, $currency:ident) => {
        Money::new(dec!($amount), $currency)
    };
}

impl_math_ops!(Add, add);
impl_math_ops!(Sub, sub);
// Due to the constraints of the trait, money amounts must be multiplied/divided by other money
// amounts, rather than decimal amounts, which makes more sense. We could have used methods instead,
// but operator overloading seemed easier to read.
impl_math_ops!(Mul, mul);
impl_math_ops!(Div, div);

impl PartialEq for Money {
    impl_cmp_op!(eq);
}

impl Eq for Money {}

impl PartialOrd for Money {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        self.amount.partial_cmp(other.amount())
    }
    impl_cmp_op!(lt);
    impl_cmp_op!(le);
    impl_cmp_op!(gt);
    impl_cmp_op!(ge);
}
