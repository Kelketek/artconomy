export const Ratings = {
  GENERAL: 0,
  MATURE: 1,
  ADULT: 2,
  EXTREME: 3,
} as const

export type RatingsValue = typeof Ratings[keyof typeof Ratings]
