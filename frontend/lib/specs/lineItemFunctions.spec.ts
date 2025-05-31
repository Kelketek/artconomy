import { genPricing } from "@/lib/specs/helpers.ts"
import { invoiceLines } from "@/lib/lineItemFunctions.ts"
import { genProduct } from "@/specs/helpers/fixtures.ts"
import { describe, expect, test } from "vitest"
import { LineCategory } from "@/types/enums/LineCategory.ts"

describe("lineItemFunctions.ts", () => {
  test("Generates preview line items for a null product", async () => {
    expect(
      invoiceLines({
        escrowEnabled: true,
        pricing: genPricing(),
        value: "25.00",
        product: null,
        cascade: true,
        international: false,
        planName: "Basic",
      }),
    ).toEqual([
      {
        id: -1,
        priority: 0,
        type: 0,
        amount: "25.00",
        category: LineCategory.ESCROW_HOLD,
        frozen_value: null,
        percentage: "0",
        description: "",
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
        amount: "3.50",
        category: LineCategory.SHIELD_FEE,
        frozen_value: null,
        percentage: "5",
        description: "",
      },
    ])
  })
  test("Generates preview line items for a product", async () => {
    expect(
      invoiceLines({
        escrowEnabled: true,
        pricing: genPricing(),
        value: "25.00",
        product: genProduct(),
        cascade: true,
        international: false,
        planName: "Basic",
      }),
    ).toEqual([
      {
        id: -1,
        priority: 0,
        type: 0,
        amount: "10.00",
        frozen_value: null,
        percentage: "0",
        description: "",
        category: LineCategory.ESCROW_HOLD,
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
        category: LineCategory.SHIELD_FEE,
        amount: "3.50",
        frozen_value: null,
        percentage: "5",
        description: "",
      },
      {
        id: -2,
        priority: 100,
        type: 1,
        amount: "15.00",
        frozen_value: null,
        category: LineCategory.ESCROW_HOLD,
        percentage: "0",
        description: "",
        cascade_amount: false,
        cascade_percentage: false,
        back_into_percentage: false,
      },
    ])
  })
  test("Generates preview line items for an international product", async () => {
    expect(
      invoiceLines({
        escrowEnabled: true,
        pricing: genPricing(),
        value: "25.00",
        product: genProduct(),
        cascade: true,
        international: true,
        planName: "Basic",
      }),
    ).toEqual([
      {
        id: -1,
        priority: 0,
        type: 0,
        amount: "10.00",
        frozen_value: null,
        percentage: "0",
        description: "",
        category: LineCategory.ESCROW_HOLD,
        cascade_amount: false,
        cascade_percentage: false,
        back_into_percentage: false,
      },
      {
        id: -5,
        priority: 300,
        type: 2,
        category: LineCategory.SHIELD_FEE,
        cascade_percentage: true,
        cascade_amount: true,
        back_into_percentage: false,
        amount: "3.50",
        frozen_value: null,
        percentage: "6",
        description: "",
      },
      {
        id: -2,
        priority: 100,
        type: 1,
        amount: "15.00",
        category: LineCategory.ESCROW_HOLD,
        frozen_value: null,
        percentage: "0",
        description: "",
        cascade_amount: false,
        cascade_percentage: false,
        back_into_percentage: false,
      },
    ])
  })
  test("Generates preview for a table product", async () => {
    expect(
      invoiceLines({
        escrowEnabled: true,
        pricing: genPricing(),
        value: "25.00",
        product: genProduct({ table_product: true }),
        cascade: true,
        international: false,
        planName: "Basic",
      }),
    ).toEqual([
      {
        id: -1,
        priority: 0,
        type: 0,
        category: LineCategory.ESCROW_HOLD,
        amount: "10.00",
        frozen_value: null,
        percentage: "0",
        description: "",
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
        amount: "5.00",
        category: LineCategory.TABLE_HANDLING,
        frozen_value: null,
        percentage: "10",
        description: "",
      },
      {
        id: -4,
        priority: 700,
        type: 6,
        cascade_percentage: true,
        cascade_amount: true,
        back_into_percentage: true,
        category: LineCategory.TAXES,
        percentage: "8.25",
        description: "",
        amount: "0",
        frozen_value: null,
      },
      {
        id: -2,
        priority: 100,
        type: 1,
        amount: "15.00",
        frozen_value: null,
        percentage: "0",
        description: "",
        category: LineCategory.ESCROW_HOLD,
        cascade_amount: false,
        cascade_percentage: false,
        back_into_percentage: false,
      },
    ])
  })
  test("Generates preview line items for a null product with no escrow", async () => {
    expect(
      invoiceLines({
        escrowEnabled: false,
        pricing: genPricing(),
        value: "25.00",
        product: null,
        cascade: true,
        international: false,
        planName: "Basic",
      }),
    ).toEqual([
      {
        id: -1,
        priority: 0,
        type: 0,
        amount: "25.00",
        frozen_value: null,
        percentage: "0",
        description: "",
        category: LineCategory.ESCROW_HOLD,
        cascade_amount: false,
        cascade_percentage: false,
        back_into_percentage: false,
      },
      {
        amount: "1.35",
        back_into_percentage: false,
        cascade_amount: true,
        cascade_percentage: true,
        description: "",
        category: LineCategory.SUBSCRIPTION_DUES,
        frozen_value: null,
        id: -6,
        percentage: "0",
        priority: 300,
        type: 10,
      },
    ])
  })
  test("Generates preview line items for a product with no escrow", async () => {
    expect(
      invoiceLines({
        escrowEnabled: false,
        pricing: genPricing(),
        value: "25.00",
        product: genProduct(),
        cascade: true,
        international: false,
        planName: "Basic",
      }),
    ).toEqual([
      {
        id: -1,
        priority: 0,
        type: 0,
        amount: "10.00",
        category: LineCategory.ESCROW_HOLD,
        frozen_value: null,
        percentage: "0",
        description: "",
        cascade_amount: false,
        cascade_percentage: false,
        back_into_percentage: false,
      },
      {
        amount: "1.35",
        back_into_percentage: false,
        cascade_amount: true,
        cascade_percentage: true,
        description: "",
        frozen_value: null,
        id: -6,
        percentage: "0",
        priority: 300,
        type: 10,
        category: LineCategory.SUBSCRIPTION_DUES,
      },
      {
        id: -2,
        priority: 100,
        type: 1,
        amount: "15.00",
        frozen_value: null,
        category: LineCategory.ESCROW_HOLD,
        percentage: "0",
        description: "",
        cascade_amount: false,
        cascade_percentage: false,
        back_into_percentage: false,
      },
    ])
  })
  test("Handles line items for a product with no escrow and a nonsense value", async () => {
    expect(
      invoiceLines({
        escrowEnabled: false,
        pricing: genPricing(),
        value: "boop",
        product: genProduct(),
        cascade: true,
        international: false,
        planName: "Basic",
      }),
    ).toEqual([
      {
        id: -1,
        priority: 0,
        type: 0,
        category: LineCategory.ESCROW_HOLD,
        amount: "10.00",
        frozen_value: null,
        percentage: "0",
        description: "",
        cascade_amount: false,
        cascade_percentage: false,
        back_into_percentage: false,
      },
      {
        amount: "1.35",
        back_into_percentage: false,
        cascade_amount: true,
        cascade_percentage: true,
        description: "",
        frozen_value: null,
        id: -6,
        percentage: "0",
        priority: 300,
        type: 10,
        category: LineCategory.SUBSCRIPTION_DUES,
      },
    ])
  })
  test("Handles line item for no product, no escrow and a nonsense value", async () => {
    expect(
      invoiceLines({
        escrowEnabled: false,
        pricing: genPricing(),
        value: "boop",
        product: null,
        cascade: true,
        international: false,
        planName: "Basic",
      }),
    ).toEqual([])
  })
  test("Bails if the pricing is not available", async () => {
    expect(
      invoiceLines({
        escrowEnabled: false,
        pricing: null,
        value: "boop",
        product: genProduct(),
        cascade: true,
        international: false,
        planName: "Basic",
      }),
    ).toEqual([])
  })
  test("Bails if the plan is unknown", async () => {
    expect(
      invoiceLines({
        escrowEnabled: false,
        pricing: genPricing(),
        value: "boop",
        product: genProduct(),
        cascade: true,
        international: false,
        planName: "Backup",
      }),
    ).toEqual([])
  })
})
