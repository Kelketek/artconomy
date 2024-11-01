export const LogLevels = {
    DEBUG: 0,
    INFO: 1,
    WARN: 2,
    ERROR: 3,
} as const

export type LogLevelsValue = typeof LogLevels[keyof typeof LogLevels]
