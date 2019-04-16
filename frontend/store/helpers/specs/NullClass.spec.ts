import {NullClass} from '@/store/helpers/NullClass'

describe('NullClass', () => {
  it('Throws an error', () => {
    expect(() => new NullClass()).toThrow(Error('Class not specified.'))
  })
})
