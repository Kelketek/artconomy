import Vue from 'vue'
import Vuex from 'vuex'
import Vuetify from 'vuetify'
import {createLocalVue, shallowMount} from '@vue/test-utils'
import AcError from '../AcError.vue'
import {ArtStore, createStore} from '../../../store'

// Must use it directly, due to issues with package imports upstream.
Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.use(Vuex)

describe('ac-error', () => {
  let store: ArtStore
  beforeEach(() => {
    store = createStore()
  })
  it('Shows an error message.', async() => {
    const wrapper = shallowMount(AcError, {
      store, localVue, sync: false,
    })
    store.commit('errors/setError', {response: {status: 500}})
    await wrapper.vm.$nextTick()
    expect(
      wrapper.find('.error-container img').attributes().src).toBe('/static/images/500.png'
    )
  })
  it('Clears out when error is removed', async() => {
    store.commit('errors/setError', {response: {status: 500}})
    const wrapper = shallowMount(AcError, {
      store, localVue, sync: false,
    })
    store.commit('errors/clearError')
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.error-container').exists()).toBe(false)
  })
})
