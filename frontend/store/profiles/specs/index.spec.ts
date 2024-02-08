import mockAxios from '@/specs/helpers/mock-axios.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {beforeEach, describe, expect, test} from 'vitest'

describe('Profiles store', () => {
  let store: ArtStore
  beforeEach(() => {
    mockAxios.reset()
    store = createStore()
  })
  test('Sets the viewer username to a token value if the user is not logged in', async() => {
    expect((store.state as any).profiles.viewerRawUsername).toBe('_')
  })
})
