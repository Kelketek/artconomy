import {genLineItem, genPricing} from '@/lib/specs/helpers.ts'
import {getTotals, invoiceLines, linesByPriority, reckonLines} from '@/lib/lineItemFunctions.ts'
import {Decimal} from 'decimal.js'
import {genProduct} from '@/specs/helpers/fixtures.ts'
import {describe, expect, test} from 'vitest'

describe('lineItemFunctions.ts', () => {
  // NOTE: Comment under each test label the name of its
  // matching backend test so that we can easily keep them in sync.
  test('Sorts by priority', () => {
    // test_line_sort
    const lines = [
      genLineItem({amount: 5, priority: 0}),
      genLineItem({amount: 6, priority: 1}),
      genLineItem({amount: 7, priority: 2}),
      genLineItem({amount: 8, priority: 2}),
      genLineItem({amount: 9, priority: 1}),
      genLineItem({amount: 10, priority: -1}),
    ]
    const prioritySet = linesByPriority(lines)
    const expectedResult = [
      [genLineItem({amount: 10, priority: -1})],
      [genLineItem({amount: 5, priority: 0})],
      [
        genLineItem({amount: 6, priority: 1}),
        genLineItem({amount: 9, priority: 1}),
      ],
      [
        genLineItem({amount: 7, priority: 2}),
        genLineItem({amount: 8, priority: 2}),
      ],
    ]
    expect(prioritySet).toEqual(expectedResult)
  })
  test('Gets the total for a single line', () => {
    // test_get_totals_single_line
    const source = [genLineItem({amount: 10, priority: 0})]
    const result = getTotals(source)
    expect(result).toEqual(
      {
        total: new Decimal('10'),
        discount: new Decimal('0'),
        subtotals: new Map([
          [genLineItem({amount: 10, priority: 0}), new Decimal('10')],
        ]),
      })
  })
  test('Gets the totals for a percentage modifier', () => {
    // test_get_totals_percentage_line
    const source = [
      genLineItem({amount: 10, priority: 0}),
      genLineItem({percentage: 10, priority: 1}),
    ]
    const result = getTotals(source)
    expect(result).toEqual(
      {
        total: new Decimal('11'),
        discount: new Decimal('0'),
        subtotals: new Map([
          [genLineItem({amount: 10, priority: 0}), new Decimal('10')],
          [genLineItem({percentage: 10, priority: 1}), new Decimal('1')],
        ]),
      },
    )
  })
  test('Gets the total with a cascading percentage modifier', () => {
    // test_get_totals_percentage_cascade
    const source = [
      genLineItem({amount: 10, priority: 0}),
      genLineItem({percentage: 10, priority: 1, cascade_percentage: true}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: new Decimal('10'),
      discount: new Decimal('0'),
      subtotals: new Map([
        [genLineItem({amount: 10, priority: 0}), new Decimal('9')],
        [genLineItem({percentage: 10, priority: 1, cascade_percentage: true}), new Decimal('1')],
      ]),
    })
  })
  test('Gets the total with a backed in, cascading percentage modifier', () => {
    // test_get_totals_percentage_backed_in_cascade
    const source = [
      genLineItem({amount: 10, priority: 0}),
      genLineItem({percentage: 10, priority: 1, cascade_percentage: true, back_into_percentage: true}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: new Decimal('10'),
      discount: new Decimal('0'),
      subtotals: new Map([
        [genLineItem({amount: 10, priority: 0}), new Decimal('9.09')],
        [
          genLineItem(
            {percentage: 10, priority: 1, cascade_percentage: true, back_into_percentage: true},
          ),
          new Decimal('.91')],
      ]),
    })
  })
  test('Gets totals with a line item that has both percentage and static modifiers', () => {
    // test_get_totals_percentage_with_static
    const source = [
      genLineItem({amount: 10, priority: 0}),
      genLineItem({amount: 0.25, percentage: 10, priority: 1}),
    ]
    const results = getTotals(source)
    expect(results).toEqual({
      total: new Decimal('11.25'),
      discount: new Decimal('0'),
      subtotals: new Map([
        [genLineItem({amount: 10, priority: 0}), new Decimal('10.00')],
        [genLineItem({percentage: 10, amount: 0.25, priority: 1}), new Decimal('1.25')],
      ]),
    })
  })
  test('Handles a cascading static+percentage modifier', () => {
    // test_get_totals_percentage_with_static_cascade
    const source = [
      genLineItem({amount: 10, priority: 0}),
      genLineItem({percentage: 10, amount: 0.25, priority: 1, cascade_percentage: true, cascade_amount: true}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: new Decimal('10'),
      discount: new Decimal('0'),
      subtotals: new Map([
        [genLineItem({amount: 10, priority: 0}), new Decimal('8.75')],
        [genLineItem({
          percentage: 10, amount: 0.25, priority: 1, cascade_percentage: true, cascade_amount: true,
        }), new Decimal('1.25')],
      ]),
    })
  })
  test('Handles cascading percentage along a stacked static amount', () => {
    // test_get_totals_percentage_no_cascade_amount
    const source = [
      genLineItem({amount: 10, priority: 0}),
      genLineItem({percentage: 10, amount: 0.25, priority: 1, cascade_amount: false, cascade_percentage: true}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: new Decimal('10.25'),
      discount: new Decimal('0'),
      subtotals: new Map([
        [genLineItem({amount: 10, priority: 0}), new Decimal('9')],
        [genLineItem({
          percentage: 10, amount: 0.25, priority: 1, cascade_amount: false, cascade_percentage: true,
        }), new Decimal('1.25')],
      ]),
    })
  })
  test('Handles lines with concurrent priorities', () => {
    // test_get_totals_concurrent_priorities
    const source = [
      genLineItem({amount: 10, priority: 0}),
      genLineItem({percentage: 10, priority: 1}),
      genLineItem({percentage: 5, priority: 1}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: new Decimal('11.50'),
      discount: new Decimal('0'),
      subtotals: new Map([
        [genLineItem({amount: 10, priority: 0}), new Decimal('10')],
        [genLineItem({percentage: 10, priority: 1}), new Decimal('1')],
        [genLineItem({percentage: 5, priority: 1}), new Decimal('0.5')],
      ]),
    })
  })
  test('Handles cascading concurrent priorities', () => {
    // test_get_totals_concurrent_priorities_cascade
    const source = [
      genLineItem({amount: 10, priority: 0}),
      genLineItem({percentage: 10, priority: 1, cascade_percentage: true, cascade_amount: true}),
      genLineItem({percentage: 5, priority: 1, cascade_percentage: true, cascade_amount: true}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: new Decimal('10'),
      discount: new Decimal('0'),
      subtotals: new Map([
        [genLineItem({amount: 10, priority: 0}), new Decimal('8.5')],
        [genLineItem({percentage: 10, priority: 1, cascade_percentage: true, cascade_amount: true}), new Decimal('1')],
        [genLineItem({percentage: 5, priority: 1, cascade_percentage: true, cascade_amount: true}), new Decimal('0.5')],
      ]),
    })
  })
  test('Handles multi-priority cascading', () => {
    // test_get_totals_multi_priority_cascade
    const source = [
      genLineItem({amount: 10, priority: 0}),
      genLineItem({percentage: 20, priority: 1, cascade_percentage: true}),
      genLineItem({percentage: 10, priority: 2, cascade_percentage: true}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: new Decimal('10'),
      discount: new Decimal('0'),
      subtotals: new Map([
        [genLineItem({amount: 10, priority: 0}), new Decimal('7.2')],
        [genLineItem({percentage: 20, priority: 1, cascade_percentage: true}), new Decimal('1.8')],
        [genLineItem({percentage: 10, priority: 2, cascade_percentage: true}), new Decimal('1')],
      ]),
    })
  })
  test('Handles multi-cascading on concurrent lower priority items', () => {
    // test_get_totals_multi_priority_cascade_on_concurrent_priority
    const source = [
      genLineItem({amount: 8, priority: 0}),
      genLineItem({amount: 2, priority: 0}),
      genLineItem({percentage: 20, priority: 1, cascade_percentage: true}),
      genLineItem({percentage: 10, priority: 2, cascade_percentage: true}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: new Decimal('10'),
      discount: new Decimal('0'),
      subtotals: new Map([
        [genLineItem({amount: 8, priority: 0}), new Decimal('5.76')],
        [genLineItem({amount: 2, priority: 0}), new Decimal('1.44')],
        [genLineItem({percentage: 20, priority: 1, cascade_percentage: true}), new Decimal('1.8')],
        [genLineItem({percentage: 10, priority: 2, cascade_percentage: true}), new Decimal('1.00')],
      ]),
    })
  })
  test('Reckons lines', () => {
    // test_reckon_lines
    const source = [
      genLineItem({amount: 1, priority: 0}),
      genLineItem({amount: 5, priority: 1}),
      genLineItem({amount: 4, priority: 2}),
    ]
    expect(reckonLines(source)).toEqual(new Decimal('10'))
  })
  test('Handles fixed-point calculations sanely', () => {
    // test_fixed_point_decisions
    const source = [
      genLineItem({amount: 100, priority: 0}),
      genLineItem({amount: 5.0, priority: 100}),
      genLineItem({amount: 5.0, percentage: 10.0, cascade_percentage: true, cascade_amount: false, priority: 300}),
      genLineItem({amount: 0, percentage: 8.25, cascade_percentage: true, cascade_amount: true, priority: 600}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: new Decimal('110.00'),
      discount: new Decimal('0'),
      subtotals: new Map([
        [genLineItem({amount: 100.0, priority: 0, percentage: 0.0}), new Decimal('82.57')],
        [genLineItem({amount: 5.0, priority: 100}), new Decimal('4.12')],
        [genLineItem({amount: 5.0, percentage: 10.0, cascade_percentage: true, cascade_amount: false, priority: 300}), new Decimal('14.23')],
        [genLineItem({amount: 0.0, percentage: 8.25, cascade_percentage: true, cascade_amount: true, priority: 600}), new Decimal('9.08')],
      ]),
    })
  })
  test('Handles fixed-point calculation scenario 2 sanely', () => {
    // test_fixed_point_calculations_2
    const source = [
      genLineItem({amount: 20, priority: 0, id: 1}),
      genLineItem({amount: 10, priority: 100, id: 2}),
      genLineItem({amount: 5.0, percentage: 10.0, cascade_percentage: true, cascade_amount: false, priority: 300, id: 3}),
      genLineItem({amount: 0, percentage: 8.25, cascade_percentage: true, cascade_amount: true, priority: 600, id: 4}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: new Decimal('35.00'),
      discount: new Decimal('0'),
      subtotals: new Map([
        [genLineItem({amount: 20, priority: 0, id: 1}), new Decimal('16.51')],
        [genLineItem({amount: 10, priority: 100, id: 2}), new Decimal('8.25')],
        [genLineItem({amount: 5.0, percentage: 10.0, cascade_percentage: true, cascade_amount: false, priority: 300, id: 3}), new Decimal('7.35')],
        [genLineItem({amount: 0.0, percentage: 8.25, cascade_percentage: true, cascade_amount: true, priority: 600, id: 4}), new Decimal('2.89')],
      ]),
    })
  })
  test('Handles fixed-point calculation scenario 3 sanely', () => {
    // test_fixed_point_calculations_3
    const source = [
      genLineItem({amount: 20, priority: 0}),
      genLineItem({amount: 5, priority: 100}),
      genLineItem({amount: 5.0, percentage: 10.0, cascade_percentage: true, cascade_amount: false, priority: 300}),
      genLineItem({amount: 0, percentage: 8.25, cascade_percentage: true, cascade_amount: true, priority: 600}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: new Decimal('30.00'),
      discount: new Decimal('0'),
      subtotals: new Map([
        [genLineItem({amount: 20, priority: 0}), new Decimal('16.51')],
        [genLineItem({amount: 5, priority: 100}), new Decimal('4.12')],
        [genLineItem({amount: 5.0, percentage: 10.0, cascade_percentage: true, cascade_amount: false, priority: 300}), new Decimal('6.89')],
        [genLineItem({amount: 0.0, percentage: 8.25, cascade_percentage: true, cascade_amount: true, priority: 600}), new Decimal('2.48')],
      ]),
    })
  })
  test('Handles a complex discount scenario', () => {
    // test_complex_discount
    const source = [
      genLineItem({amount: 0.01, priority: 0, id: 1}),
      genLineItem({amount: 0.01, priority: 100, id: 2}),
      genLineItem({amount: 0.01, priority: 100, id: 3}),
      genLineItem({amount: -5.00, priority: 100, id: 4}),
      genLineItem({amount: 10.00, priority: 100, id: 5}),
      genLineItem({
        amount: 0.75, percentage: 8.0, cascade_percentage: true, cascade_amount: true, priority: 300,
      }),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: new Decimal('5.03'),
      discount: new Decimal('-5'),
      subtotals: new Map([
        [genLineItem({amount: 0.01, priority: 0, id: 1}), new Decimal('0.00')],
        [genLineItem({amount: 0.01, priority: 100, id: 2}), new Decimal('0.00')],
        [genLineItem({amount: 0.01, priority: 100, id: 3}), new Decimal('0.01')],
        [genLineItem({amount: -5.00, priority: 100, id: 4}), new Decimal('-5.00')],
        [genLineItem({amount: 10.00, priority: 100, id: 5}), new Decimal('8.86')],
        [genLineItem({
          amount: 0.75,
          percentage: 8.0,
          cascade_percentage: true,
          cascade_amount: true,
          priority: 300,
        }), new Decimal('1.16')],
      ]),
    })
  })
  test('Handles a zero total', () => {
    // test_zero_total
    const source = [
      genLineItem({amount: 0, priority: 0}),
      genLineItem({amount: 8, cascade_percentage: true, cascade_amount: true, priority: 600}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: new Decimal('0'),
      discount: new Decimal('0'),
      subtotals: new Map([
        [genLineItem({amount: 0, priority: 0}), new Decimal('-8')],
        [genLineItem({amount: 8, cascade_percentage: true, cascade_amount: true, priority: 600}), new Decimal('8')],
      ]),
    })
  })
  test('Handles negative distribution', () => {
    // test_negative_distribution
    const source = [
      genLineItem({amount: 1, priority: 0, id: 1}),
      genLineItem({amount: 1, priority: 1, id: 2}),
      genLineItem({amount: 4, priority: 1, id: 3}),
      genLineItem({amount: 8, cascade_amount: true, priority: 100, id: 4}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: new Decimal('6'),
      discount: new Decimal('0'),
      subtotals: new Map([
        [genLineItem({amount: 1, priority: 0, id: 1}), new Decimal('-0.34')],
        [genLineItem({amount: 1, priority: 1, id: 2}), new Decimal('-0.33')],
        [genLineItem({amount: 4, priority: 1, id: 3}), new Decimal('-1.33')],
        [genLineItem({amount: 8, cascade_amount: true, priority: 100, id: 4}), new Decimal('8.00')],
      ]),
    })
  })
  test('Handles non-cascaded percentages', () => {
    // test_non_cascading_percentage
    const source = [
      genLineItem({amount: 5, priority: 0, id: 1}),
      genLineItem({amount: 1, priority: 1, id: 2}),
      genLineItem({amount: 4, priority: 1, id: 3}),
      genLineItem({percentage: 5, back_into_percentage: true, priority: 100, id: 4}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: new Decimal('10.52'),
      discount: new Decimal('0'),
      subtotals: new Map([
        [genLineItem({amount: 5, priority: 0, id: 1}), new Decimal('5')],
        [genLineItem({amount: 1, priority: 1, id: 2}), new Decimal('1')],
        [genLineItem({amount: 4, priority: 1, id: 3}), new Decimal('4')],
        [genLineItem({percentage: 5, back_into_percentage: true, priority: 100, id: 4}), new Decimal('.52')],
      ]),
    })
  })
  test('Handles many transactions divvied up for fees', () => {
    // test_handles_many_transactions_divvied_up_for_fees
    const source = [
      genLineItem({amount: 25.00, priority: 0, cascade_amount: false, id: 1}),
      genLineItem({amount: 25.00, priority: 0, cascade_amount: false, id: 2}),
      genLineItem({amount: 35.00, priority: 0, cascade_amount: false, id: 3}),
      genLineItem({amount: 55.00, priority: 0, cascade_amount: false, id: 4}),
      genLineItem({amount: 10.00, priority: 0, cascade_amount: false, id: 5}),
      genLineItem({amount: 5.00, priority: 0, cascade_amount: false, id: 6}),
      genLineItem({amount: 30.00, priority: 0, cascade_amount: false, id: 7}),
      genLineItem({amount: 55.00, priority: 0, cascade_amount: false, id: 8}),
      genLineItem({amount: 25.00, priority: 0, cascade_amount: false, id: 9}),
      genLineItem({amount: 5.00, priority: 0, cascade_amount: false, id: 10}),
      genLineItem({amount: 6.00, priority: 0, cascade_amount: false, id: 11}),
      genLineItem({amount: 25.00, priority: 0, cascade_amount: false, id: 12}),
      genLineItem({amount: 6.00, priority: 0, cascade_amount: false, id: 13}),
      genLineItem({amount: 3.00, priority: 0, cascade_amount: false, id: 14}),
      genLineItem({amount: 5.00, priority: 0, cascade_amount: false, id: 15}),
      genLineItem({amount: 10.06, priority: 1, cascade_amount: true, id: 16}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      subtotals: new Map([
        [genLineItem({
          amount: 25,
          back_into_percentage: false,
          cascade_amount: false,
          cascade_percentage: false,
          description: '',
          id: 1,
          percentage: 0,
          priority: 0,
          type: 0,
        }), new Decimal('24.2')],
        [genLineItem({
          amount: 25,
          back_into_percentage: false,
          cascade_amount: false,
          cascade_percentage: false,
          description: '',
          id: 2,
          percentage: 0,
          priority: 0,
          type: 0,
        }), new Decimal('24.2')],
        [genLineItem({
          amount: 35,
          back_into_percentage: false,
          cascade_amount: false,
          cascade_percentage: false,
          description: '',
          id: 3,
          percentage: 0,
          priority: 0,
          type: 0,
        }), new Decimal('33.89')],
        [genLineItem({
          amount: 55,
          back_into_percentage: false,
          cascade_amount: false,
          cascade_percentage: false,
          description: '',
          id: 4,
          percentage: 0,
          priority: 0,
          type: 0,
        }), new Decimal('53.25')],
        [genLineItem({
          amount: 10,
          back_into_percentage: false,
          cascade_amount: false,
          cascade_percentage: false,
          description: '',
          id: 5,
          percentage: 0,
          priority: 0,
          type: 0,
        }), new Decimal('9.68')],
        [genLineItem({
          amount: 5,
          back_into_percentage: false,
          cascade_amount: false,
          cascade_percentage: false,
          description: '',
          id: 6,
          percentage: 0,
          priority: 0,
          type: 0,
        }), new Decimal('4.84')],
        [genLineItem({
          amount: 30,
          back_into_percentage: false,
          cascade_amount: false,
          cascade_percentage: false,
          description: '',
          id: 7,
          percentage: 0,
          priority: 0,
          type: 0,
        }), new Decimal('29.04')],
        [genLineItem({
          amount: 55,
          back_into_percentage: false,
          cascade_amount: false,
          cascade_percentage: false,
          description: '',
          id: 8,
          percentage: 0,
          priority: 0,
          type: 0,
        }), new Decimal('53.25')],
        [genLineItem({
          amount: 25,
          back_into_percentage: false,
          cascade_amount: false,
          cascade_percentage: false,
          description: '',
          id: 9,
          percentage: 0,
          priority: 0,
          type: 0,
        }), new Decimal('24.2')],
        [genLineItem({
          amount: 5,
          back_into_percentage: false,
          cascade_amount: false,
          cascade_percentage: false,
          description: '',
          id: 10,
          percentage: 0,
          priority: 0,
          type: 0,
        }), new Decimal('4.84')],
        [genLineItem({
          amount: 6,
          back_into_percentage: false,
          cascade_amount: false,
          cascade_percentage: false,
          description: '',
          id: 11,
          percentage: 0,
          priority: 0,
          type: 0,
        }), new Decimal('5.80')],
        [genLineItem({
          amount: 25,
          back_into_percentage: false,
          cascade_amount: false,
          cascade_percentage: false,
          description: '',
          id: 12,
          percentage: 0,
          priority: 0,
          type: 0,
        }), new Decimal('24.2')],
        [genLineItem({
          amount: 6,
          back_into_percentage: false,
          cascade_amount: false,
          cascade_percentage: false,
          description: '',
          id: 13,
          percentage: 0,
          priority: 0,
          type: 0,
        }), new Decimal('5.80')],
        [genLineItem({
          amount: 3,
          back_into_percentage: false,
          cascade_amount: false,
          cascade_percentage: false,
          description: '',
          id: 14,
          percentage: 0,
          priority: 0,
          type: 0,
        }), new Decimal('2.90')],
        [genLineItem({
          amount: 5,
          back_into_percentage: false,
          cascade_amount: false,
          cascade_percentage: false,
          description: '',
          id: 15,
          percentage: 0,
          priority: 0,
          type: 0,
        }), new Decimal('4.84')],
        [genLineItem({
          amount: 10.06,
          back_into_percentage: false,
          cascade_amount: true,
          cascade_percentage: false,
          description: '',
          id: 16,
          percentage: 0,
          priority: 1,
          type: 0,
        }), new Decimal('10.07')],
      ]),
      total: new Decimal('315'),
      discount: new Decimal('0.00'),
    })
  })
  test('Generates preview line items for a null product', async() => {
    expect(invoiceLines({
      escrowEnabled: true,
      pricing: genPricing(),
      value: '25.00',
      product: null,
      cascade: true,
      international: false,
      planName: 'Basic',
    })).toEqual([
      {
        id: -1,
        priority: 0,
        type: 0,
        amount: 25,
        frozen_value: null,
        percentage: 0,
        description: '',
        cascade_amount: false,
        cascade_percentage: false,
        back_into_percentage: false,
      },
      {
        id: -5,
        priority: 300,
        type: 2,
        cascade_percentage: true,
        cascade_amount: true,
        back_into_percentage: false,
        amount: 3.5,
        frozen_value: null,
        percentage: 5,
        description: '',
      },
    ])
  })
  test('Generates preview line items for a product', async() => {
    expect(invoiceLines({
      escrowEnabled: true,
      pricing: genPricing(),
      value: '25.00',
      product: genProduct(),
      cascade: true,
      international: false,
      planName: 'Basic',
    })).toEqual([
      {
        id: -1,
        priority: 0,
        type: 0,
        amount: 10,
        frozen_value: null,
        percentage: 0,
        description: '',
        cascade_amount: false,
        cascade_percentage: false,
        back_into_percentage: false,
      },
      {
        id: -5,
        priority: 300,
        type: 2,
        cascade_percentage: true,
        cascade_amount: true,
        back_into_percentage: false,
        amount: 3.5,
        frozen_value: null,
        percentage: 5,
        description: '',
      },
      {
        id: -2,
        priority: 100,
        type: 1,
        amount: 15,
        frozen_value: null,
        percentage: 0,
        description: '',
        cascade_amount: false,
        cascade_percentage: false,
        back_into_percentage: false,
      },
    ])
  })
  test('Generates preview line items for an international product', async() => {
    expect(invoiceLines({
      escrowEnabled: true,
      pricing: genPricing(),
      value: '25.00',
      product: genProduct(),
      cascade: true,
      international: true,
      planName: 'Basic',
    })).toEqual([
      {
        id: -1,
        priority: 0,
        type: 0,
        amount: 10,
        frozen_value: null,
        percentage: 0,
        description: '',
        cascade_amount: false,
        cascade_percentage: false,
        back_into_percentage: false,
      },
      {
        id: -5,
        priority: 300,
        type: 2,
        cascade_percentage: true,
        cascade_amount: true,
        back_into_percentage: false,
        amount: 3.5,
        frozen_value: null,
        percentage: 6,
        description: '',
      },
      {
        id: -2,
        priority: 100,
        type: 1,
        amount: 15,
        frozen_value: null,
        percentage: 0,
        description: '',
        cascade_amount: false,
        cascade_percentage: false,
        back_into_percentage: false,
      },
    ])
  })
  test('Generates preview for a table product', async() => {
    expect(invoiceLines({
      escrowEnabled: true,
      pricing: genPricing(),
      value: '25.00',
      product: genProduct({table_product: true}),
      cascade: true,
      international: false,
      planName: 'Basic',
    })).toEqual([
      {
        id: -1,
        priority: 0,
        type: 0,
        amount: 10,
        frozen_value: null,
        percentage: 0,
        description: '',
        cascade_amount: false,
        cascade_percentage: false,
        back_into_percentage: false,
      },
      {
        id: -3,
        priority: 400,
        type: 5,
        cascade_percentage: true,
        cascade_amount: false,
        back_into_percentage: false,
        amount: 5,
        frozen_value: null,
        percentage: 10,
        description: '',
      },
      {
        id: -4,
        priority: 700,
        type: 6,
        cascade_percentage: true,
        cascade_amount: true,
        back_into_percentage: true,
        percentage: 8.25,
        description: '',
        amount: 0,
        frozen_value: null,
      },
      {
        id: -2,
        priority: 100,
        type: 1,
        amount: 15,
        frozen_value: null,
        percentage: 0,
        description: '',
        cascade_amount: false,
        cascade_percentage: false,
        back_into_percentage: false,
      },
    ])
  })
  test('Generates preview line items for a null product with no escrow', async() => {
    expect(invoiceLines({
      escrowEnabled: false,
      pricing: genPricing(),
      value: '25.00',
      product: null,
      cascade: true,
      international: false,
      planName: 'Basic',
    })).toEqual([
      {
        id: -1,
        priority: 0,
        type: 0,
        amount: 25,
        frozen_value: null,
        percentage: 0,
        description: '',
        cascade_amount: false,
        cascade_percentage: false,
        back_into_percentage: false,
      },
      {
        amount: 1.35,
        back_into_percentage: false,
        cascade_amount: true,
        cascade_percentage: true,
        description: '',
        frozen_value: null,
        id: -6,
        percentage: 0,
        priority: 300,
        type: 10,
      },
    ])
  })
  test('Generates preview line items for a product with no escrow', async() => {
    expect(invoiceLines({
      escrowEnabled: false,
      pricing: genPricing(),
      value: '25.00',
      product: genProduct(),
      cascade: true,
      international: false,
      planName: 'Basic',
    })).toEqual([
      {
        id: -1,
        priority: 0,
        type: 0,
        amount: 10,
        frozen_value: null,
        percentage: 0,
        description: '',
        cascade_amount: false,
        cascade_percentage: false,
        back_into_percentage: false,
      },
      {
        amount: 1.35,
        back_into_percentage: false,
        cascade_amount: true,
        cascade_percentage: true,
        description: '',
        frozen_value: null,
        id: -6,
        percentage: 0,
        priority: 300,
        type: 10,
      },
      {
        id: -2,
        priority: 100,
        type: 1,
        amount: 15,
        frozen_value: null,
        percentage: 0,
        description: '',
        cascade_amount: false,
        cascade_percentage: false,
        back_into_percentage: false,
      },
    ])
  })
  test('Handles line items for a product with no escrow and a nonsense value', async() => {
    expect(invoiceLines({
      escrowEnabled: false,
      pricing: genPricing(),
      value: 'boop',
      product: genProduct(),
      cascade: true,
      international: false,
      planName: 'Basic',
    })).toEqual([
      {
        id: -1,
        priority: 0,
        type: 0,
        amount: 10,
        frozen_value: null,
        percentage: 0,
        description: '',
        cascade_amount: false,
        cascade_percentage: false,
        back_into_percentage: false,
      },
      {
        amount: 1.35,
        back_into_percentage: false,
        cascade_amount: true,
        cascade_percentage: true,
        description: '',
        frozen_value: null,
        id: -6,
        percentage: 0,
        priority: 300,
        type: 10,
      },
    ])
  })
  test('Handles line item for no product, no escrow and a nonsense value', async() => {
    expect(invoiceLines({
      escrowEnabled: false,
      pricing: genPricing(),
      value: 'boop',
      product: null,
      cascade: true,
      international: false,
      planName: 'Basic',
    })).toEqual([])
  })
  test('Bails if the pricing is not available', async() => {
    expect(invoiceLines({
      escrowEnabled: false,
      pricing: null,
      value: 'boop',
      product: genProduct(),
      cascade: true,
      international: false,
      planName: 'Basic',
    })).toEqual([])
  })
  test('Bails if the plan is unknown', async() => {
    expect(invoiceLines({
      escrowEnabled: false,
      pricing: genPricing(),
      value: 'boop',
      product: genProduct(),
      cascade: true,
      international: false,
      planName: 'Backup',
    })).toEqual([])
  })
})
