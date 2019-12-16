import Vue from 'vue'
import {shallowMount, Wrapper} from '@vue/test-utils'
import AcError from '../AcError.vue'
import {ArtStore, createStore} from '../../../store'
import {cleanUp, createVuetify, vueSetup} from '@/specs/helpers'
import {Vuetify} from 'vuetify/types'

const localVue = vueSetup()

describe('ac-error', () => {
  let store: ArtStore
  let vuetify: Vuetify
  let wrapper: Wrapper<Vue>
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Shows an error message.', async() => {
    wrapper = shallowMount(AcError, {
      store, localVue, vuetify, sync: false,
    })
    store.commit('errors/setError', {response: {status: 500}})
    await wrapper.vm.$nextTick()
    expect(
      wrapper.find('.error-container img').attributes().src).toBe('/static/images/500.png'
    )
  })
  it('Clears out when error is removed', async() => {
    store.commit('errors/setError', {response: {status: 500}})
    wrapper = shallowMount(AcError, {
      store, localVue, vuetify, sync: false,
    })
    store.commit('errors/clearError')
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.error-container').exists()).toBe(false)
  })
})
