import { LineType } from "@/types/enums/LineType.ts"
import type { LineItem, Pricing } from "@/types/main"

export function genLineItem(overrides: Partial<LineItem>): LineItem {
  return {
    id: -1,
    type: 0,
    amount: "0.00",
    frozen_value: null,
    percentage: "0",
    priority: 0,
    cascade_percentage: false,
    cascade_amount: false,
    back_into_percentage: false,
    description: "",
    ...overrides,
  }
}

export function dummyLineItems(): LineItem[] {
  return [
    {
      id: 21,
      priority: 300,
      percentage: "4",
      amount: "0.50",
      frozen_value: null,
      type: LineType.SHIELD,
      destination_account: 304,
      destination_user: null,
      description: "",
      cascade_percentage: true,
      cascade_amount: true,
      back_into_percentage: false,
    },
    {
      id: 22,
      priority: 300,
      percentage: "4",
      amount: "0.25",
      frozen_value: null,
      type: LineType.BONUS,
      destination_account: 304,
      destination_user: null,
      description: "",
      cascade_percentage: true,
      cascade_amount: true,
      back_into_percentage: false,
    },
    {
      id: 20,
      priority: 0,
      percentage: "0",
      amount: "100.00",
      frozen_value: null,
      type: LineType.BASE_PRICE,
      destination_account: 302,
      destination_user: 1,
      description: "",
      cascade_percentage: false,
      cascade_amount: false,
      back_into_percentage: false,
    },
    {
      id: 23,
      priority: 100,
      percentage: "0",
      amount: "-20.00",
      frozen_value: null,
      type: LineType.ADD_ON,
      destination_account: 302,
      destination_user: 1,
      description: "Discount",
      cascade_percentage: false,
      cascade_amount: false,
      back_into_percentage: false,
    },
  ]
}

export function genPricing(): Pricing {
  return {
    plans: [
      {
        id: 7,
        name: "Free",
        description:
          "\n            For those just starting out.\n            Stay organized-- all of your commission information is kept in one place for easy access. For free.\n            ",
        features: [
          "Slick, mobile-friendly storefront",
          "Built-in order forms",
          "Order management tools",
          "Commissioner communication tools",
          "Optional public queue",
          "Gallery",
          "Character Management",
          "PostyBirb Integration",
          "Community Discord",
          "Shielded orders can be purchased at commissioner's option",
        ],
        monthly_charge: "0.00",
        per_deliverable_price: "0",
        max_simultaneous_orders: 1,
        waitlisting: false,
        shield_static_price: "3.50",
        shield_percentage_price: "5.5",
        paypal_invoicing: false,
      },
      {
        id: 8,
        name: "Basic",
        description:
          "\n            Good for artists getting consistent orders, but don't need the full features of Landscape. Pay per order\n            tracked, with no monthly subscription fee.\n            ",
        features: [
          "Slick, mobile-friendly storefront",
          "Built-in order forms",
          "Order management tools",
          "Commissioner communication tools",
          "Optional public queue",
          "Gallery",
          "Character Management",
          "PostyBirb Integration",
          "Community Discord",
          "Shielded orders can be purchased at commissioner's option",
          "Discount on shield percentage",
          "No order limit-- pay as you go!",
        ],
        monthly_charge: "0.00",
        per_deliverable_price: "1.35",
        max_simultaneous_orders: 0,
        waitlisting: false,
        shield_static_price: "3.50",
        shield_percentage_price: "5",
        paypal_invoicing: false,
      },
      {
        id: 9,
        name: "Landscape",
        description:
          "\n            Best for those living off of, or making significant income from, their work. Significant reduction in fees\n            and extra features to help you get the most out of Artconomy.\n            ",
        features: [
          "Slick, mobile-friendly storefront",
          "Built-in order forms",
          "Order management tools",
          "Commissioner communication tools",
          "Optional public queue",
          "Gallery",
          "Character Management",
          "PostyBirb Integration",
          "Special Discord Role",
          "Ability to make all orders shielded by default at a discounted rate",
          "No order limit-- pay as you go!",
          "First consideration for Virtual Table Events -- sell commissions and merch at cons without being physically present!",
          "Tip Jar",
          "Wait list",
          "First Access to New Features",
        ],
        monthly_charge: "8.00",
        per_deliverable_price: "0.75",
        max_simultaneous_orders: 0,
        waitlisting: true,
        shield_static_price: "0.75",
        shield_percentage_price: "4",
        paypal_invoicing: true,
      },
    ],
    minimum_price: "1.00",
    table_percentage: "10",
    table_static: "5.00",
    table_tax: "8.25",
    international_conversion_percentage: "1",
    preferred_plan: "Landscape",
  }
}
