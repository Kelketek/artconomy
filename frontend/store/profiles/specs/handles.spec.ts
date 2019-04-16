import {createLocalVue, shallowMount} from '@vue/test-utils'
import mockAxios from '@/specs/helpers/mock-axios'
import {userResponse} from '@/specs/helpers/fixtures'
import flushPromises from 'flush-promises'
import {ArtStore, createStore} from '../../index'
import Vue from 'vue'
import Vuex from 'vuex'
import Vuetify from 'vuetify'
import UserProp from '@/specs/helpers/dummy_components/user-prop.vue'
import {singleRegistry, Singles} from '@/store/singles/registry'
import {profileRegistry, Profiles} from '@/store/profiles/registry'
import {Lists} from '@/store/lists/registry'

Vue.use(Vuetify)
const mockError = jest.spyOn(console, 'error')
const mockWarn = jest.spyOn(console, 'warn')

describe('User Handles', () => {
  let store: ArtStore
  let vue: Vue
  const localVue = createLocalVue()
  localVue.use(Vuex)
  localVue.use(Singles)
  localVue.use(Lists)
  localVue.use(Profiles)
  beforeEach(() => {
    mockAxios.reset()
    store = createStore()
    mockError.mockReset()
    profileRegistry.reset()
    singleRegistry.reset()
  })
  it('Populates a user handler', async() => {
    const wrapper = shallowMount(UserProp, {localVue, store})
    expect(mockAxios.get).toHaveBeenCalledTimes(1)
    expect((wrapper.vm as any).subject).toBe(null)
    mockAxios.mockResponse(userResponse())
    await flushPromises()
    expect((wrapper.vm as any).subject).toBeTruthy()
    expect((wrapper.vm as any).subject.username).toBe('Fox')
  })
  it('Gives a warning when using a nonsense prop source on a user handler', async() => {
    mockWarn.mockImplementationOnce(() => undefined)
    const wrapper = shallowMount(UserProp, {localVue, store})
    expect((wrapper.vm as any).target).toBe(null)
    expect(mockWarn).toHaveBeenCalledWith(
      'Expected profile controller on property named \'undefinedHandler\', got ', undefined, ' instead.')
  })
})
