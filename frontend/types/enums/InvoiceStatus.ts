export const InvoiceStatus = {
  DRAFT: 0,
  OPEN: 1,
  PAID: 2,
  VOID: 5,
} as const

export type InvoiceStatusValue = typeof InvoiceStatus[keyof typeof InvoiceStatus]
