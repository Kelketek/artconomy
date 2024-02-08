import {VueWrapper} from '@vue/test-utils'
import mockAxios from '@/specs/helpers/mock-axios.ts'
import {userResponse} from '@/specs/helpers/fixtures.ts'
import flushPromises from 'flush-promises'
import {ArtStore, createStore} from '@/store/index.ts'
import UserProp from '@/specs/helpers/dummy_components/user-prop.vue'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'
import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'

const mockError = vi.spyOn(console, 'error')
const mockWarn = vi.spyOn(console, 'warn')

describe('User Handles', () => {
  let store: ArtStore
  let wrapper: VueWrapper<any>
  beforeEach(() => {
    mockAxios.reset()
    store = createStore()
    mockError.mockReset()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Populates a user handler', async() => {
    wrapper = mount(UserProp, vueSetup({store}))
    expect(mockAxios.request).toHaveBeenCalledTimes(1)
    expect((wrapper.vm as any).subject).toBe(null)
    mockAxios.mockResponse(userResponse())
    await flushPromises()
    expect((wrapper.vm as any).subject).toBeTruthy()
    expect((wrapper.vm as any).subject.username).toBe('Fox')
  })
  test('Gives a warning when using a nonsense prop source on a user handler', async() => {
    mockWarn.mockImplementationOnce(() => undefined)
    wrapper = mount(UserProp, vueSetup({store}))
    expect((wrapper.vm as any).target).toBe(null)
    expect(mockWarn).toHaveBeenCalledWith(
      'Expected profile controller on property named \'undefinedHandler\', got ', undefined, ' instead.')
  })
})
