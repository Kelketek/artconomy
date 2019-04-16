import {clearItem} from '@/store/registry-base'

describe('registry-base.ts', () => {
  it('Clears a list cleanly', () => {
    const tracker = {thing: [1, 2, 3], stuff: [4, 5, 6]}
    clearItem(tracker, 'thing', 1)
    expect(tracker.thing).toEqual([2, 3])
    clearItem(tracker, 'thing', 2)
    expect(tracker.thing).toEqual([3])
    clearItem(tracker, 'thing', 3)
    expect(tracker.thing).toBe(undefined)
  })
})
