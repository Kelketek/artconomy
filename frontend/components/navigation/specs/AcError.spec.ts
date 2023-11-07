import {shallowMount, VueWrapper} from '@vue/test-utils'
import AcError from '../AcError.vue'
import {ArtStore, createStore} from '../../../store'
import {cleanUp, createVuetify, vueSetup} from '@/specs/helpers'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

describe('ac-error', () => {
  let store: ArtStore
  let wrapper: VueWrapper<any>
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Shows an error message.', async() => {
    wrapper = shallowMount(AcError, vueSetup({
      store,
    }))
    store.commit('errors/setError', {response: {status: 500}})
    await wrapper.vm.$nextTick()
    expect(
      wrapper.find('.error-container img').attributes().src).toBe('/static/images/500.png',
    )
  })
  test('Clears out when error is removed', async() => {
    store.commit('errors/setError', {response: {status: 500}})
    wrapper = shallowMount(AcError, vueSetup({
      store,
    }))
    store.commit('errors/clearError')
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.error-container').exists()).toBe(false)
  })
})
