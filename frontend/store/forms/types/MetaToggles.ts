export const MetaToggles = {
  disabled: 'disabled',
  reset: 'reset',
  submitted: 'submitted',
  sending: 'sending',
} as const

export type MetaTogglesValue = typeof MetaToggles[keyof typeof MetaToggles]
