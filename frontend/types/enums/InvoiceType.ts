export const InvoiceType = {
  SALE: 0,
  SUBSCRIPTION: 1,
  TERM: 2,
  TIP: 3,
} as const

export type InvoiceTypeValue = typeof InvoiceType[keyof typeof InvoiceType]
