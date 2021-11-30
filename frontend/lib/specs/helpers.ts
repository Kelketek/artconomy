import LineItem from '@/types/LineItem'
import {LineTypes} from '@/types/LineTypes'

export function genLineItem(overrides: Partial<LineItem>): LineItem {
  return {
    id: -1,
    type: 0,
    amount: 0.0,
    percentage: 0.0,
    priority: 0,
    cascade_percentage: false,
    cascade_amount: false,
    back_into_percentage: false,
    description: '',
    ...overrides,
  }
}

export function dummyLineItems(): LineItem[] {
  return [
    {
      id: 21,
      priority: 300,
      percentage: 4,
      amount: 0.5,
      type: LineTypes.SHIELD,
      destination_account: 304,
      destination_user: null,
      description: '',
      cascade_percentage: true,
      cascade_amount: true,
      back_into_percentage: false,
    },
    {
      id: 22,
      priority: 300,
      percentage: 4,
      amount: 0.25,
      type: LineTypes.BONUS,
      destination_account: 304,
      destination_user: null,
      description: '',
      cascade_percentage: true,
      cascade_amount: true,
      back_into_percentage: false,
    },
    {
      id: 20,
      priority: 0,
      percentage: 0,
      amount: 100,
      type: LineTypes.BASE_PRICE,
      destination_account: 302,
      destination_user: 1,
      description: '',
      cascade_percentage: false,
      cascade_amount: false,
      back_into_percentage: false,
    },
    {
      id: 23,
      priority: 100,
      percentage: 0,
      amount: -20,
      type: LineTypes.ADD_ON,
      destination_account: 302,
      destination_user: 1,
      description: 'Discount',
      cascade_percentage: false,
      cascade_amount: false,
      back_into_percentage: false,
    },
  ]
}

export function genPricing() {
  return {
    premium_percentage_bonus: 4.0,
    premium_static_bonus: 0.25,
    landscape_price: 5.0,
    standard_percentage: 4.0,
    standard_static: 0.5,
    minimum_price: 1.0,
    table_percentage: 10.0,
    table_static: 5.0,
    table_tax: 8.25,
  }
}
