export const ViewerType = {
  UNSET: 0,
  BUYER: 1,
  SELLER: 2,
  STAFF: 3,
} as const

export type ViewerTypeValue = typeof ViewerType[keyof typeof ViewerType]