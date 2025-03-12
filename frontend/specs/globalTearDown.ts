/* This file is run before all tests are run to prep the test environment. */

import { LocalStorageMock } from "./setupTestEnv.ts"

const internalWindow = window

export default async function setupTest(globalConfig: any) {
  console.log(globalConfig)
  Object.defineProperty(internalWindow, "localStorage", {
    value: new LocalStorageMock(),
  })
}
