import {NullClass} from '@/store/helpers/NullClass'
import {describe, expect, test} from 'vitest'

describe('NullClass', () => {
  test('Throws an error', () => {
    expect(() => new NullClass()).toThrow(Error('Class not specified.'))
  })
})
