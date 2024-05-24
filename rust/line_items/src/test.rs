#[cfg(test)]
mod interface_tests {
    use crate::data::LineItem;
    use crate::funcs::{get_totals, reckon_lines};
    use crate::s;
    use ntest::timeout;
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
    fn test_get_totals_percentage_cascade() {
        let input = vec![
            LineItem {
                amount: s!("10.00"),
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                percentage: s!("10"),
                priority: 1,
                cascade_percentage: true,
                id: 2,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(10.00));
        assert_eq!(discount, dec!(0.00));
        assert_eq!(map[&input[0]], dec!(9.00));
        assert_eq!(map[&input[1]], dec!(1.00));
    }

    #[test]
    #[timeout(100)]
    fn test_get_totals_percentage_backed_in_cascade() {
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
                cascade_percentage: true,
                back_into_percentage: true,
                id: 2,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(10.00));
        assert_eq!(discount, dec!(0.00));
        assert_eq!(map[&input[0]], dec!(9.09));
        assert_eq!(map[&input[1]], dec!(0.91));
        assert_eq!(
            total,
            map.values().fold(dec!(0), |current, item| current + *item)
        );
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
    fn test_get_totals_percentage_with_static_cascade() {
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
                cascade_percentage: true,
                cascade_amount: true,
                priority: 1,
                id: 2,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(10.00));
        assert_eq!(discount, dec!(0.00));
        assert_eq!(map[&input[0]], dec!(8.75));
        assert_eq!(map[&input[1]], dec!(1.25));
        assert_eq!(
            total,
            map.values().fold(dec!(0), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_get_totals_percentage_no_cascade_amount() {
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
                cascade_amount: false,
                cascade_percentage: true,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(10.25));
        assert_eq!(discount, dec!(0.00));
        assert_eq!(map[&input[0]], dec!(9.00));
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
                percentage: s!("10"),
                priority: 1,
                id: 2,
                ..Default::default()
            },
            LineItem {
                percentage: s!("5"),
                priority: 1,
                id: 3,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(11.50));
        assert_eq!(discount, dec!(0));
        assert_eq!(map[&input[0]], dec!(10.00));
        assert_eq!(map[&input[1]], dec!(1));
        assert_eq!(map[&input[2]], dec!(0.50));
        assert_eq!(
            total,
            map.values().fold(dec!(0), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_get_totals_concurrent_priorities_cascade() {
        let input = vec![
            LineItem {
                amount: s!("10.00"),
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                percentage: s!("10"),
                priority: 1,
                cascade_percentage: true,
                id: 2,
                ..Default::default()
            },
            LineItem {
                percentage: s!("5"),
                priority: 1,
                cascade_percentage: true,
                id: 3,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(10));
        assert_eq!(discount, dec!(0));
        assert_eq!(map[&input[0]], dec!(8.50));
        assert_eq!(map[&input[1]], dec!(1));
        assert_eq!(map[&input[2]], dec!(0.50));
        assert_eq!(
            total,
            map.values().fold(dec!(0), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_get_totals_multi_priority_cascade_on_concurrent_priority() {
        let input = vec![
            LineItem {
                amount: s!("2"),
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: s!("8"),
                priority: 0,
                id: 2,
                ..Default::default()
            },
            LineItem {
                percentage: s!("20"),
                priority: 1,
                cascade_percentage: true,
                id: 3,
                ..Default::default()
            },
            LineItem {
                percentage: s!("10"),
                priority: 2,
                cascade_percentage: true,
                id: 4,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(10));
        assert_eq!(discount, dec!(0));
        assert_eq!(map[&input[0]], dec!(1.44));
        assert_eq!(map[&input[1]], dec!(5.76));
        assert_eq!(map[&input[2]], dec!(1.80));
        assert_eq!(map[&input[3]], dec!(1.00));
        assert_eq!(
            total,
            map.values().fold(dec!(0), |current, item| current + *item)
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
                amount: s!("100"),
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: s!("5.00"),
                priority: 100,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: s!("5.00"),
                percentage: s!("10"),
                priority: 300,
                cascade_percentage: true,
                id: 3,
                ..Default::default()
            },
            LineItem {
                percentage: s!("8.25"),
                cascade_percentage: true,
                priority: 600,
                id: 4,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(110.00));
        assert_eq!(discount, dec!(0.00));
        assert_eq!(map[&input[0]], dec!(82.57));
        assert_eq!(map[&input[1]], dec!(4.12));
        assert_eq!(map[&input[2]], dec!(14.23));
        assert_eq!(map[&input[3]], dec!(9.08));
        assert_eq!(
            total,
            map.values().fold(dec!(0), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_fixed_point_decisions_2() {
        let input = vec![
            LineItem {
                amount: s!("20"),
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: s!("10.00"),
                priority: 100,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: s!("5.00"),
                percentage: s!("10"),
                cascade_percentage: true,
                priority: 300,
                id: 3,
                ..Default::default()
            },
            LineItem {
                percentage: s!("8.25"),
                cascade_percentage: true,
                priority: 600,
                id: 4,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(35.00));
        assert_eq!(discount, dec!(0.00));
        assert_eq!(map[&input[0]], dec!(16.51));
        assert_eq!(map[&input[1]], dec!(8.26));
        assert_eq!(map[&input[2]], dec!(7.34));
        assert_eq!(map[&input[3]], dec!(2.89));
        assert_eq!(
            total,
            map.values().fold(dec!(0), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_fixed_point_calculations_3() {
        let input = vec![
            LineItem {
                amount: s!("20"),
                priority: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: s!("5"),
                priority: 100,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: s!("5"),
                percentage: s!("10"),
                cascade_percentage: true,
                priority: 300,
                id: 3,
                ..Default::default()
            },
            LineItem {
                percentage: s!("8.25"),
                cascade_percentage: true,
                priority: 600,
                id: 4,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(30.00));
        assert_eq!(discount, dec!(0.00));
        assert_eq!(map[&input[0]], dec!(16.51));
        assert_eq!(map[&input[1]], dec!(4.12));
        assert_eq!(map[&input[2]], dec!(6.89));
        assert_eq!(map[&input[3]], dec!(2.48));
        assert_eq!(
            total,
            map.values().fold(dec!(0), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_zero_total() {
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
                amount: s!("8.00"),
                cascade_percentage: true,
                cascade_amount: true,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        let zero = dec!(0);
        assert_eq!(total, zero);
        assert_eq!(discount, zero);
        assert_eq!(map[&input[0]], dec!(-8.00));
        assert_eq!(map[&input[1]], dec!(8.00));
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
                cascade_percentage: true,
                cascade_amount: true,
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
        assert_eq!(total, dec!(539.92));
        assert_eq!(discount, dec!(0.00));
        assert_eq!(map[&input[0]], dec!(18.33));
        assert_eq!(map[&input[1]], dec!(33.80));
        assert_eq!(map[&input[2]], dec!(487.79));
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
                cascade_percentage: true,
                cascade_amount: true,
                priority: 300,
                id: 6,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(5.03));
        assert_eq!(discount, dec!(-5.00));
        assert_eq!(map[&input[0]], dec!(0.00));
        assert_eq!(map[&input[1]], dec!(0.00));
        assert_eq!(map[&input[2]], dec!(0.00));
        assert_eq!(map[&input[3]], dec!(-5.00));
        assert_eq!(map[&input[4]], dec!(8.86));
        assert_eq!(map[&input[5]], dec!(1.17));
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
    fn test_non_cascading_percentage() {
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

    #[test]
    #[timeout(100)]
    fn test_handles_many_transactions_divvied_up_for_fees() {
        let input = vec![
            LineItem {
                amount: s!("25.00"),
                priority: 0,
                cascade_amount: false,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: s!("25.00"),
                priority: 0,
                cascade_amount: false,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: s!("35.00"),
                priority: 0,
                cascade_amount: false,
                id: 3,
                ..Default::default()
            },
            LineItem {
                amount: s!("55.00"),
                priority: 0,
                cascade_amount: false,
                id: 4,
                ..Default::default()
            },
            LineItem {
                amount: s!("10.00"),
                priority: 0,
                cascade_amount: false,
                id: 5,
                ..Default::default()
            },
            LineItem {
                amount: s!("5.00"),
                priority: 0,
                cascade_amount: false,
                id: 6,
                ..Default::default()
            },
            LineItem {
                amount: s!("30.00"),
                priority: 0,
                cascade_amount: false,
                id: 7,
                ..Default::default()
            },
            LineItem {
                amount: s!("55.00"),
                priority: 0,
                cascade_amount: false,
                id: 8,
                ..Default::default()
            },
            LineItem {
                amount: s!("25.00"),
                priority: 0,
                cascade_amount: false,
                id: 9,
                ..Default::default()
            },
            LineItem {
                amount: s!("5.00"),
                priority: 0,
                cascade_amount: false,
                id: 10,
                ..Default::default()
            },
            LineItem {
                amount: s!("6.00"),
                priority: 0,
                cascade_amount: false,
                id: 11,
                ..Default::default()
            },
            LineItem {
                amount: s!("25.00"),
                priority: 0,
                cascade_amount: false,
                id: 12,
                ..Default::default()
            },
            LineItem {
                amount: s!("6.00"),
                priority: 0,
                cascade_amount: false,
                id: 13,
                ..Default::default()
            },
            LineItem {
                amount: s!("3.00"),
                priority: 0,
                cascade_amount: false,
                id: 14,
                ..Default::default()
            },
            LineItem {
                amount: s!("5.00"),
                priority: 0,
                cascade_amount: false,
                id: 15,
                ..Default::default()
            },
            LineItem {
                amount: s!("10.06"),
                priority: 1,
                cascade_amount: true,
                id: 16,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(315));
        assert_eq!(discount, dec!(0));
        assert_eq!(map[&input[0]], dec!(24.20));
        assert_eq!(map[&input[1]], dec!(24.20));
        assert_eq!(map[&input[2]], dec!(33.88));
        assert_eq!(map[&input[3]], dec!(53.24));
        assert_eq!(map[&input[4]], dec!(9.68));
        assert_eq!(map[&input[5]], dec!(4.85));
        assert_eq!(map[&input[6]], dec!(29.04));
        assert_eq!(map[&input[7]], dec!(53.24));
        assert_eq!(map[&input[8]], dec!(24.20));
        assert_eq!(map[&input[9]], dec!(4.85));
        assert_eq!(map[&input[10]], dec!(5.80));
        assert_eq!(map[&input[11]], dec!(24.20));
        assert_eq!(map[&input[12]], dec!(5.80));
        assert_eq!(map[&input[13]], dec!(2.91));
        assert_eq!(map[&input[14]], dec!(4.84));
        assert_eq!(map[&input[15]], dec!(10.07));
        assert_eq!(
            total,
            map.values().fold(dec!(0), |current, item| current + *item)
        );
    }

    #[test]
    #[timeout(100)]
    fn test_missing_applicable_base_lines() {
        let input = vec![
            LineItem {
                id: 21,
                priority: 300,
                amount: s!("0.50"),
                percentage: s!("4"),
                cascade_percentage: true,
                cascade_amount: true,
                back_into_percentage: false,
                ..Default::default()
            },
            LineItem {
                id: 22,
                priority: 300,
                percentage: s!("4"),
                amount: s!("0.50"),
                cascade_percentage: true,
                cascade_amount: true,
                back_into_percentage: false,
                ..Default::default()
            },
        ];
        let result = get_totals(input.clone(), 2);
        assert_eq!(
            result.err().unwrap().to_string(),
            "No line items to distribute difference to. \
        You may be missing a base price line item, which should be included even if the base price \
        would be zero."
        )
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
            [dec!(3.34), dec!(3.33), dec!(3.33)]
        );
        assert_eq!(
            divide_amount(dec!(10.01), 3, 2),
            [dec!(3.34), dec!(3.34), dec!(3.33)]
        );
        assert_eq!(
            divide_amount(dec!(10.02), 3, 2),
            [dec!(3.34), dec!(3.34), dec!(3.34)],
        );
        assert_eq!(
            divide_amount(dec!(10.03), 3, 2),
            [dec!(3.35), dec!(3.34), dec!(3.34)],
        );
    }

    #[test]
    fn test_divide_non_subunit() {
        assert_eq!(
            divide_amount(dec!(10000), 3, 0),
            [dec!(3334), dec!(3333), dec!(3333)],
        );
        assert_eq!(
            divide_amount(dec!(10001), 3, 0),
            [dec!(3334), dec!(3334), dec!(3333)],
        );
        assert_eq!(
            divide_amount(dec!(10003), 3, 0),
            [dec!(3335), dec!(3334), dec!(3334)],
        );
    }
}
