export const ConnectionStatus = {
  CONNECTING: 0,
  CONNECTED: 1,
  CLOSING: 2,
  CLOSED: 3,
} as const

export type ConnectionStatusValue = typeof ConnectionStatus[keyof typeof ConnectionStatus]
