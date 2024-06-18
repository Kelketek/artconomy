#[cfg(test)]
mod interface_tests {
    use crate::data::{LineItem, Money, USD};
    use crate::funcs::{get_totals, reckon_lines};
    use crate::money;
    use ntest::timeout;
    use rust_decimal_macros::dec;

    #[test]
    #[timeout(100)]
    fn test_single_line() {
        let input = vec![LineItem {
            amount: "10.00",
            priority: 0,
            id: 1,
            ..Default::default()
        }];
        let (total, discount, map) = get_totals(input.clone(), USD);
        assert_eq!(total, money!(10.00, USD));
        assert_eq!(discount, money!(0.00, USD));
        assert_eq!(map[&input[0]], money!(10.00, USD));
    }

    #[test]
    #[timeout(100)]
    fn test_get_totals_percentage_line() {
        let input = vec![
            LineItem {
                amount: "10.00",
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                percentage: "10.00",
                priority: 1,
                id: 2,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), USD);
        assert_eq!(total, money!(11.00, USD));
        assert_eq!(discount, money!(0.00, USD));
        assert_eq!(map[&input[0]], money!(10.00, USD));
        assert_eq!(map[&input[1]], money!(1.00, USD));
    }

    #[test]
    #[timeout(100)]
    fn test_get_totals_percentage_cascade() {
        let input = vec![
            LineItem {
                amount: "10.00",
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                percentage: "10",
                priority: 1,
                cascade_percentage: true,
                id: 2,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), USD);
        assert_eq!(total, money!(10.00, USD));
        assert_eq!(discount, money!(0.00, USD));
        assert_eq!(map[&input[0]], money!(9.00, USD));
        assert_eq!(map[&input[1]], money!(1.00, USD));
    }

    #[test]
    #[timeout(100)]
    fn test_get_totals_percentage_backed_in_cascade() {
        let input = vec![
            LineItem {
                amount: "10.00",
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                percentage: "10.00",
                priority: 1,
                cascade_percentage: true,
                back_into_percentage: true,
                id: 2,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), USD);
        assert_eq!(total, money!(10.00, USD));
        assert_eq!(discount, money!(0.00, USD));
        assert_eq!(map[&input[0]], money!(9.09, USD));
        assert_eq!(map[&input[1]], money!(0.91, USD));
        assert_eq!(
            total,
            map.values()
                .fold(money!(0, USD), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_get_totals_percentage_with_static() {
        let input = vec![
            LineItem {
                amount: "10.00",
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                percentage: "10",
                amount: "0.25",
                priority: 1,
                id: 2,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), USD);
        assert_eq!(total, money!(11.25, USD));
        assert_eq!(discount, money!(0.00, USD));
        assert_eq!(map[&input[0]], money!(10.00, USD));
        assert_eq!(map[&input[1]], money!(1.25, USD));
        assert_eq!(
            total,
            map.values()
                .fold(money!(0, USD), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_get_totals_percentage_with_static_cascade() {
        let input = vec![
            LineItem {
                amount: "10.00",
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                percentage: "10",
                amount: "0.25",
                cascade_percentage: true,
                cascade_amount: true,
                priority: 1,
                id: 2,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), USD);
        assert_eq!(total, money!(10.00, USD));
        assert_eq!(discount, money!(0.00, USD));
        assert_eq!(map[&input[0]], money!(8.75, USD));
        assert_eq!(map[&input[1]], money!(1.25, USD));
        assert_eq!(
            total,
            map.values()
                .fold(money!(0, USD), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_get_totals_percentage_no_cascade_amount() {
        let input = vec![
            LineItem {
                amount: "10.00",
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                percentage: "10",
                amount: "0.25",
                priority: 1,
                id: 2,
                cascade_amount: false,
                cascade_percentage: true,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), USD);
        assert_eq!(total, money!(10.25, USD));
        assert_eq!(discount, money!(0.00, USD));
        assert_eq!(map[&input[0]], money!(9.00, USD));
        assert_eq!(map[&input[1]], money!(1.25, USD));
        assert_eq!(
            total,
            map.values()
                .fold(money!(0, USD), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_get_totals_concurrent_priorities() {
        let input = vec![
            LineItem {
                amount: "10.00",
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                percentage: "10",
                priority: 1,
                id: 2,
                ..Default::default()
            },
            LineItem {
                percentage: "5",
                priority: 1,
                id: 3,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), USD);
        assert_eq!(total, money!(11.50, USD));
        assert_eq!(discount, money!(0, USD));
        assert_eq!(map[&input[0]], money!(10.00, USD));
        assert_eq!(map[&input[1]], money!(1, USD));
        assert_eq!(map[&input[2]], money!(0.50, USD));
        assert_eq!(
            total,
            map.values()
                .fold(money!(0, USD), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_get_totals_concurrent_priorities_cascade() {
        let input = vec![
            LineItem {
                amount: "10.00",
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                percentage: "10",
                priority: 1,
                cascade_percentage: true,
                id: 2,
                ..Default::default()
            },
            LineItem {
                percentage: "5",
                priority: 1,
                cascade_percentage: true,
                id: 3,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), USD);
        assert_eq!(total, money!(10, USD));
        assert_eq!(discount, money!(0, USD));
        assert_eq!(map[&input[0]], money!(8.50, USD));
        assert_eq!(map[&input[1]], money!(1, USD));
        assert_eq!(map[&input[2]], money!(0.50, USD));
        assert_eq!(
            total,
            map.values()
                .fold(money!(0, USD), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_get_totals_multi_priority_cascade_on_concurrent_priority() {
        let input = vec![
            LineItem {
                amount: "2",
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: "8",
                priority: 0,
                id: 2,
                ..Default::default()
            },
            LineItem {
                percentage: "20",
                priority: 1,
                cascade_percentage: true,
                id: 3,
                ..Default::default()
            },
            LineItem {
                percentage: "10",
                priority: 2,
                cascade_percentage: true,
                id: 4,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), USD);
        assert_eq!(total, money!(10, USD));
        assert_eq!(discount, money!(0, USD));
        assert_eq!(map[&input[0]], money!(1.44, USD));
        assert_eq!(map[&input[1]], money!(5.76, USD));
        assert_eq!(map[&input[2]], money!(1.80, USD));
        assert_eq!(map[&input[3]], money!(1.00, USD));
        assert_eq!(
            total,
            map.values()
                .fold(money!(0, USD), |current, item| current + *item)
        );
    }

    /*
    These next few tests check edge cases that were found in real-world invoices. These challenged
    my assumptions of how fixed point calculations were to be done, and helped my refine the
    calculation functions. Their values will look different from other tests accordingly.
     */
    #[test]
    #[timeout(100)]
    fn test_fixed_point_decisions() {
        let input = vec![
            LineItem {
                amount: "100",
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: "5.00",
                priority: 100,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: "5.00",
                percentage: "10",
                priority: 300,
                cascade_percentage: true,
                id: 3,
                ..Default::default()
            },
            LineItem {
                percentage: "8.25",
                cascade_percentage: true,
                priority: 600,
                id: 4,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), USD);
        assert_eq!(total, money!(110.00, USD));
        assert_eq!(discount, money!(0.00, USD));
        assert_eq!(map[&input[0]], money!(82.57, USD));
        assert_eq!(map[&input[1]], money!(4.12, USD));
        assert_eq!(map[&input[2]], money!(14.23, USD));
        assert_eq!(map[&input[3]], money!(9.08, USD));
        assert_eq!(
            total,
            map.values()
                .fold(money!(0, USD), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_fixed_point_decisions_2() {
        let input = vec![
            LineItem {
                amount: "20",
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: "10.00",
                priority: 100,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: "5.00",
                percentage: "10",
                cascade_percentage: true,
                priority: 300,
                id: 3,
                ..Default::default()
            },
            LineItem {
                percentage: "8.25",
                cascade_percentage: true,
                priority: 600,
                id: 4,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), USD);
        assert_eq!(total, money!(35.00, USD));
        assert_eq!(discount, money!(0.00, USD));
        assert_eq!(map[&input[0]], money!(16.51, USD));
        assert_eq!(map[&input[1]], money!(8.26, USD));
        assert_eq!(map[&input[2]], money!(7.34, USD));
        assert_eq!(map[&input[3]], money!(2.89, USD));
        assert_eq!(
            total,
            map.values()
                .fold(money!(0, USD), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_fixed_point_calculations_3() {
        let input = vec![
            LineItem {
                amount: "20",
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: "5",
                priority: 100,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: "5",
                percentage: "10",
                cascade_percentage: true,
                priority: 300,
                id: 3,
                ..Default::default()
            },
            LineItem {
                percentage: "8.25",
                cascade_percentage: true,
                priority: 600,
                id: 4,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), USD);
        assert_eq!(total, money!(30.00, USD));
        assert_eq!(discount, money!(0.00, USD));
        assert_eq!(map[&input[0]], money!(16.51, USD));
        assert_eq!(map[&input[1]], money!(4.12, USD));
        assert_eq!(map[&input[2]], money!(6.89, USD));
        assert_eq!(map[&input[3]], money!(2.48, USD));
        assert_eq!(
            total,
            map.values()
                .fold(money!(0, USD), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_zero_total() {
        let input = vec![
            LineItem {
                id: 1,
                amount: "0.00",
                priority: 0,
                ..Default::default()
            },
            LineItem {
                id: 2,
                priority: 100,
                amount: "8.00",
                cascade_percentage: true,
                cascade_amount: true,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), USD);
        let zero = money!(0, USD);
        assert_eq!(total, zero);
        assert_eq!(discount, zero);
        assert_eq!(map[&input[0]], money!(-8.00, USD));
        assert_eq!(map[&input[1]], money!(8.00, USD));
        assert_eq!(
            total,
            map.values()
                .fold(money!(0, USD), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_zero_line() {
        let input = vec![
            LineItem {
                amount: "19.56",
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: "2.75",
                percentage: "5.75",
                cascade_percentage: true,
                cascade_amount: true,
                priority: 300,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: "520.36",
                priority: 100,
                id: 3,
                ..Default::default()
            },
            LineItem {
                amount: "0.00",
                priority: 100,
                id: 4,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), USD);
        assert_eq!(total, money!(539.92, USD));
        assert_eq!(discount, money!(0.00, USD));
        assert_eq!(map[&input[0]], money!(18.33, USD));
        assert_eq!(map[&input[1]], money!(33.80, USD));
        assert_eq!(map[&input[2]], money!(487.79, USD));
        assert_eq!(map[&input[3]], money!(0.00, USD));
        assert_eq!(
            total,
            map.values()
                .fold(money!(0, USD), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_complex_discount() {
        let input = vec![
            LineItem {
                amount: "0.01",
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: "0.01",
                priority: 100,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: "0.01",
                priority: 100,
                id: 3,
                ..Default::default()
            },
            LineItem {
                amount: "-5.00",
                priority: 100,
                id: 4,
                ..Default::default()
            },
            LineItem {
                amount: "10.00",
                priority: 100,
                id: 5,
                ..Default::default()
            },
            LineItem {
                amount: "0.75",
                percentage: "8",
                cascade_percentage: true,
                cascade_amount: true,
                priority: 300,
                id: 6,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), USD);
        assert_eq!(total, money!(5.03, USD));
        assert_eq!(discount, money!(-5.00, USD));
        assert_eq!(map[&input[0]], money!(0.00, USD));
        assert_eq!(map[&input[1]], money!(0.00, USD));
        assert_eq!(map[&input[2]], money!(0.00, USD));
        assert_eq!(map[&input[3]], money!(-5.00, USD));
        assert_eq!(map[&input[4]], money!(8.86, USD));
        assert_eq!(map[&input[5]], money!(1.17, USD));
        assert_eq!(
            total,
            map.values()
                .fold(money!(0, USD), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_reckon_lines() {
        let input = vec![
            LineItem {
                amount: "1",
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: "5",
                priority: 1,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: "4",
                priority: 2,
                id: 3,
                ..Default::default()
            },
        ];
        assert_eq!(
            reckon_lines(input.clone(), USD),
            money!(10.00, USD)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_non_cascading_percentage() {
        let input = vec![
            LineItem {
                amount: "5",
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: "1",
                priority: 1,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: "4",
                priority: 1,
                id: 3,
                ..Default::default()
            },
            LineItem {
                percentage: "5",
                back_into_percentage: true,
                priority: 100,
                id: 4,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), USD);
        assert_eq!(total, money!(10.52, USD));
        assert_eq!(discount, money!(0.00, USD));
        assert_eq!(map[&input[0]], money!(5.00, USD));
        assert_eq!(map[&input[1]], money!(1.00, USD));
        assert_eq!(map[&input[2]], money!(4.00, USD));
        assert_eq!(map[&input[3]], money!(0.52, USD));
    }

    #[test]
    #[timeout(100)]
    fn test_handles_many_transactions_divvied_up_for_fees() {
        let input = vec![
            LineItem {
                amount: "25.00",
                priority: 0,
                cascade_amount: false,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: "25.00",
                priority: 0,
                cascade_amount: false,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: "35.00",
                priority: 0,
                cascade_amount: false,
                id: 3,
                ..Default::default()
            },
            LineItem {
                amount: "55.00",
                priority: 0,
                cascade_amount: false,
                id: 4,
                ..Default::default()
            },
            LineItem {
                amount: "10.00",
                priority: 0,
                cascade_amount: false,
                id: 5,
                ..Default::default()
            },
            LineItem {
                amount: "5.00",
                priority: 0,
                cascade_amount: false,
                id: 6,
                ..Default::default()
            },
            LineItem {
                amount: "30.00",
                priority: 0,
                cascade_amount: false,
                id: 7,
                ..Default::default()
            },
            LineItem {
                amount: "55.00",
                priority: 0,
                cascade_amount: false,
                id: 8,
                ..Default::default()
            },
            LineItem {
                amount: "25.00",
                priority: 0,
                cascade_amount: false,
                id: 9,
                ..Default::default()
            },
            LineItem {
                amount: "5.00",
                priority: 0,
                cascade_amount: false,
                id: 10,
                ..Default::default()
            },
            LineItem {
                amount: "6.00",
                priority: 0,
                cascade_amount: false,
                id: 11,
                ..Default::default()
            },
            LineItem {
                amount: "25.00",
                priority: 0,
                cascade_amount: false,
                id: 12,
                ..Default::default()
            },
            LineItem {
                amount: "6.00",
                priority: 0,
                cascade_amount: false,
                id: 13,
                ..Default::default()
            },
            LineItem {
                amount: "3.00",
                priority: 0,
                cascade_amount: false,
                id: 14,
                ..Default::default()
            },
            LineItem {
                amount: "5.00",
                priority: 0,
                cascade_amount: false,
                id: 15,
                ..Default::default()
            },
            LineItem {
                amount: "10.06",
                priority: 1,
                cascade_amount: true,
                id: 16,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), USD);
        assert_eq!(total, money!(315, USD));
        assert_eq!(discount, money!(0, USD));
        assert_eq!(map[&input[0]], money!(24.20, USD));
        assert_eq!(map[&input[1]], money!(24.20, USD));
        assert_eq!(map[&input[2]], money!(33.88, USD));
        assert_eq!(map[&input[3]], money!(53.24, USD));
        assert_eq!(map[&input[4]], money!(9.68, USD));
        assert_eq!(map[&input[5]], money!(4.85, USD));
        assert_eq!(map[&input[6]], money!(29.04, USD));
        assert_eq!(map[&input[7]], money!(53.24, USD));
        assert_eq!(map[&input[8]], money!(24.20, USD));
        assert_eq!(map[&input[9]], money!(4.85, USD));
        assert_eq!(map[&input[10]], money!(5.80, USD));
        assert_eq!(map[&input[11]], money!(24.20, USD));
        assert_eq!(map[&input[12]], money!(5.80, USD));
        assert_eq!(map[&input[13]], money!(2.91, USD));
        assert_eq!(map[&input[14]], money!(4.84, USD));
        assert_eq!(map[&input[15]], money!(10.07, USD));
        assert_eq!(
            total,
            map.values()
                .fold(money!(0, USD), |current, item| current + *item)
        );
    }
}

#[cfg(test)]
mod helpers_tests {
    use crate::data::{Currency, Money, USD};
    use crate::funcs::divide_amount;
    use crate::money;
    use rust_decimal_macros::dec;

    #[test]
    fn test_divide_amount() {
        assert_eq!(
            divide_amount(money!(10, USD), 3),
            [money!(3.34, USD), money!(3.33, USD), money!(3.33, USD)]
        );
        assert_eq!(
            divide_amount(money!(10.01, USD), 3),
            [money!(3.34, USD), money!(3.34, USD), money!(3.33, USD)]
        );
        assert_eq!(
            divide_amount(money!(10.02, USD), 3),
            [money!(3.34, USD), money!(3.34, USD), money!(3.34, USD)],
        );
        assert_eq!(
            divide_amount(money!(10.03, USD), 3),
            [money!(3.35, USD), money!(3.34, USD), money!(3.34, USD)],
        );
    }

    #[test]
    fn test_divide_non_subunit() {
        let sur = Currency::new("SUR", None, 0);
        assert_eq!(
            divide_amount(money!(10000, sur), 3),
            [money!(3334, sur), money!(3333, sur), money!(3333, sur)],
        );
        assert_eq!(
            divide_amount(money!(10001, sur), 3),
            [money!(3334, sur), money!(3334, sur), money!(3333, sur)],
        );
        assert_eq!(
            divide_amount(money!(10003, sur), 3),
            [money!(3335, sur), money!(3334, sur), money!(3334, sur)],
        );
    }
}

#[cfg(test)]
mod comparison_tests {
    use crate::data::{Currency, Money, USD};
    use crate::money;
    use ntest::assert_false;
    use rust_decimal_macros::dec;

    #[test]
    #[should_panic(
        expected = "Attempted mathematical operation between disparate currencies: USD and CAD"
    )]
    fn test_panic_comparison_gt() {
        let cad = Currency::new("CAD", None, 2);
        let _ = money!(0, USD) > money!(0, cad);
    }

    #[test]
    #[should_panic(
        expected = "Attempted mathematical operation between disparate currencies: USD and CAD"
    )]
    fn test_panic_comparison_gte() {
        let cad = Currency::new("CAD", None, 2);
        let _ = money!(0, USD) >= money!(0, cad);
    }

    #[test]
    #[should_panic(
        expected = "Attempted mathematical operation between disparate currencies: USD and CAD"
    )]
    fn test_panic_comparison_lt() {
        let cad = Currency::new("CAD", None, 2);
        let _ = money!(0, USD) < money!(0, cad);
    }

    #[test]
    #[should_panic(
        expected = "Attempted mathematical operation between disparate currencies: USD and CAD"
    )]
    fn test_panic_comparison_lte() {
        let cad = Currency::new("CAD", None, 2);
        let _ = money!(0, USD) <= money!(0, cad);
    }

    #[test]
    fn test_eq() {
        assert_eq!(money!(0.00, USD), money!(0.00, USD));
        assert_eq!(money!(0, USD), money!(0.00, USD));
        assert_eq!(money!(5.00, USD), money!(5, USD));
        assert_eq!(money!(5.01, USD), money!(5.01000, USD));
    }

    #[test]
    fn test_ne() {
        assert_ne!(money!(0.00, USD), money!(0.01, USD));
        assert_ne!(money!(1, USD), money!(2, USD));
        assert_ne!(money!(5.00, USD), money!(5.000001, USD));
        assert_ne!(money!(5.01, USD), money!(5.01001, USD));
    }

    #[test]
    fn test_lt() {
        assert!(money!(0, USD) < money!(1, USD));
        assert!(money!(10, USD) < money!(100, USD));
        assert!(money!(-100, USD) < money!(-1, USD));
        assert_false!(money!(100, USD) < money!(100, USD));
        assert_false!(money!(1, USD) < money!(0, USD));
        assert_false!(money!(100, USD) < money!(10, USD));
        assert_false!(money!(-1, USD) < money!(-100, USD));
    }

    #[test]
    fn test_lte() {
        assert!(money!(0, USD) <= money!(1, USD));
        assert!(money!(-100, USD) <= money!(-1, USD));
        assert!(money!(0.00, USD) <= money!(0.00, USD));
        assert!(money!(0, USD) <= money!(0.00, USD));
        assert!(money!(5.00, USD) <= money!(5, USD));
        assert!(money!(5.01, USD) <= money!(5.01000, USD));
        assert_false!(money!(100, USD) <= money!(1, USD));
        assert_false!(money!(1, USD) <= money!(0, USD));
        assert_false!(money!(100, USD) <= money!(10, USD));
        assert_false!(money!(-1, USD) <= money!(-100, USD));
    }

    #[test]
    fn test_gt() {
        assert!(money!(1, USD) > money!(0, USD));
        assert!(money!(100, USD) > money!(10, USD));
        assert!(money!(-1, USD) > money!(-100, USD));
        assert_false!(money!(100, USD) > money!(100, USD));
        assert_false!(money!(100, USD) > money!(100, USD));
        assert_false!(money!(0, USD) > money!(1, USD));
        assert_false!(money!(10, USD) > money!(100, USD));
        assert_false!(money!(-100, USD) > money!(-1, USD));
    }

    #[test]
    fn test_gte() {
        assert!(money!(1, USD) >= money!(0, USD));
        assert!(money!(100, USD) >= money!(10, USD));
        assert!(money!(-1, USD) >= money!(-100, USD));
        assert!(money!(0.00, USD) >= money!(0.00, USD));
        assert!(money!(0, USD) >= money!(0.00, USD));
        assert!(money!(5.00, USD) >= money!(5, USD));
        assert!(money!(5.01, USD) >= money!(5.01000, USD));
        assert_false!(money!(0, USD) >= money!(1, USD));
        assert_false!(money!(10, USD) >= money!(100, USD));
        assert_false!(money!(-100, USD) >= money!(-1, USD));
    }
}

#[cfg(test)]
mod money_formatter {
    use crate::data::{Currency, Money, USD};
    use crate::money;
    use rust_decimal_macros::dec;

    #[test]
    fn test_no_prefix() {
        let cad = Currency::new("CAD", None, 2);
        assert_eq!(format!("{}", money!(10, cad)), "10 CAD");
    }

    #[test]
    fn test_prefix() {
        assert_eq!(format!("{}", money!(10, USD)), "$10");
    }

    #[test]
    fn test_decimal() {
        assert_eq!(format!("{}", money!(10.00, USD)), "$10.00");
    }

    #[test]
    fn test_negative() {
        assert_eq!(format!("{}", money!(-10.00, USD)), "-$10.00");
    }
}
