import {shallowMount, VueWrapper} from '@vue/test-utils'
import AcError from '../AcError.vue'
import {ArtStore, createStore} from '@/store/index.ts'
import {cleanUp, vueSetup} from '@/specs/helpers/index.ts'
import {describe, expect, beforeEach, afterEach, test} from 'vitest'
import {nextTick} from 'vue'

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
    await nextTick()
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
    await nextTick()
    expect(wrapper.find('.error-container').exists()).toBe(false)
  })
})
