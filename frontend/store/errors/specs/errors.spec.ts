import mockAxios from '@/specs/helpers/mock-axios.ts'
import {ArtStore, createStore} from '../../index.ts'
import {beforeEach, describe, expect, test} from 'vitest'

describe('Errors store', () => {
  let store: ArtStore
  beforeEach(() => {
    mockAxios.reset()
    store = createStore()
  })
  test('Commits an error code', () => {
    store.commit('errors/setError', {response: {status: 500}})
    expect((store.state as any).errors.code).toBe(500)
  })
  test('Clears the error', () => {
    store.commit('errors/setError', {response: {status: 500}})
    store.commit('errors/clearError')
    expect((store.state as any).errors.code).toBe(0)
  })
})
