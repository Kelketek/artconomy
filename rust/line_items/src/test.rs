#[cfg(test)]
mod interface_tests {
    use crate::data::{LineItem, TabulationError};
    use crate::funcs::{get_totals, reckon_lines};
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
    fn test_get_totals_percentage_cascade() {
        let input = vec![
            LineItem {
                amount: s!("10.00"),
                priority: 0,
                cascade_under: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                percentage: s!("10"),
                priority: 1,
                cascade_under: 1,
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
    fn test_get_totals_percentage_cascade_selective() {
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
                percentage: s!("10"),
                priority: 200,
                cascade_under: 100,
                cascade_percentage: true,
                id: 3,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(15.00));
        assert_eq!(discount, dec!(0.00));
        assert_eq!(map[&input[0]], dec!(8.50));
        assert_eq!(map[&input[1]], dec!(5.00));
        assert_eq!(map[&input[2]], dec!(1.50));
    }

    #[test]
    #[timeout(100)]
    fn test_get_totals_amount_cascade_selective() {
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
                cascade_under: 100,
                cascade_amount: true,
                id: 3,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(15.00));
        assert_eq!(discount, dec!(0.00));
        assert_eq!(map[&input[0]], dec!(8.00));
        assert_eq!(map[&input[1]], dec!(5.00));
        assert_eq!(map[&input[2]], dec!(2.00));
    }

    #[test]
    #[timeout(100)]
    fn test_get_totals_amount_cascade_none_below() {
        let input = vec![
            LineItem {
                amount: s!("10.00"),
                priority: 100,
                cascade_under: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: s!("5.00"),
                priority: 200,
                cascade_under: 200,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: s!("2.00"),
                priority: 300,
                cascade_under: 0,
                cascade_amount: true,
                id: 3,
                ..Default::default()
            },
        ];
        let result = get_totals(input, 2);
        assert_eq!(
            result,
            Err(TabulationError::from(
                "No line items to distribute difference to. You may be missing a base price \
                line item, which should be included even if the base price would be zero."
            ))
        )
    }

    #[test]
    #[timeout(100)]
    fn test_get_totals_percentage_backed_in_cascade() {
        let input = vec![
            LineItem {
                amount: s!("10.00"),
                priority: 0,
                cascade_under: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                percentage: s!("10.00"),
                priority: 1,
                cascade_under: 1,
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
                cascade_under: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                percentage: s!("10"),
                amount: s!("0.25"),
                priority: 1,
                cascade_under: 0,
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
                cascade_under: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                percentage: s!("10"),
                amount: s!("0.25"),
                cascade_percentage: true,
                cascade_amount: true,
                priority: 1,
                cascade_under: 1,
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
    fn test_get_totals_percentage_with_static_cascade_under() {
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
                percentage: s!("10"),
                amount: s!("0.25"),
                cascade_percentage: true,
                cascade_amount: true,
                priority: 200,
                cascade_under: 100,
                id: 3,
                ..Default::default()
            },
        ];
        let (total, discount, map) = get_totals(input.clone(), 2).unwrap();
        assert_eq!(total, dec!(15.00));
        assert_eq!(discount, dec!(0.00));
        assert_eq!(map[&input[0]], dec!(8.25));
        assert_eq!(map[&input[1]], dec!(5.00));
        assert_eq!(map[&input[2]], dec!(1.75));
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
                cascade_under: 1,
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
                cascade_under: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: s!("2.00"),
                priority: 10,
                cascade_under: 10,
                id: 1,
                ..Default::default()
            },
            LineItem {
                percentage: s!("10"),
                amount: s!(".05"),
                priority: 100,
                cascade_under: 50,
                id: 2,
                ..Default::default()
            },
            LineItem {
                percentage: s!("5"),
                amount: s!("0.08"),
                priority: 100,
                cascade_under: 50,
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
    fn test_get_totals_concurrent_priorities_cascade() {
        let input = vec![
            LineItem {
                amount: s!("10.00"),
                priority: 0,
                cascade_under: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                percentage: s!("10"),
                priority: 1,
                cascade_under: 1,
                cascade_percentage: true,
                id: 2,
                ..Default::default()
            },
            LineItem {
                percentage: s!("5"),
                priority: 1,
                cascade_under: 1,
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
                cascade_under: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: s!("8"),
                priority: 0,
                cascade_under: 0,
                id: 2,
                ..Default::default()
            },
            LineItem {
                percentage: s!("20"),
                priority: 1,
                cascade_under: 1,
                cascade_percentage: true,
                id: 3,
                ..Default::default()
            },
            LineItem {
                percentage: s!("10"),
                priority: 2,
                cascade_under: 2,
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
                amount: s!("5.00"),
                percentage: s!("10"),
                priority: 300,
                cascade_under: 300,
                cascade_percentage: true,
                id: 3,
                ..Default::default()
            },
            LineItem {
                percentage: s!("8.25"),
                cascade_percentage: true,
                priority: 600,
                cascade_under: 600,
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
                cascade_under: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: s!("10.00"),
                priority: 100,
                cascade_under: 100,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: s!("5.00"),
                percentage: s!("10"),
                cascade_percentage: true,
                priority: 300,
                cascade_under: 300,
                id: 3,
                ..Default::default()
            },
            LineItem {
                percentage: s!("8.25"),
                cascade_percentage: true,
                priority: 600,
                cascade_under: 600,
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
                cascade_under: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: s!("5"),
                priority: 100,
                cascade_under: 100,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: s!("5"),
                percentage: s!("10"),
                cascade_percentage: true,
                priority: 300,
                cascade_under: 300,
                id: 3,
                ..Default::default()
            },
            LineItem {
                percentage: s!("8.25"),
                cascade_percentage: true,
                priority: 600,
                cascade_under: 600,
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
                cascade_under: 0,
                ..Default::default()
            },
            LineItem {
                id: 2,
                priority: 100,
                cascade_under: 100,
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
                cascade_under: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: s!("2.75"),
                percentage: s!("5.75"),
                cascade_percentage: true,
                cascade_amount: true,
                priority: 300,
                cascade_under: 300,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: s!("520.36"),
                priority: 100,
                cascade_under: 100,
                id: 3,
                ..Default::default()
            },
            LineItem {
                amount: s!("0.00"),
                priority: 100,
                cascade_under: 100,
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
                cascade_under: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: s!("0.01"),
                priority: 100,
                cascade_under: 100,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: s!("0.01"),
                priority: 100,
                cascade_under: 100,
                id: 3,
                ..Default::default()
            },
            LineItem {
                amount: s!("-5.00"),
                priority: 100,
                cascade_under: 100,
                id: 4,
                ..Default::default()
            },
            LineItem {
                amount: s!("10.00"),
                priority: 100,
                cascade_under: 100,
                id: 5,
                ..Default::default()
            },
            LineItem {
                amount: s!("0.75"),
                percentage: s!("8"),
                cascade_percentage: true,
                cascade_amount: true,
                priority: 300,
                cascade_under: 300,
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
                cascade_under: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: s!("5"),
                priority: 1,
                cascade_under: 1,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: s!("4"),
                priority: 2,
                cascade_under: 2,
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
                cascade_under: 0,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: s!("1"),
                priority: 1,
                cascade_under: 1,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: s!("4"),
                priority: 1,
                cascade_under: 1,
                id: 3,
                ..Default::default()
            },
            LineItem {
                percentage: s!("5"),
                back_into_percentage: true,
                priority: 100,
                cascade_under: 100,
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
                cascade_under: 0,
                cascade_amount: false,
                id: 1,
                ..Default::default()
            },
            LineItem {
                amount: s!("25.00"),
                priority: 0,
                cascade_under: 0,
                cascade_amount: false,
                id: 2,
                ..Default::default()
            },
            LineItem {
                amount: s!("35.00"),
                priority: 0,
                cascade_under: 0,
                cascade_amount: false,
                id: 3,
                ..Default::default()
            },
            LineItem {
                amount: s!("55.00"),
                priority: 0,
                cascade_under: 0,
                cascade_amount: false,
                id: 4,
                ..Default::default()
            },
            LineItem {
                amount: s!("10.00"),
                priority: 0,
                cascade_under: 0,
                cascade_amount: false,
                id: 5,
                ..Default::default()
            },
            LineItem {
                amount: s!("5.00"),
                priority: 0,
                cascade_under: 0,
                cascade_amount: false,
                id: 6,
                ..Default::default()
            },
            LineItem {
                amount: s!("30.00"),
                priority: 0,
                cascade_under: 0,
                cascade_amount: false,
                id: 7,
                ..Default::default()
            },
            LineItem {
                amount: s!("55.00"),
                priority: 0,
                cascade_under: 0,
                cascade_amount: false,
                id: 8,
                ..Default::default()
            },
            LineItem {
                amount: s!("25.00"),
                priority: 0,
                cascade_under: 0,
                cascade_amount: false,
                id: 9,
                ..Default::default()
            },
            LineItem {
                amount: s!("5.00"),
                priority: 0,
                cascade_under: 0,
                cascade_amount: false,
                id: 10,
                ..Default::default()
            },
            LineItem {
                amount: s!("6.00"),
                priority: 0,
                cascade_under: 0,
                cascade_amount: false,
                id: 11,
                ..Default::default()
            },
            LineItem {
                amount: s!("25.00"),
                priority: 0,
                cascade_under: 0,
                cascade_amount: false,
                id: 12,
                ..Default::default()
            },
            LineItem {
                amount: s!("6.00"),
                priority: 0,
                cascade_under: 0,
                cascade_amount: false,
                id: 13,
                ..Default::default()
            },
            LineItem {
                amount: s!("3.00"),
                priority: 0,
                cascade_under: 0,
                cascade_amount: false,
                id: 14,
                ..Default::default()
            },
            LineItem {
                amount: s!("5.00"),
                priority: 0,
                cascade_under: 0,
                cascade_amount: false,
                id: 15,
                ..Default::default()
            },
            LineItem {
                amount: s!("10.06"),
                priority: 1,
                cascade_under: 1,
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
                cascade_under: 300,
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
                cascade_under: 300,
                percentage: s!("4"),
                amount: s!("0.50"),
                cascade_percentage: true,
                cascade_amount: true,
                back_into_percentage: false,
                ..Default::default()
            },
        ];
        let result = get_totals(input, 2);
        assert_eq!(
            result.err().unwrap().to_string(),
            "No line items to distribute difference to. \
        You may be missing a base price line item, which should be included even if the base price \
        would be zero."
        )
    }
}

#[cfg(test)]
macro_rules! assert_same_subtotals {
    ($left: expr, $right: expr) => {
        let mut left_subtotals = HashMap::<LineType, String>::new();
        for (key, value) in $left.into_iter() {
            left_subtotals.insert(key.kind, value.to_string());
        }
        let mut right_subtotals = HashMap::<LineType, String>::new();
        for (key, value) in $right.into_iter() {
            right_subtotals.insert(key.kind, value.to_string());
        }
        assert_eq!(left_subtotals, right_subtotals)
    };
}

#[cfg(test)]
macro_rules! reversible_deliverable_lines {
    ($($name:ident: $value:expr,)*) => {
    $(
        #[test]
        #[timeout(100)]
        fn $name() {
            let non_cascade_parameters = $value;
            let mut cascade_parameters = non_cascade_parameters.clone();
            cascade_parameters.cascade = true;
            println!("Non-cascading");
            let non_cascade_lines = deliverable_lines(non_cascade_parameters)
                .expect("Failed on non-cascade line generation!");
            let (non_cascade_total, _non_cascade_discount, non_cascade_map) =
                get_totals(non_cascade_lines.clone(), 2).expect("Failed on non-cascade tally.");
            cascade_parameters.base_price = non_cascade_total.to_string();
            println!("Cascading");
            let cascade_lines =
                deliverable_lines(cascade_parameters).expect("Failed on cascade line generation!");
            let (_cascade_total, _cascade_discount, cascade_map) =
                get_totals(cascade_lines.clone(), 2).expect("Failed on cascade tally.");
            assert_same_subtotals!(non_cascade_map, cascade_map);
        }
    )*
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
            cascade: true,
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
                cascade_under: 0,
                kind: LineType::BasePrice,
                amount: s!("25.00"),
                category: Category::EscrowHold,
                frozen_value: None,
                percentage: s!("0"),
                description: s!(""),
                cascade_amount: false,
                cascade_percentage: false,
                back_into_percentage: false,
                destination_user_id: Some(-1),
                destination_account: Account::Escrow,
            },
            LineItem {
                id: -5,
                priority: 330,
                cascade_under: 201,
                kind: LineType::Shield,
                cascade_percentage: true,
                cascade_amount: true,
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
                cascade_under: 201,
                kind: LineType::CardFee,
                amount: s!("0.30"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("3.30"),
                category: Category::ThirdPartyFee,
                cascade_percentage: true,
                cascade_amount: true,
                back_into_percentage: false,
                destination_account: Account::Fund,
                destination_user_id: None,
            },
            LineItem {
                id: -9,
                priority: 325,
                cascade_under: 201,
                kind: LineType::PayoutFee,
                amount: s!(".25"),
                percentage: s!("1.25"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                cascade_amount: true,
                back_into_percentage: false,
                frozen_value: None,
                description: s!(""),
            },
            LineItem {
                id: -10,
                priority: 325,
                cascade_under: 201,
                kind: LineType::ConnectFee,
                amount: s!("2.00"),
                percentage: s!("0"),
                cascade_percentage: true,
                cascade_amount: true,
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
            cascade: true,
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
                cascade_under: 0,
                kind: LineType::BasePrice,
                amount: s!("0.00"),
                category: Category::EscrowHold,
                frozen_value: None,
                percentage: s!("0"),
                description: s!(""),
                cascade_amount: false,
                cascade_percentage: false,
                back_into_percentage: false,
                destination_user_id: Some(-1),
                destination_account: Account::Escrow,
            },
            LineItem {
                id: -6,
                priority: 300,
                cascade_under: 201,
                kind: LineType::DeliverableTracking,
                amount: s!("1.35"),
                percentage: s!("0"),
                back_into_percentage: false,
                cascade_amount: true,
                cascade_percentage: true,
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
            cascade: true,
            international: false,
            plan_name: Some(s!("Basic")),
            table_product: false,
            extra_lines: vec![LineItem {
                id: 5,
                priority: 0,
                cascade_under: 0,
                kind: LineType::BasePrice,
                amount: s!("8.50"),
                category: Category::EscrowHold,
                frozen_value: None,
                percentage: s!("0"),
                description: s!(""),
                cascade_amount: false,
                cascade_percentage: false,
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
                cascade_under: 201,
                kind: LineType::Shield,
                cascade_percentage: true,
                cascade_amount: true,
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
                cascade_under: 201,
                kind: LineType::CardFee,
                amount: s!("0.30"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("3.30"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                back_into_percentage: false,
                cascade_amount: true,
            },
            LineItem {
                id: -9,
                priority: 325,
                cascade_under: 201,
                kind: LineType::PayoutFee,
                amount: s!(".25"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("1.25"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                back_into_percentage: false,
                cascade_amount: true,
            },
            LineItem {
                id: -10,
                priority: 325,
                cascade_under: 201,
                kind: LineType::ConnectFee,
                amount: s!("2.00"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("0"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                back_into_percentage: false,
                cascade_amount: true,
            },
            LineItem {
                id: 5,
                priority: 0,
                cascade_under: 0,
                kind: LineType::BasePrice,
                amount: s!("8.50"),
                category: Category::EscrowHold,
                frozen_value: None,
                percentage: s!("0"),
                description: s!(""),
                cascade_amount: false,
                cascade_percentage: false,
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
            cascade: true,
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
                cascade_under: 0,
                kind: LineType::BasePrice,
                amount: s!("25.00"),
                category: Category::EscrowHold,
                frozen_value: None,
                percentage: s!("0"),
                cascade_amount: false,
                cascade_percentage: false,
                back_into_percentage: false,
                description: s!(""),
                destination_user_id: Some(-2),
                destination_account: Account::Escrow,
            },
            LineItem {
                id: -5,
                priority: 330,
                cascade_under: 201,
                kind: LineType::Shield,
                cascade_percentage: true,
                cascade_amount: true,
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
                cascade_under: 201,
                kind: LineType::CardFee,
                amount: s!("0.30"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("3.30"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                back_into_percentage: false,
                cascade_amount: true,
            },
            LineItem {
                id: -9,
                priority: 325,
                cascade_under: 201,
                kind: LineType::PayoutFee,
                amount: s!(".25"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("1.25"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                back_into_percentage: false,
                cascade_amount: true,
            },
            LineItem {
                id: -10,
                priority: 325,
                cascade_under: 201,
                kind: LineType::ConnectFee,
                amount: s!("2.00"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("0"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                back_into_percentage: false,
                cascade_amount: true,
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
            cascade: true,
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
                cascade_under: 0,
                kind: LineType::BasePrice,
                amount: s!("10.00"),
                frozen_value: None,
                percentage: s!("0"),
                description: s!(""),
                category: Category::EscrowHold,
                cascade_amount: false,
                cascade_percentage: false,
                back_into_percentage: false,
                destination_user_id: Some(-1),
                destination_account: Account::Escrow,
            },
            LineItem {
                id: -5,
                priority: 330,
                cascade_under: 201,
                kind: LineType::Shield,
                cascade_percentage: true,
                cascade_amount: true,
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
                cascade_under: 201,
                kind: LineType::CardFee,
                amount: s!("0.30"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("3.30"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                back_into_percentage: false,
                cascade_amount: true,
            },
            LineItem {
                id: -9,
                priority: 325,
                cascade_under: 201,
                kind: LineType::PayoutFee,
                amount: s!(".25"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("1.25"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                back_into_percentage: false,
                cascade_amount: true,
            },
            LineItem {
                id: -10,
                priority: 325,
                cascade_under: 201,
                kind: LineType::ConnectFee,
                amount: s!("2.00"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("0"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                back_into_percentage: false,
                cascade_amount: true,
            },
            LineItem {
                id: -2,
                priority: 100,
                cascade_under: 100,
                kind: LineType::AddOn,
                amount: s!("15.00"),
                frozen_value: None,
                category: Category::EscrowHold,
                percentage: s!("0"),
                description: s!(""),
                cascade_amount: false,
                cascade_percentage: false,
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
            cascade: true,
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
                cascade_under: 0,
                kind: LineType::BasePrice,
                amount: s!("10.00"),
                frozen_value: None,
                percentage: s!("0"),
                description: s!(""),
                category: Category::EscrowHold,
                cascade_amount: false,
                cascade_percentage: false,
                back_into_percentage: false,
                destination_user_id: Some(-1),
                destination_account: Account::Escrow,
            },
            LineItem {
                id: -5,
                priority: 330,
                cascade_under: 201,
                kind: LineType::Shield,
                category: Category::ShieldFee,
                cascade_percentage: true,
                cascade_amount: true,
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
                cascade_under: 201,
                kind: LineType::CardFee,
                amount: s!("0.30"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("3.30"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                back_into_percentage: false,
                cascade_amount: true,
            },
            LineItem {
                id: -9,
                priority: 325,
                cascade_under: 201,
                kind: LineType::PayoutFee,
                amount: s!(".25"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("1.25"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                back_into_percentage: false,
                cascade_amount: true,
            },
            LineItem {
                id: -8,
                priority: 325,
                cascade_under: 201,
                kind: LineType::CrossBorderTransferFee,
                amount: s!("0"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("1"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                back_into_percentage: false,
                cascade_amount: true,
            },
            LineItem {
                id: -10,
                priority: 325,
                cascade_under: 201,
                kind: LineType::ConnectFee,
                amount: s!("2.00"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("0"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                back_into_percentage: false,
                cascade_amount: true,
            },
            LineItem {
                id: -2,
                priority: 100,
                cascade_under: 100,
                kind: LineType::AddOn,
                amount: s!("15.00"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("0"),
                category: Category::EscrowHold,
                destination_user_id: Some(-1),
                destination_account: Account::Escrow,
                cascade_percentage: false,
                back_into_percentage: false,
                cascade_amount: false,
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
            cascade: true,
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
                cascade_under: 0,
                kind: LineType::BasePrice,
                category: Category::EscrowHold,
                amount: s!("10.00"),
                frozen_value: None,
                percentage: s!("0"),
                description: s!(""),
                cascade_amount: false,
                cascade_percentage: false,
                back_into_percentage: false,
                destination_user_id: Some(-3),
                destination_account: Account::Escrow,
            },
            LineItem {
                id: -3,
                priority: 400,
                cascade_under: 201,
                kind: LineType::TableService,
                cascade_percentage: true,
                cascade_amount: true,
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
                cascade_under: 201,
                kind: LineType::Tax,
                cascade_amount: true,
                cascade_percentage: true,
                back_into_percentage: true,
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
                cascade_under: 201,
                kind: LineType::CardFee,
                amount: s!("0.30"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("3.30"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                back_into_percentage: false,
                cascade_amount: true,
            },
            LineItem {
                id: -9,
                priority: 325,
                cascade_under: 201,
                kind: LineType::PayoutFee,
                amount: s!(".25"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("1.25"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                back_into_percentage: false,
                cascade_amount: true,
            },
            LineItem {
                id: -10,
                priority: 325,
                cascade_under: 201,
                kind: LineType::ConnectFee,
                amount: s!("2.00"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("0"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                back_into_percentage: false,
                cascade_amount: true,
            },
            LineItem {
                id: -2,
                priority: 100,
                cascade_under: 100,
                kind: LineType::AddOn,
                amount: s!("15.00"),
                frozen_value: None,
                percentage: s!("0"),
                description: s!(""),
                category: Category::EscrowHold,
                cascade_amount: false,
                cascade_percentage: false,
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
            cascade: true,
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
                cascade_under: 0,
                kind: LineType::BasePrice,
                amount: s!("25.00"),
                frozen_value: None,
                percentage: s!("0"),
                description: s!(""),
                category: Category::EscrowHold,
                cascade_amount: false,
                cascade_percentage: false,
                back_into_percentage: false,
                destination_user_id: Some(-1),
                destination_account: Account::Escrow,
            },
            LineItem {
                id: -6,
                priority: 300,
                cascade_under: 201,
                kind: LineType::DeliverableTracking,
                amount: s!("1.35"),
                percentage: s!("0"),
                back_into_percentage: false,
                cascade_amount: true,
                cascade_percentage: true,
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
            cascade: true,
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
                cascade_under: 0,
                kind: LineType::BasePrice,
                amount: s!("10.00"),
                category: Category::EscrowHold,
                frozen_value: None,
                percentage: s!("0"),
                description: s!(""),
                cascade_amount: false,
                cascade_percentage: false,
                back_into_percentage: false,
                destination_user_id: Some(4),
                destination_account: Account::Escrow,
            },
            LineItem {
                id: -6,
                priority: 300,
                cascade_under: 201,
                kind: LineType::DeliverableTracking,
                category: Category::SubscriptionDues,
                amount: s!("1.35"),
                percentage: s!("0"),
                cascade_percentage: true,
                cascade_amount: true,
                back_into_percentage: false,
                frozen_value: None,
                description: s!(""),
                destination_account: Account::Fund,
                destination_user_id: None,
            },
            LineItem {
                id: -2,
                priority: 100,
                cascade_under: 100,
                kind: LineType::AddOn,
                amount: s!("15.00"),
                percentage: s!("0"),
                description: s!(""),
                cascade_amount: false,
                cascade_percentage: false,
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
            cascade: true,
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
            cascade: true,
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
            cascade: true,
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
            cascade: true,
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
                cascade_under: 201,
                kind: LineType::Processing,
                amount: s!("0.15"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("1"),
                category: Category::ProcessingFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                back_into_percentage: false,
                cascade_amount: true,
            },
            LineItem {
                id: -7,
                priority: 350,
                cascade_under: 201,
                kind: LineType::CardFee,
                amount: s!("0.30"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("3.30"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                back_into_percentage: false,
                cascade_amount: true,
            },
            LineItem {
                id: -9,
                priority: 325,
                cascade_under: 201,
                kind: LineType::PayoutFee,
                amount: s!(".25"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("1.25"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                back_into_percentage: false,
                cascade_amount: true,
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
                cascade_under: 201,
                kind: LineType::Processing,
                amount: s!("0.15"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("2"),
                category: Category::ProcessingFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                back_into_percentage: false,
                cascade_amount: true,
            },
            LineItem {
                id: -7,
                priority: 350,
                cascade_under: 201,
                kind: LineType::CardFee,
                amount: s!("0.30"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("3.30"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                back_into_percentage: false,
                cascade_amount: true,
            },
            LineItem {
                id: -9,
                priority: 325,
                cascade_under: 201,
                kind: LineType::PayoutFee,
                amount: s!(".25"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("1.25"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                back_into_percentage: false,
                cascade_amount: true,
            },
            LineItem {
                id: -8,
                priority: 325,
                cascade_under: 201,
                kind: LineType::CrossBorderTransferFee,
                amount: s!("0"),
                description: s!(""),
                frozen_value: None,
                percentage: s!("1"),
                category: Category::ThirdPartyFee,
                destination_user_id: None,
                destination_account: Account::Fund,
                cascade_percentage: true,
                back_into_percentage: false,
                cascade_amount: true,
            },
        ];
        assert_eq!(tip_fee_lines(parameters), Ok(expected));
    }
}

#[cfg(test)]
mod test_helpers {
    use crate::data::{Pricing, ServicePlan};
    use crate::s;

    pub fn gen_pricing() -> Pricing {
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
}

#[cfg(test)]
mod cascade_reversability_tests {
    use crate::data::{DeliverableLinesContext, LineItem, LineType};
    use crate::funcs::{deliverable_lines, get_totals};
    use crate::s;
    use crate::test::test_helpers::gen_pricing;
    use ntest::timeout;
    use pretty_assertions::assert_eq;
    use rust_decimal_macros::dec;
    use std::collections::HashMap;

    /// Test the simplest round-trip cascade-vs-non-cascade equivalent, to make it easier
    /// to diagnose any issues.
    #[test]
    fn test_simplest_round_trip() {
        let non_cascaded = vec![
            LineItem {
                id: 0,
                kind: LineType::BasePrice,
                priority: 0,
                cascade_under: 0,
                amount: s!("10.00"),
                percentage: s!("0"),
                cascade_percentage: false,
                ..Default::default()
            },
            LineItem {
                id: 1,
                kind: LineType::CardFee,
                priority: 1,
                cascade_under: 1,
                percentage: s!("5"),
                cascade_percentage: false,
                ..Default::default()
            },
            LineItem {
                id: 2,
                kind: LineType::Shield,
                priority: 2,
                cascade_under: 2,
                percentage: s!("10"),
                cascade_percentage: false,
                ..Default::default()
            },
        ];
        let (non_cascade_total, _non_cascade_discount, non_cascaded_map) =
            get_totals(non_cascaded, 2).unwrap();
        assert_eq!(non_cascade_total, dec!(11.55));
        let cascaded = vec![
            LineItem {
                id: 0,
                kind: LineType::BasePrice,
                priority: 0,
                cascade_under: 0,
                // Update this to match the previous total assertion to keep
                // test valid, if changing.
                amount: s!("11.55"),
                percentage: s!("0"),
                cascade_percentage: false,
                ..Default::default()
            },
            LineItem {
                id: 1,
                kind: LineType::CardFee,
                priority: 1,
                cascade_under: 1,
                percentage: s!("5"),
                cascade_percentage: true,

                ..Default::default()
            },
            LineItem {
                id: 2,
                kind: LineType::Shield,
                priority: 2,
                cascade_under: 2,
                percentage: s!("10"),
                cascade_percentage: true,
                ..Default::default()
            },
        ];
        let (cascade_total, _cascade_discount, cascaded_map) = get_totals(cascaded, 2).unwrap();
        assert_eq!(cascade_total, dec!(11.55));
        assert_same_subtotals!(non_cascaded_map, cascaded_map);
    }

    #[test]
    fn test_back_into_percentage_matters() {
        let non_cascaded = vec![
            LineItem {
                id: 0,
                kind: LineType::BasePrice,
                priority: 0,
                cascade_under: 0,
                amount: s!("100.00"),
                percentage: s!("0"),
                cascade_percentage: false,
                ..Default::default()
            },
            LineItem {
                id: 1,
                kind: LineType::CardFee,
                priority: 1,
                cascade_under: 1,
                percentage: s!("5"),
                cascade_percentage: false,
                ..Default::default()
            },
        ];
        let (non_cascade_total, _non_cascade_discount, non_cascaded_map) =
            get_totals(non_cascaded, 2).unwrap();
        assert_eq!(non_cascade_total, dec!(105.00));
        let cascaded = vec![
            LineItem {
                id: 0,
                kind: LineType::BasePrice,
                priority: 0,
                cascade_under: 0,
                // Update this to match the previous total assertion to keep
                // test valid, if changing.
                amount: s!("105.00"),
                percentage: s!("0"),
                cascade_percentage: false,
                ..Default::default()
            },
            LineItem {
                id: 1,
                kind: LineType::CardFee,
                priority: 1,
                cascade_under: 1,
                percentage: s!("5"),
                cascade_percentage: true,
                back_into_percentage: false,
                ..Default::default()
            },
        ];
        let (cascade_total, _cascade_discount, cascaded_map) = get_totals(cascaded, 2).unwrap();
        assert_eq!(cascade_total, dec!(105.00));
        assert_same_subtotals!(non_cascaded_map.clone(), cascaded_map);
        let back_into_cascaded = vec![
            LineItem {
                id: 0,
                kind: LineType::BasePrice,
                priority: 0,
                cascade_under: 0,
                // Update this to match the previous total assertion to keep
                // test valid, if changing.
                amount: s!("105.00"),
                percentage: s!("0"),
                cascade_percentage: false,
                ..Default::default()
            },
            LineItem {
                id: 1,
                kind: LineType::CardFee,
                priority: 1,
                cascade_under: 1,
                percentage: s!("5"),
                cascade_percentage: true,
                back_into_percentage: false,
                ..Default::default()
            },
        ];
        let (back_into_total, _back_into_discount, back_into_map) = get_totals(back_into_cascaded, 2).unwrap();
        assert_eq!(back_into_total, dec!(10.50));
        assert_same_subtotals!(non_cascaded_map, back_into_map);
    }

    /// Test the simplest round-trip cascade-vs-non-cascade equivalent, to make it easier
    /// to diagnose any issues.
    #[test]
    fn test_simplest_round_trip_back_into_percentage_when_cascading() {
        let non_cascaded = vec![
            LineItem {
                id: 0,
                kind: LineType::BasePrice,
                priority: 0,
                cascade_under: 0,
                amount: s!("10.00"),
                percentage: s!("0"),
                cascade_percentage: false,
                ..Default::default()
            },
            LineItem {
                id: 1,
                kind: LineType::CardFee,
                priority: 1,
                cascade_under: 1,
                percentage: s!("5"),
                cascade_percentage: false,
                ..Default::default()
            },
            LineItem {
                id: 2,
                kind: LineType::Shield,
                priority: 2,
                cascade_under: 2,
                percentage: s!("10"),
                cascade_percentage: false,
                ..Default::default()
            },
        ];
        let (non_cascade_total, _non_cascade_discount, non_cascaded_map) =
            get_totals(non_cascaded, 2).unwrap();
        assert_eq!(non_cascade_total, dec!(11.55));
        let cascaded = vec![
            LineItem {
                id: 0,
                kind: LineType::BasePrice,
                priority: 0,
                cascade_under: 0,
                // Update this to match the previous total assertion to keep
                // test valid, if changing.
                amount: s!("11.55"),
                percentage: s!("0"),
                cascade_percentage: false,
                back_into_percentage: true,
                ..Default::default()
            },
            LineItem {
                id: 1,
                kind: LineType::CardFee,
                priority: 1,
                cascade_under: 1,
                percentage: s!("5"),
                cascade_percentage: true,
                back_into_percentage: true,
                ..Default::default()
            },
            LineItem {
                id: 2,
                kind: LineType::Shield,
                priority: 2,
                cascade_under: 2,
                percentage: s!("10"),
                cascade_percentage: true,
                back_into_percentage: true,
                ..Default::default()
            },
        ];
        let (cascade_total, _cascade_discount, cascaded_map) = get_totals(cascaded, 2).unwrap();
        assert_eq!(cascade_total, dec!(11.55));
        assert_same_subtotals!(non_cascaded_map, cascaded_map);
    }

    reversible_deliverable_lines! {
        test_reversible_basic: DeliverableLinesContext {
            escrow_enabled: true,
            table_product: false,
            pricing: Some(gen_pricing()),
            base_price: s!("10.00"),
            cascade: false,
            international: false,
            plan_name: Some(s!("Basic")),
            user_id: -1,
            allow_soft_failure: false,
            quantization: 2,
            extra_lines: vec![],
        },
        test_reversible_table: DeliverableLinesContext {
            escrow_enabled: true,
            table_product: true,
            pricing: Some(gen_pricing()),
            base_price: s!("10.00"),
            cascade: false,
            international: false,
            plan_name: Some(s!("Basic")),
            user_id: -1,
            allow_soft_failure: false,
            quantization: 2,
            extra_lines: vec![],
        },
        test_reversible_international: DeliverableLinesContext {
            escrow_enabled: true,
            table_product: false,
            pricing: Some(gen_pricing()),
            base_price: s!("10.00"),
            cascade: false,
            international: true,
            plan_name: Some(s!("Basic")),
            user_id: -1,
            allow_soft_failure: false,
            quantization: 2,
            extra_lines: vec![],
        },
        test_reversible_non_escrow: DeliverableLinesContext {
            escrow_enabled: false,
            table_product: false,
            pricing: Some(gen_pricing()),
            base_price: s!("10.00"),
            cascade: false,
            international: false,
            plan_name: Some(s!("Basic")),
            user_id: -1,
            allow_soft_failure: false,
            quantization: 2,
            extra_lines: vec![],
        },
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
