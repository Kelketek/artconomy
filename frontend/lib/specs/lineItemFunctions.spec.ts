import {genLineItem} from '@/lib/specs/helpers'
import {getTotals, linesByPriority, reckonLines, sum} from '@/lib/lineItemFunctions'
import Big from 'big.js'

describe('lineItemFunctions.ts', () => {
  beforeEach(() => {
    Big.DP = 2
    Big.RM = 2
  })
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
    expect(result).toEqual({total: Big('10'), map: new Map([[genLineItem({amount: 10, priority: 0}), Big('10')]])})
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
      map: new Map([
        [genLineItem({amount: 10, priority: 0}), Big('9')],
        [genLineItem({percentage: 10, priority: 1, cascade_percentage: true}), Big('1')],
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
    let source = [
      genLineItem({amount: 100, priority: 0}),
      genLineItem({amount: 5.0, priority: 100}),
      genLineItem({amount: 5.0, percentage: 10.0, cascade_percentage: true, cascade_amount: false, priority: 300}),
      genLineItem({amount: 0, percentage: 8.25, cascade_percentage: true, cascade_amount: true, priority: 600}),
    ]
    let result = getTotals(source)
    expect(result).toEqual({
      total: Big('110.00'),
      map: new Map([
        [genLineItem({amount: 100.0, priority: 0, percentage: 0.0}), Big('82.58')],
        [genLineItem({amount: 5.0, priority: 100}), Big('4.11')],
        [genLineItem({amount: 5.0, percentage: 10.0, cascade_percentage: true, cascade_amount: false, priority: 300}), Big('14.23')],
        [genLineItem({amount: 0.0, percentage: 8.25, cascade_percentage: true, cascade_amount: true, priority: 600}), Big('9.08')],
      ]),
    })
  })
  it('Handles a zero total', () => {
    let source = [
      genLineItem({amount: 0, priority: 0}),
      genLineItem({amount: 8, cascade_percentage: true, cascade_amount: true, priority: 600}),
    ]
    let result = getTotals(source)
    expect(result).toEqual({
      total: Big('0'),
      map: new Map([
        [genLineItem({amount: 0, priority: 0}), Big('0')],
        [genLineItem({amount: 8, cascade_percentage: true, cascade_amount: true, priority: 600}), Big('8')],
      ]),
    })
  })
})
