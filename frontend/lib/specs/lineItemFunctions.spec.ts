import {genLineItem, genPricing} from '@/lib/specs/helpers'
import {getTotals, invoiceLines, linesByPriority, reckonLines, sum} from '@/lib/lineItemFunctions'
import Big from 'big.js'
import {genProduct} from '@/specs/helpers/fixtures'

describe('lineItemFunctions.ts', () => {
  it('Sorts by priority', () => {
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
  it('Gets the total for a single line', () => {
    const source = [genLineItem({amount: 10, priority: 0})]
    const result = getTotals(source)
    expect(result).toEqual(
      {
        total: Big('10'),
        discount: Big('0'),
        map: new Map([
          [genLineItem({amount: 10, priority: 0}), Big('10')],
        ]),
      })
  })
  it('Gets the totals for a percentage modifier', () => {
    const source = [
      genLineItem({amount: 10, priority: 0}),
      genLineItem({percentage: 10, priority: 1}),
    ]
    const result = getTotals(source)
    expect(result).toEqual(
      {
        total: Big('11'),
        discount: Big('0'),
        map: new Map([
          [genLineItem({amount: 10, priority: 0}), Big('10')],
          [genLineItem({percentage: 10, priority: 1}), Big('1')],
        ]),
      },
    )
  })
  it('Gets the total with a cascading percentage modifier', () => {
    const source = [
      genLineItem({amount: 10, priority: 0}),
      genLineItem({percentage: 10, priority: 1, cascade_percentage: true}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: Big('10'),
      discount: Big('0'),
      map: new Map([
        [genLineItem({amount: 10, priority: 0}), Big('9')],
        [genLineItem({percentage: 10, priority: 1, cascade_percentage: true}), Big('1')],
      ]),
    })
  })
  it('Gets the total with a backed in, cascading percentage modifier', () => {
    const source = [
      genLineItem({amount: 10, priority: 0}),
      genLineItem({percentage: 10, priority: 1, cascade_percentage: true, back_into_percentage: true}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: Big('10'),
      discount: Big('0'),
      map: new Map([
        [genLineItem({amount: 10, priority: 0}), Big('9.09')],
        [
          genLineItem(
            {percentage: 10, priority: 1, cascade_percentage: true, back_into_percentage: true},
          ),
          Big('.91')],
      ]),
    })
  })
  it('Gets totals with a line item that has both percentage and static modifiers', () => {
    const source = [
      genLineItem({amount: 10, priority: 0}),
      genLineItem({amount: 0.25, percentage: 10, priority: 1}),
    ]
    const results = getTotals(source)
    expect(results).toEqual({
      total: Big('11.25'),
      discount: Big('0'),
      map: new Map([
        [genLineItem({amount: 10, priority: 0}), Big('10.00')],
        [genLineItem({percentage: 10, amount: 0.25, priority: 1}), Big('1.25')],
      ]),
    })
  })
  it('Handles a cascading static+percentage modifier', () => {
    const source = [
      genLineItem({amount: 10, priority: 0}),
      genLineItem({percentage: 10, amount: 0.25, priority: 1, cascade_percentage: true, cascade_amount: true}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: Big('10'),
      discount: Big('0'),
      map: new Map([
        [genLineItem({amount: 10, priority: 0}), Big('8.75')],
        [genLineItem({
          percentage: 10, amount: 0.25, priority: 1, cascade_percentage: true, cascade_amount: true,
        }), Big('1.25')],
      ]),
    })
  })
  it('Handles cascading percentage along a stacked static amount', () => {
    const source = [
      genLineItem({amount: 10, priority: 0}),
      genLineItem({percentage: 10, amount: 0.25, priority: 1, cascade_amount: false, cascade_percentage: true}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: Big('10.25'),
      discount: Big('0'),
      map: new Map([
        [genLineItem({amount: 10, priority: 0}), Big('9')],
        [genLineItem({
          percentage: 10, amount: 0.25, priority: 1, cascade_amount: false, cascade_percentage: true,
        }), Big('1.25')],
      ]),
    })
  })
  it('Handles lines with concurrent priorities', () => {
    const source = [
      genLineItem({amount: 10, priority: 0}),
      genLineItem({percentage: 10, priority: 1}),
      genLineItem({percentage: 5, priority: 1}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: Big('11.50'),
      discount: Big('0'),
      map: new Map([
        [genLineItem({amount: 10, priority: 0}), Big('10')],
        [genLineItem({percentage: 10, priority: 1}), Big('1')],
        [genLineItem({percentage: 5, priority: 1}), Big('0.5')],
      ]),
    })
  })
  it('Handles cascading concurrent priorities', () => {
    const source = [
      genLineItem({amount: 10, priority: 0}),
      genLineItem({percentage: 10, priority: 1, cascade_percentage: true, cascade_amount: true}),
      genLineItem({percentage: 5, priority: 1, cascade_percentage: true, cascade_amount: true}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: Big('10'),
      discount: Big('0'),
      map: new Map([
        [genLineItem({amount: 10, priority: 0}), Big('8.5')],
        [genLineItem({percentage: 10, priority: 1, cascade_percentage: true, cascade_amount: true}), Big('1')],
        [genLineItem({percentage: 5, priority: 1, cascade_percentage: true, cascade_amount: true}), Big('0.5')],
      ]),
    })
  })
  it('Handles multi-priority cascading', () => {
    const source = [
      genLineItem({amount: 10, priority: 0}),
      genLineItem({percentage: 20, priority: 1, cascade_percentage: true}),
      genLineItem({percentage: 10, priority: 2, cascade_percentage: true}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: Big('10'),
      discount: Big('0'),
      map: new Map([
        [genLineItem({amount: 10, priority: 0}), Big('7.2')],
        [genLineItem({percentage: 20, priority: 1, cascade_percentage: true}), Big('1.8')],
        [genLineItem({percentage: 10, priority: 2, cascade_percentage: true}), Big('1')],
      ]),
    })
  })
  it('Handles multi-cascading on concurrent lower priority items', () => {
    const source = [
      genLineItem({amount: 8, priority: 0}),
      genLineItem({amount: 2, priority: 0}),
      genLineItem({percentage: 20, priority: 1, cascade_percentage: true}),
      genLineItem({percentage: 10, priority: 2, cascade_percentage: true}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: Big('10'),
      discount: Big('0'),
      map: new Map([
        [genLineItem({amount: 8, priority: 0}), Big('5.76')],
        [genLineItem({amount: 2, priority: 0}), Big('1.44')],
        [genLineItem({percentage: 20, priority: 1, cascade_percentage: true}), Big('1.8')],
        [genLineItem({percentage: 10, priority: 2, cascade_percentage: true}), Big('1.00')],
      ]),
    })
  })
  it('Reckons lines', () => {
    const source = [
      genLineItem({amount: 1, priority: 0}),
      genLineItem({amount: 5, priority: 1}),
      genLineItem({amount: 4, priority: 2}),
    ]
    expect(reckonLines(source)).toEqual(Big('10'))
  })
  it('Handles fixed-point calculations sanely', () => {
    const source = [
      genLineItem({amount: 100, priority: 0}),
      genLineItem({amount: 5.0, priority: 100}),
      genLineItem({amount: 5.0, percentage: 10.0, cascade_percentage: true, cascade_amount: false, priority: 300}),
      genLineItem({amount: 0, percentage: 8.25, cascade_percentage: true, cascade_amount: true, priority: 600}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: Big('110.00'),
      discount: Big('0'),
      map: new Map([
        [genLineItem({amount: 100.0, priority: 0, percentage: 0.0}), Big('82.58')],
        [genLineItem({amount: 5.0, priority: 100}), Big('4.13')],
        [genLineItem({amount: 5.0, percentage: 10.0, cascade_percentage: true, cascade_amount: false, priority: 300}), Big('14.22')],
        [genLineItem({amount: 0.0, percentage: 8.25, cascade_percentage: true, cascade_amount: true, priority: 600}), Big('9.07')],
      ]),
    })
  })
  it('Handles fixed-point calculation scenario 2 sanely', () => {
    const source = [
      genLineItem({amount: 20, priority: 0}),
      genLineItem({amount: 10, priority: 100}),
      genLineItem({amount: 5.0, percentage: 10.0, cascade_percentage: true, cascade_amount: false, priority: 300}),
      genLineItem({amount: 0, percentage: 8.25, cascade_percentage: true, cascade_amount: true, priority: 600}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: Big('35.00'),
      discount: Big('0'),
      map: new Map([
        [genLineItem({amount: 20, priority: 0}), Big('16.51')],
        [genLineItem({amount: 10, priority: 100}), Big('8.26')],
        [genLineItem({amount: 5.0, percentage: 10.0, cascade_percentage: true, cascade_amount: false, priority: 300}), Big('7.34')],
        [genLineItem({amount: 0.0, percentage: 8.25, cascade_percentage: true, cascade_amount: true, priority: 600}), Big('2.89')],
      ]),
    })
  })
  it('Handles fixed-point calculation scenario 3 sanely', () => {
    const source = [
      genLineItem({amount: 20, priority: 0}),
      genLineItem({amount: 5, priority: 100}),
      genLineItem({amount: 5.0, percentage: 10.0, cascade_percentage: true, cascade_amount: false, priority: 300}),
      genLineItem({amount: 0, percentage: 8.25, cascade_percentage: true, cascade_amount: true, priority: 600}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: Big('30.00'),
      discount: Big('0'),
      map: new Map([
        [genLineItem({amount: 20, priority: 0}), Big('16.52')],
        [genLineItem({amount: 5, priority: 100}), Big('4.13')],
        [genLineItem({amount: 5.0, percentage: 10.0, cascade_percentage: true, cascade_amount: false, priority: 300}), Big('6.88')],
        [genLineItem({amount: 0.0, percentage: 8.25, cascade_percentage: true, cascade_amount: true, priority: 600}), Big('2.47')],
      ]),
    })
  })
  it('Handles a complex discount scenario', () => {
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
      total: Big('5.03'),
      discount: Big('-5'),
      map: new Map([
        [genLineItem({amount: 0.01, priority: 0, id: 1}), Big('0.01')],
        [genLineItem({amount: 0.01, priority: 100, id: 2}), Big('0.01')],
        [genLineItem({amount: 0.01, priority: 100, id: 3}), Big('0.01')],
        [genLineItem({amount: -5.00, priority: 100, id: 4}), Big('-5.00')],
        [genLineItem({amount: 10.00, priority: 100, id: 5}), Big('8.85')],
        [genLineItem({
          amount: 0.75,
          percentage: 8.0,
          cascade_percentage: true,
          cascade_amount: true,
          priority: 300,
        }), Big('1.15')],
      ]),
    })
  })
  it('Handles a zero total', () => {
    const source = [
      genLineItem({amount: 0, priority: 0}),
      genLineItem({amount: 8, cascade_percentage: true, cascade_amount: true, priority: 600}),
    ]
    const result = getTotals(source)
    expect(result).toEqual({
      total: Big('0'),
      discount: Big('0'),
      map: new Map([
        [genLineItem({amount: 0, priority: 0}), Big('0')],
        [genLineItem({amount: 8, cascade_percentage: true, cascade_amount: true, priority: 600}), Big('8')],
      ]),
    })
  })
  it('Handles many transactions divvied up for fees', () => {
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
      map: new Map([
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
        }), Big('24.2')],
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
        }), Big('24.2')],
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
        }), Big('33.88')],
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
        }), Big('53.24')],
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
        }), Big('9.68')],
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
        }), Big('4.84')],
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
        }), Big('29.04')],
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
        }), Big('53.25')],
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
        }), Big('24.2')],
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
        }), Big('4.84')],
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
        }), Big('5.81')],
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
        }), Big('24.2')],
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
        }), Big('5.81')],
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
        }), Big('2.91')],
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
        }), Big('4.84')],
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
        }), Big('10.06')],
      ]),
      total: Big('315'),
      discount: Big('0.00'),
    })
  })
  it('Generates preview line items for a null product', async() => {
    expect(invoiceLines({escrowDisabled: false, pricing: genPricing(), value: '25.00', product: null})).toEqual([
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
        back_into_percentage: true,
      },
      {
        id: -5,
        priority: 300,
        type: 2,
        cascade_percentage: true,
        cascade_amount: true,
        back_into_percentage: false,
        amount: 0.5,
        frozen_value: null,
        percentage: 4,
        description: '',
      },
      {
        id: -6,
        priority: 300,
        type: 3,
        cascade_percentage: true,
        cascade_amount: true,
        back_into_percentage: false,
        amount: 0.25,
        frozen_value: null,
        percentage: 4,
        description: '',
      },
    ])
  })
  it('Generates preview line items for a product', async() => {
    expect(invoiceLines({escrowDisabled: false, pricing: genPricing(), value: '25.00', product: genProduct()})).toEqual([
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
      {
        id: -5,
        priority: 300,
        type: 2,
        cascade_percentage: true,
        cascade_amount: true,
        back_into_percentage: false,
        amount: 0.5,
        frozen_value: null,
        percentage: 4,
        description: '',
      },
      {
        id: -6,
        priority: 300,
        type: 3,
        cascade_percentage: true,
        cascade_amount: true,
        back_into_percentage: false,
        amount: 0.25,
        frozen_value: null,
        percentage: 4,
        description: '',
      },
    ])
  })
  it('Generates preview for a table product', async() => {
    expect(invoiceLines({
      escrowDisabled: false,
      pricing: genPricing(),
      value: '25.00',
      product: genProduct({table_product: true}),
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
    ])
  })
  it('Generates preview line items for a null product with no escrow', async() => {
    expect(invoiceLines({escrowDisabled: true, pricing: genPricing(), value: '25.00', product: null})).toEqual([
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
        back_into_percentage: true,
      },
    ])
  })
  it('Generates preview line items for a product with no escrow', async() => {
    expect(invoiceLines({escrowDisabled: true, pricing: genPricing(), value: '25.00', product: genProduct()})).toEqual([
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
  it('Handles line items for a product with no escrow and a nonsense value', async() => {
    expect(invoiceLines({escrowDisabled: true, pricing: genPricing(), value: 'boop', product: genProduct()})).toEqual([
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
    ])
  })
  it('Handles line item for no product, no escrow and a nonsense value', async() => {
    expect(invoiceLines({escrowDisabled: true, pricing: genPricing(), value: 'boop', product: null})).toEqual([])
  })
})
