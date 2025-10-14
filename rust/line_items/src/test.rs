#[cfg(test)]
mod interface_tests {
    use crate::data::{LineItem, TabulationError};
    use crate::funcs::{frozen_lines, get_totals, reckon_lines};
    use crate::s;
    use ntest::timeout;
    use pretty_assertions::assert_eq;
    use rust_decimal_macros::dec;

    #[test]
    #[timeout(100)]
    fn test_single_line() {
        let input = vec![LineItem {
            amount: s!("10.00"),
            priority: 0,
            id: 1,
            ..Default::default()
        }];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(10.00));
        assert_eq!(discount, dec!(0.00));
        assert_eq!(map[&input[0]], dec!(10.00));
    }

    #[test]
    #[timeout(100)]
    fn test_get_totals_percentage_line() {
        let input = vec![
            LineItem {
                amount: s!("10.00"),
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                percentage: s!("10.00"),
                priority: 1,
                id: 2,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(11.00));
        assert_eq!(discount, dec!(0.00));
        assert_eq!(map[&input[0]], dec!(10.00));
        assert_eq!(map[&input[1]], dec!(1.00));
    }

    #[test]
    #[timeout(100)]
    fn test_get_totals_percentage_with_static() {
        let input = vec![
            LineItem {
                amount: s!("10.00"),
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                percentage: s!("10"),
                amount: s!("0.25"),
                priority: 1,
                id: 2,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(11.25));
        assert_eq!(discount, dec!(0.00));
        assert_eq!(map[&input[0]], dec!(10.00));
        assert_eq!(map[&input[1]], dec!(1.25));
        assert_eq!(
            total,
            map.values().fold(dec!(0), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_get_totals_concurrent_priorities() {
        let input = vec![
            LineItem {
                amount: s!("10.00"),
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: s!("2.00"),
                priority: 10,
                id: 1,
                ..Default::default()
            },
            LineItem {
                percentage: s!("10"),
                amount: s!(".05"),
                priority: 100,
                id: 2,
                ..Default::default()
            },
            LineItem {
                percentage: s!("5"),
                amount: s!("0.08"),
                priority: 100,
                id: 3,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(13.93));
        assert_eq!(discount, dec!(0));
        assert_eq!(map[&input[0]], dec!(10.00));
        assert_eq!(map[&input[1]], dec!(2.00));
        assert_eq!(map[&input[2]], dec!(1.25));
        assert_eq!(map[&input[3]], dec!(0.68));
        assert_eq!(
            total,
            map.values().fold(dec!(0), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_negative_total() {
        let input = vec![
            LineItem {
                id: 1,
                amount: s!("0.00"),
                priority: 0,
                ..Default::default()
            },
            LineItem {
                id: 2,
                priority: 100,
                amount: s!("-8.00"),
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(-8));
        assert_eq!(discount, dec!(-8));
        assert_eq!(map[&input[0]], dec!(0));
        assert_eq!(map[&input[1]], dec!(-8.00));
        assert_eq!(
            total,
            map.values().fold(dec!(0), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_negative_percentage() {
        let input = vec![
            LineItem {
                id: 1,
                amount: s!("10.00"),
                priority: 0,
                ..Default::default()
            },
            LineItem {
                id: 2,
                priority: 100,
                percentage: s!("-10.00"),
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(9));
        assert_eq!(discount, dec!(-1));
        assert_eq!(map[&input[0]], dec!(10));
        assert_eq!(map[&input[1]], dec!(-1.00));
        assert_eq!(
            total,
            map.values().fold(dec!(0), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_frozen_values() {
        let input = vec![
            LineItem {
                id: 1,
                amount: s!("10.00"),
                priority: 0,
                frozen_value: Some(s!("4.00")),
                ..Default::default()
            },
            LineItem {
                id: 2,
                priority: 100,
                percentage: s!("-10.00"),
                frozen_value: Some(s!("3.50")),
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(7.50));
        assert_eq!(discount, dec!(0));
        assert_eq!(map[&input[0]], dec!(4));
        assert_eq!(map[&input[1]], dec!(3.50));
    }

    #[test]
    fn test_ignores_on_mixed_frozenness() {
        let input = vec![
            LineItem {
                id: 1,
                amount: s!("10.00"),
                priority: 0,
                frozen_value: Some(s!("4.00")),
                ..Default::default()
            },
            LineItem {
                id: 2,
                priority: 100,
                percentage: s!("-10.00"),
                frozen_value: None,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(9));
        assert_eq!(discount, dec!(-1));
        assert_eq!(map[&input[0]], dec!(10));
        assert_eq!(map[&input[1]], dec!(-1.00));
        assert_eq!(
            total,
            map.values().fold(dec!(0), |current, item| current + *item)
        );
    }

    #[test]
    fn test_errors_on_mixed_frozenness_inner() {
        let input = vec![
            LineItem {
                id: 1,
                amount: s!("10.00"),
                priority: 0,
                frozen_value: Some(s!("4.00")),
                ..Default::default()
            },
            LineItem {
                id: 2,
                priority: 100,
                percentage: s!("-10.00"),
                frozen_value: None,
                ..Default::default()
            },
        ];
        let error = frozen_lines(input);
        assert_eq!(error, Err(TabulationError::from("Unfrozen line found!")))
    }

    #[test]
    #[timeout(100)]
    fn test_discount_on_zero() {
        let input = vec![
            LineItem {
                id: 1,
                amount: s!("0.00"),
                priority: 0,
                ..Default::default()
            },
            LineItem {
                id: 2,
                priority: 100,
                percentage: s!("-10.00"),
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(0));
        assert_eq!(discount, dec!(0));
        assert_eq!(map[&input[0]], dec!(0));
        assert_eq!(map[&input[1]], dec!(0));
        assert_eq!(
            total,
            map.values().fold(dec!(0), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_zero_line() {
        let input = vec![
            LineItem {
                amount: s!("19.56"),
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: s!("2.75"),
                percentage: s!("5.75"),
                priority: 300,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: s!("520.36"),
                priority: 100,
                id: 3,
                ..Default::default()
            },
            LineItem {
                amount: s!("0.00"),
                priority: 100,
                id: 4,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(573.71));
        assert_eq!(discount, dec!(0.00));
        assert_eq!(map[&input[0]], dec!(19.56));
        assert_eq!(map[&input[1]], dec!(33.79));
        assert_eq!(map[&input[2]], dec!(520.36));
        assert_eq!(map[&input[3]], dec!(0.00));
        assert_eq!(
            total,
            map.values().fold(dec!(0), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_complex_discount() {
        let input = vec![
            LineItem {
                amount: s!("0.01"),
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: s!("0.01"),
                priority: 100,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: s!("0.01"),
                priority: 100,
                id: 3,
                ..Default::default()
            },
            LineItem {
                amount: s!("-5.00"),
                priority: 100,
                id: 4,
                ..Default::default()
            },
            LineItem {
                amount: s!("10.00"),
                priority: 100,
                id: 5,
                ..Default::default()
            },
            LineItem {
                amount: s!("0.75"),
                percentage: s!("8"),
                priority: 300,
                id: 6,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(6.18));
        assert_eq!(discount, dec!(-5.00));
        assert_eq!(map[&input[0]], dec!(0.01));
        assert_eq!(map[&input[1]], dec!(0.01));
        assert_eq!(map[&input[2]], dec!(0.01));
        assert_eq!(map[&input[3]], dec!(-5.00));
        assert_eq!(map[&input[4]], dec!(10.00));
        assert_eq!(map[&input[5]], dec!(1.15));
        assert_eq!(
            total,
            map.values().fold(dec!(0), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_reckon_lines() {
        let input = vec![
            LineItem {
                amount: s!("1"),
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: s!("5"),
                priority: 1,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: s!("4"),
                priority: 2,
                id: 3,
                ..Default::default()
            },
        ];
        assert_eq!(reckon_lines(input.clone(), 2).unwrap(), dec!(10.00));
    }

    #[test]
    #[timeout(100)]
    fn test_percentage() {
        let input = vec![
            LineItem {
                amount: s!("5"),
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: s!("1"),
                priority: 1,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: s!("4"),
                priority: 1,
                id: 3,
                ..Default::default()
            },
            LineItem {
                percentage: s!("5"),
                back_into_percentage: true,
                priority: 100,
                id: 4,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(10.52));
        assert_eq!(discount, dec!(0.00));
        assert_eq!(map[&input[0]], dec!(5.00));
        assert_eq!(map[&input[1]], dec!(1.00));
        assert_eq!(map[&input[2]], dec!(4.00));
        assert_eq!(map[&input[3]], dec!(0.52));
    }
}

#[cfg(test)]
mod line_item_generation_tests {
    use crate::data::{
        Account, Category, DeliverableLinesContext, InvoiceLinesContext, LineItem, LineType,
        Pricing, Product, ServicePlan, TabulationError, TipLinesContext,
    };
    use crate::funcs::{deliverable_lines, invoice_lines, tip_fee_lines};
    use crate::s;
    use ntest::timeout;
    use pretty_assertions::assert_eq;

    fn gen_pricing() -> Pricing {
        Pricing {
            plans: vec![
                ServicePlan {
                    id: 7,
                    name: s!("Free"),
                    per_deliverable_price: s!("0.00"),
                    max_simultaneous_orders: 1,
                    waitlisting: false,
                    shield_static_price: s!("3.50"),
                    shield_percentage_price: s!("3.50"),
                    paypal_invoicing: false,
                    connection_fee_waived: false,
                },
                ServicePlan {
                    id: 8,
                    name: s!("Basic"),
                    per_deliverable_price: s!("1.35"),
                    max_simultaneous_orders: 0,
                    waitlisting: false,
                    shield_static_price: s!("3.50"),
                    shield_percentage_price: s!("5"),
                    paypal_invoicing: false,
                    connection_fee_waived: false,
                },
                ServicePlan {
                    id: 9,
                    name: s!("Landscape"),
                    per_deliverable_price: s!("0.75"),
                    max_simultaneous_orders: 0,
                    waitlisting: true,
                    shield_static_price: s!("0.75"),
                    shield_percentage_price: s!("4"),
                    paypal_invoicing: true,
                    connection_fee_waived: true,
                },
            ],
            minimum_price: s!("1.00"),
            table_percentage: s!("10"),
            table_static: s!("5.00"),
            table_tax: s!("8.25"),
            processing_percentage: s!("1"),
            processing_static: s!("0.15"),
            stripe_blended_rate_static: s!("0.30"),
            stripe_active_account_monthly_fee: s!("2.00"),
            stripe_blended_rate_percentage: s!("3.30"),
            stripe_payout_cross_border_percentage: s!("1"),
            stripe_payout_static: s!(".25"),
            stripe_payout_percentage: s!("1.25"),
            international_conversion_percentage: s!("1"),
            preferred_plan: s!("Landscape"),
        }
    }

    #[test]
    #[timeout(100)]
    fn test_basic_line_items() {
        let lines_result = deliverable_lines(DeliverableLinesContext {
            escrow_enabled: true,
            pricing: Some(gen_pricing()),
            base_price: s!("25.00"),
            international: false,
            plan_name: Some(s!("Basic")),
            table_product: false,
            extra_lines: vec![],
            allow_soft_failure: false,
            user_id: -1,
            quantization: 2,
        });
        let expected = vec![
            LineItem {
                id: -1,
                priority: 0,
                kind: LineType::BasePrice,
                amount: s!("25.00"),
                category: Category::EscrowHold,
                frozen_value: None,
                percentage: s!("0"),
                description: s!(""),
                back_into_percentage: false,
                destination_user_id: Some(-1),
                destination_account: Account::Escrow,
            },
            LineItem {
                id: -5,
                priority: 330,
                kind: LineType::Shield,
                back_into_percentage: false,
                amount: s!("3.50"),
                category: Category::ShieldFee,
                frozen_value: None,
                percentage: s!("5"),
                description: s!(""),
                destination_user_id: None,
                destination_account: Account::Fund,
            },
            LineItem {
                id: -7,
                priority: 350,
                kind: LineType::CardFee,
                amount: s!("0.30"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("3.30"),
                category: Category::ThirdPartyFee,
                back_into_percentage: true,
                destination_account: Account::Fund,
                destination_user_id: None,
            },
            LineItem {
                id: -9,
                priority: 325,
                kind: LineType::PayoutFee,
                amount: s!(".25"),
                percentage: s!("1.25"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: false,
                frozen_value: None,
                description: s!(""),
            },
            LineItem {
                id: -10,
                priority: 325,
                kind: LineType::ConnectFee,
                amount: s!("2.00"),
                percentage: s!("0"),
                description: s!(""),
                frozen_value: None,
                back_into_percentage: false,
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
            },
        ];
        assert_eq!(lines_result, Ok(expected));
    }

    #[test]
    #[timeout(100)]
    fn test_basic_zero_line_items() {
        let lines_result = deliverable_lines(DeliverableLinesContext {
            escrow_enabled: true,
            pricing: Some(gen_pricing()),
            base_price: s!("0.00"),
            international: false,
            plan_name: Some(s!("Basic")),
            table_product: false,
            extra_lines: vec![],
            allow_soft_failure: false,
            user_id: -1,
            quantization: 2,
        });
        let expected = vec![
            LineItem {
                id: -1,
                priority: 0,
                kind: LineType::BasePrice,
                amount: s!("0.00"),
                category: Category::EscrowHold,
                frozen_value: None,
                percentage: s!("0"),
                description: s!(""),
                back_into_percentage: false,
                destination_user_id: Some(-1),
                destination_account: Account::Escrow,
            },
            LineItem {
                id: -6,
                priority: 300,
                kind: LineType::DeliverableTracking,
                amount: s!("1.35"),
                percentage: s!("0"),
                back_into_percentage: false,
                description: s!(""),
                category: Category::SubscriptionDues,
                frozen_value: None,
                destination_account: Account::Fund,
                destination_user_id: None,
            },
        ];
        assert_eq!(lines_result, Ok(expected));
    }

    #[test]
    #[timeout(100)]
    fn test_skips_basic_if_in_extra() {
        let lines_result = deliverable_lines(DeliverableLinesContext {
            escrow_enabled: true,
            pricing: Some(gen_pricing()),
            base_price: s!("25.00"),
            international: false,
            plan_name: Some(s!("Basic")),
            table_product: false,
            extra_lines: vec![LineItem {
                id: 5,
                priority: 0,
                kind: LineType::BasePrice,
                amount: s!("8.50"),
                category: Category::EscrowHold,
                frozen_value: None,
                percentage: s!("0"),
                description: s!(""),
                back_into_percentage: false,
                destination_user_id: Some(-1),
                destination_account: Account::Escrow,
            }],
            allow_soft_failure: false,
            user_id: -1,
            quantization: 2,
        });
        let expected = vec![
            LineItem {
                id: -5,
                priority: 330,
                kind: LineType::Shield,
                back_into_percentage: false,
                amount: s!("3.50"),
                category: Category::ShieldFee,
                frozen_value: None,
                percentage: s!("5"),
                description: s!(""),
                destination_user_id: None,
                destination_account: Account::Fund,
            },
            LineItem {
                id: -7,
                priority: 350,
                kind: LineType::CardFee,
                amount: s!("0.30"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("3.30"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: true,
            },
            LineItem {
                id: -9,
                priority: 325,
                kind: LineType::PayoutFee,
                amount: s!(".25"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("1.25"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: false,
            },
            LineItem {
                id: -10,
                priority: 325,
                kind: LineType::ConnectFee,
                amount: s!("2.00"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("0"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: false,
            },
            LineItem {
                id: 5,
                priority: 0,
                kind: LineType::BasePrice,
                amount: s!("8.50"),
                category: Category::EscrowHold,
                frozen_value: None,
                percentage: s!("0"),
                description: s!(""),
                back_into_percentage: false,
                destination_user_id: Some(-1),
                destination_account: Account::Escrow,
            },
        ];
        assert_eq!(lines_result, Ok(expected));
    }

    #[test]
    #[timeout(100)]
    fn test_generates_for_null_product() {
        let lines_result = invoice_lines(InvoiceLinesContext {
            escrow_enabled: true,
            pricing: Some(gen_pricing()),
            value: s!("25.00"),
            international: false,
            plan_name: Some(s!("Basic")),
            product: None,
            allow_soft_failure: false,
            user_id: -2,
            quantization: 2,
        });
        let expected = vec![
            LineItem {
                id: -1,
                priority: 0,
                kind: LineType::BasePrice,
                amount: s!("25.00"),
                category: Category::EscrowHold,
                frozen_value: None,
                percentage: s!("0"),
                back_into_percentage: false,
                description: s!(""),
                destination_user_id: Some(-2),
                destination_account: Account::Escrow,
            },
            LineItem {
                id: -5,
                priority: 330,
                kind: LineType::Shield,
                back_into_percentage: false,
                amount: s!("3.50"),
                category: Category::ShieldFee,
                frozen_value: None,
                percentage: s!("5"),
                description: s!(""),
                destination_user_id: None,
                destination_account: Account::Fund,
            },
            LineItem {
                id: -7,
                priority: 350,
                kind: LineType::CardFee,
                amount: s!("0.30"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("3.30"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: true,
            },
            LineItem {
                id: -9,
                priority: 325,
                kind: LineType::PayoutFee,
                amount: s!(".25"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("1.25"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: false,
            },
            LineItem {
                id: -10,
                priority: 325,
                kind: LineType::ConnectFee,
                amount: s!("2.00"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("0"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: false,
            },
        ];
        assert_eq!(lines_result, Ok(expected));
    }

    #[test]
    #[timeout(100)]
    fn test_generates_for_product() {
        let lines_result = invoice_lines(InvoiceLinesContext {
            escrow_enabled: true,
            pricing: Some(gen_pricing()),
            value: s!("25.00"),
            international: false,
            plan_name: Some(s!("Basic")),
            product: Some(Product {
                ..Default::default()
            }),
            allow_soft_failure: false,
            quantization: 2,
            user_id: -1,
        });
        let expected = vec![
            LineItem {
                id: -1,
                priority: 0,
                kind: LineType::BasePrice,
                amount: s!("10.00"),
                frozen_value: None,
                percentage: s!("0"),
                description: s!(""),
                category: Category::EscrowHold,
                back_into_percentage: false,
                destination_user_id: Some(-1),
                destination_account: Account::Escrow,
            },
            LineItem {
                id: -5,
                priority: 330,
                kind: LineType::Shield,
                back_into_percentage: false,
                category: Category::ShieldFee,
                amount: s!("3.50"),
                frozen_value: None,
                percentage: s!("5"),
                description: s!(""),
                destination_user_id: None,
                destination_account: Account::Fund,
            },
            LineItem {
                id: -7,
                priority: 350,
                kind: LineType::CardFee,
                amount: s!("0.30"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("3.30"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: true,
            },
            LineItem {
                id: -9,
                priority: 325,
                kind: LineType::PayoutFee,
                amount: s!(".25"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("1.25"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: false,
            },
            LineItem {
                id: -10,
                priority: 325,
                kind: LineType::ConnectFee,
                amount: s!("2.00"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("0"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: false,
            },
            LineItem {
                id: -2,
                priority: 100,
                kind: LineType::AddOn,
                amount: s!("15.00"),
                frozen_value: None,
                category: Category::EscrowHold,
                percentage: s!("0"),
                description: s!(""),
                back_into_percentage: false,
                destination_account: Account::Escrow,
                destination_user_id: Some(-1),
            },
        ];
        assert_eq!(lines_result, Ok(expected));
    }

    #[test]
    #[timeout(100)]
    fn test_generates_for_international_product() {
        let line_items = invoice_lines(InvoiceLinesContext {
            escrow_enabled: true,
            pricing: Some(gen_pricing()),
            value: s!("25.00"),
            product: Some(Product {
                ..Default::default()
            }),
            international: true,
            plan_name: Some(s!("Basic")),
            allow_soft_failure: false,
            quantization: 2,
            user_id: -1,
        });
        let expected = vec![
            LineItem {
                id: -1,
                priority: 0,
                kind: LineType::BasePrice,
                amount: s!("10.00"),
                frozen_value: None,
                percentage: s!("0"),
                description: s!(""),
                category: Category::EscrowHold,
                back_into_percentage: false,
                destination_user_id: Some(-1),
                destination_account: Account::Escrow,
            },
            LineItem {
                id: -5,
                priority: 330,
                kind: LineType::Shield,
                category: Category::ShieldFee,
                back_into_percentage: false,
                amount: s!("3.50"),
                frozen_value: None,
                percentage: s!("6"),
                description: s!(""),
                destination_account: Account::Fund,
                destination_user_id: None,
            },
            LineItem {
                id: -7,
                priority: 350,
                kind: LineType::CardFee,
                amount: s!("0.30"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("3.30"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: true,
            },
            LineItem {
                id: -9,
                priority: 325,
                kind: LineType::PayoutFee,
                amount: s!(".25"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("1.25"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: false,
            },
            LineItem {
                id: -8,
                priority: 325,
                kind: LineType::CrossBorderTransferFee,
                amount: s!("0"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("1"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: false,
            },
            LineItem {
                id: -10,
                priority: 325,
                kind: LineType::ConnectFee,
                amount: s!("2.00"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("0"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: false,
            },
            LineItem {
                id: -2,
                priority: 100,
                kind: LineType::AddOn,
                amount: s!("15.00"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("0"),
                category: Category::EscrowHold,
                destination_user_id: Some(-1),
                destination_account: Account::Escrow,
                back_into_percentage: false,
            },
        ];
        assert_eq!(line_items, Ok(expected));
    }

    #[test]
    #[timeout(100)]
    fn test_generates_for_table_product() {
        let line_items = invoice_lines(InvoiceLinesContext {
            escrow_enabled: true,
            pricing: Some(gen_pricing()),
            value: s!("25.00"),
            product: Some(Product {
                table_product: true,
                ..Default::default()
            }),
            international: false,
            plan_name: Some(s!("Basic")),
            user_id: -3,
            allow_soft_failure: false,
            quantization: 2,
        });
        let expected = vec![
            LineItem {
                id: -1,
                priority: 0,
                kind: LineType::BasePrice,
                category: Category::EscrowHold,
                amount: s!("10.00"),
                frozen_value: None,
                percentage: s!("0"),
                description: s!(""),
                back_into_percentage: false,
                destination_user_id: Some(-3),
                destination_account: Account::Escrow,
            },
            LineItem {
                id: -3,
                priority: 400,
                kind: LineType::TableService,
                back_into_percentage: false,
                amount: s!("5.00"),
                category: Category::TableHandling,
                frozen_value: None,
                percentage: s!("10"),
                description: s!(""),
                destination_user_id: None,
                destination_account: Account::Reserve,
            },
            LineItem {
                id: -4,
                priority: 700,
                kind: LineType::Tax,
                back_into_percentage: false,
                category: Category::Taxes,
                percentage: s!("8.25"),
                description: s!(""),
                amount: s!("0"),
                frozen_value: None,
                destination_user_id: None,
                destination_account: Account::MoneyHoleStage,
            },
            LineItem {
                id: -7,
                priority: 350,
                kind: LineType::CardFee,
                amount: s!("0.30"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("3.30"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: true,
            },
            LineItem {
                id: -9,
                priority: 325,
                kind: LineType::PayoutFee,
                amount: s!(".25"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("1.25"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: false,
            },
            LineItem {
                id: -10,
                priority: 325,
                kind: LineType::ConnectFee,
                amount: s!("2.00"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("0"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: false,
            },
            LineItem {
                id: -2,
                priority: 100,
                kind: LineType::AddOn,
                amount: s!("15.00"),
                frozen_value: None,
                percentage: s!("0"),
                description: s!(""),
                category: Category::EscrowHold,
                back_into_percentage: false,
                destination_user_id: Some(-3),
                destination_account: Account::Escrow,
            },
        ];
        assert_eq!(line_items, Ok(expected));
    }

    #[test]
    #[timeout(100)]
    fn test_generates_lines_null_product_no_escrow() {
        let line_items = invoice_lines(InvoiceLinesContext {
            escrow_enabled: false,
            pricing: Some(gen_pricing()),
            value: s!("25.00"),
            product: None,
            international: false,
            plan_name: Some(s!("Basic")),
            user_id: -1,
            allow_soft_failure: false,
            quantization: 2,
        });
        let expected = vec![
            LineItem {
                id: -1,
                priority: 0,
                kind: LineType::BasePrice,
                amount: s!("25.00"),
                frozen_value: None,
                percentage: s!("0"),
                description: s!(""),
                category: Category::EscrowHold,
                back_into_percentage: false,
                destination_user_id: Some(-1),
                destination_account: Account::Escrow,
            },
            LineItem {
                id: -6,
                priority: 300,
                kind: LineType::DeliverableTracking,
                amount: s!("1.35"),
                percentage: s!("0"),
                back_into_percentage: false,
                description: s!(""),
                category: Category::SubscriptionDues,
                frozen_value: None,
                destination_account: Account::Fund,
                destination_user_id: None,
            },
        ];
        assert_eq!(line_items, Ok(expected))
    }

    #[test]
    #[timeout(100)]
    fn test_generates_lines_product_no_escrow() {
        let line_items = invoice_lines(InvoiceLinesContext {
            escrow_enabled: false,
            pricing: Some(gen_pricing()),
            value: s!("25.00"),
            product: Some(Product {
                ..Default::default()
            }),
            international: false,
            plan_name: Some(s!("Basic")),
            user_id: 4,
            allow_soft_failure: false,
            quantization: 2,
        });
        let expected = vec![
            LineItem {
                id: -1,
                priority: 0,
                kind: LineType::BasePrice,
                amount: s!("10.00"),
                category: Category::EscrowHold,
                frozen_value: None,
                percentage: s!("0"),
                description: s!(""),
                back_into_percentage: false,
                destination_user_id: Some(4),
                destination_account: Account::Escrow,
            },
            LineItem {
                id: -6,
                priority: 300,
                kind: LineType::DeliverableTracking,
                category: Category::SubscriptionDues,
                amount: s!("1.35"),
                percentage: s!("0"),
                back_into_percentage: false,
                frozen_value: None,
                description: s!(""),
                destination_account: Account::Fund,
                destination_user_id: None,
            },
            LineItem {
                id: -2,
                priority: 100,
                kind: LineType::AddOn,
                amount: s!("15.00"),
                percentage: s!("0"),
                description: s!(""),
                back_into_percentage: false,
                frozen_value: None,
                category: Category::EscrowHold,
                destination_account: Account::Escrow,
                destination_user_id: Some(4),
            },
        ];
        assert_eq!(line_items, Ok(expected));
    }

    #[test]
    #[timeout(100)]
    fn test_product_no_escrow_and_nonsense_value() {
        let parameters = InvoiceLinesContext {
            escrow_enabled: false,
            pricing: Some(gen_pricing()),
            value: s!("boop"),
            product: Some(Product {
                ..Default::default()
            }),
            international: false,
            plan_name: Some(s!("Basic")),
            user_id: -1,
            allow_soft_failure: false,
            quantization: 2,
        };
        let mut working_parameters = parameters.clone();
        working_parameters.allow_soft_failure = true;
        assert_eq!(invoice_lines(working_parameters), Ok(vec![]));
        assert_eq!(
            invoice_lines(parameters),
            Err(TabulationError::from("Invalid decimal: unknown character"))
        );
    }

    #[test]
    #[timeout(100)]
    fn test_no_product_no_escrow_and_nonsense_value() {
        let parameters = InvoiceLinesContext {
            escrow_enabled: false,
            pricing: Some(gen_pricing()),
            value: s!("boop"),
            product: None,
            international: false,
            user_id: -1,
            plan_name: Some(s!("Basic")),
            allow_soft_failure: false,
            quantization: 2,
        };
        let mut working_parameters = parameters.clone();
        working_parameters.allow_soft_failure = true;
        assert_eq!(invoice_lines(working_parameters), Ok(vec![]));
        assert_eq!(
            invoice_lines(parameters),
            Err(TabulationError::from("Invalid decimal: unknown character"))
        );
    }

    #[test]
    #[timeout(100)]
    fn test_pricing_unavailable() {
        let parameters = InvoiceLinesContext {
            escrow_enabled: false,
            pricing: None,
            value: s!("10.00"),
            product: None,
            international: false,
            plan_name: Some(s!("Basic")),
            user_id: -1,
            allow_soft_failure: false,
            quantization: 2,
        };
        let mut working_parameters = parameters.clone();
        working_parameters.allow_soft_failure = true;
        assert_eq!(invoice_lines(working_parameters), Ok(vec![]));
        assert_eq!(
            invoice_lines(parameters),
            Err(TabulationError::from("Pricing specification not provided."))
        );
    }

    #[test]
    #[timeout(100)]
    fn test_plan_unknown() {
        let parameters = InvoiceLinesContext {
            escrow_enabled: false,
            pricing: Some(gen_pricing()),
            value: s!("10.00"),
            product: None,
            international: false,
            plan_name: Some(s!("Backup")),
            user_id: -1,
            allow_soft_failure: false,
            quantization: 2,
        };
        let mut working_parameters = parameters.clone();
        working_parameters.allow_soft_failure = true;
        assert_eq!(invoice_lines(working_parameters), Ok(vec![]));
        assert_eq!(
            invoice_lines(parameters),
            Err(TabulationError::from("Could not find Backup in plan list."))
        );
    }

    #[test]
    #[timeout(100)]
    fn test_tip_lines_domestic() {
        let parameters = TipLinesContext {
            international: false,
            pricing: Some(gen_pricing()),
            quantization: 2,
        };
        let expected = vec![
            LineItem {
                id: -1,
                priority: 300,
                kind: LineType::Processing,
                amount: s!("0.15"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("1"),
                category: Category::ProcessingFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: false,
            },
            LineItem {
                id: -7,
                priority: 350,
                kind: LineType::CardFee,
                amount: s!("0.30"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("3.30"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: false,
            },
            LineItem {
                id: -9,
                priority: 325,
                kind: LineType::PayoutFee,
                amount: s!(".25"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("1.25"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: false,
            },
        ];
        assert_eq!(tip_fee_lines(parameters), Ok(expected));
    }

    #[test]
    #[timeout(100)]
    fn test_tip_lines_international() {
        let parameters = TipLinesContext {
            international: true,
            pricing: Some(gen_pricing()),
            quantization: 2,
        };
        let expected = vec![
            LineItem {
                id: -1,
                priority: 300,
                kind: LineType::Processing,
                amount: s!("0.15"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("2"),
                category: Category::ProcessingFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: false,
            },
            LineItem {
                id: -7,
                priority: 350,
                kind: LineType::CardFee,
                amount: s!("0.30"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("3.30"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: false,
            },
            LineItem {
                id: -9,
                priority: 325,
                kind: LineType::PayoutFee,
                amount: s!(".25"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("1.25"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: false,
            },
            LineItem {
                id: -8,
                priority: 325,
                kind: LineType::CrossBorderTransferFee,
                amount: s!("0"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("1"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                back_into_percentage: false,
            },
        ];
        assert_eq!(tip_fee_lines(parameters), Ok(expected));
    }
}

#[cfg(test)]
mod helpers_tests {
    use crate::funcs::divide_amount;
    use rust_decimal_macros::dec;

    #[test]
    fn test_divide_amount() {
        assert_eq!(
            divide_amount(dec!(10), 3, 2),
            Ok(vec![dec!(3.34), dec!(3.33), dec!(3.33)]),
        );
        assert_eq!(
            divide_amount(dec!(10.01), 3, 2),
            Ok(vec![dec!(3.34), dec!(3.34), dec!(3.33)]),
        );
        assert_eq!(
            divide_amount(dec!(10.02), 3, 2),
            Ok(vec![dec!(3.34), dec!(3.34), dec!(3.34)]),
        );
        assert_eq!(
            divide_amount(dec!(10.03), 3, 2),
            Ok(vec![dec!(3.35), dec!(3.34), dec!(3.34)]),
        );
    }

    #[test]
    fn test_divide_non_subunit() {
        assert_eq!(
            divide_amount(dec!(10000), 3, 0),
            Ok(vec![dec!(3334), dec!(3333), dec!(3333)]),
        );
        assert_eq!(
            divide_amount(dec!(10001), 3, 0),
            Ok(vec![dec!(3334), dec!(3334), dec!(3333)]),
        );
        assert_eq!(
            divide_amount(dec!(10003), 3, 0),
            Ok(vec![dec!(3335), dec!(3334), dec!(3334)]),
        );
    }
}
