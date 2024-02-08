import {NullClass} from '@/store/helpers/NullClass.ts'
import {describe, expect, test} from 'vitest'

describe('NullClass', () => {
  test('Throws an error', () => {
    expect(() => new NullClass()).toThrow(Error('Class not specified.'))
  })
})
