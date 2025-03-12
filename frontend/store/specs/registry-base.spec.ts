import { clearItem } from "@/store/registry-base.ts"
import { describe, expect, test } from "vitest"

describe("registry-base.ts", () => {
  test("Clears a list cleanly", () => {
    const tracker = { thing: [1, 2, 3], stuff: [4, 5, 6] }
    clearItem(tracker, "thing", 1)
    expect(tracker.thing).toEqual([2, 3])
    clearItem(tracker, "thing", 2)
    expect(tracker.thing).toEqual([3])
    clearItem(tracker, "thing", 3)
    expect(tracker.thing).toBe(undefined)
  })
})
