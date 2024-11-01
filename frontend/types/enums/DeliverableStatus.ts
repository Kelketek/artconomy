export const DeliverableStatus = {
  WAITING: 0,
  NEW: 1,
  PAYMENT_PENDING: 2,
  QUEUED: 3,
  IN_PROGRESS: 4,
  REVIEW: 5,
  CANCELLED: 6,
  DISPUTED: 7,
  COMPLETED: 8,
  REFUNDED: 9,
  LIMBO: 10,
  MISSED: 11,
} as const

export type DeliverableStatusValue = typeof DeliverableStatus[keyof typeof DeliverableStatus]
