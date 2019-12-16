import {Vuetify} from 'vuetify'
import Vue from 'vue'
import {mount, Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {ListController} from '@/store/lists/controller'
import {cleanUp, createVuetify, vueSetup} from '@/specs/helpers'

describe('AcLoadSection.vue', () => {
  const localVue = vueSetup()
  let wrapper: Wrapper<Vue>
  let store: ArtStore
  let empty: Wrapper<Vue>
  let list: ListController<any>
  let vuetify: Vuetify
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    empty = mount(Empty, {
      localVue,
      store,
      vuetify,
      sync: false,
    })
    list = empty.vm.$getList('demo', {endpoint: '/endpoint/'})
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Shows a prompt if the controller fails', async() => {
    store.commit('lists/demo/setFailed', true)
    wrapper = mount(AcLoadSection, {
      localVue,
      store,
      vuetify,
      propsData: {controller: list},
      sync: false,
      attachToDocument: true,
    })
    expect(wrapper.find('.default-loaded-data').exists()).toBe(false)
    expect(wrapper.find('.retry-button').exists()).toBe(true)
    expect(wrapper.find('.support-button').exists()).toBe(true)
  })
  it('Opens the support menu when the support button is clicked', async() => {
    store.commit('lists/demo/setFailed', true)
    wrapper = mount(AcLoadSection, {
      localVue,
      store,
      vuetify,
      propsData: {controller: list},
      sync: false,
      attachToDocument: true,
    })
    const button = wrapper.find('.support-button')
    expect(button.exists()).toBe(true)
    expect(store.state.showSupport).toBe(false)
    button.trigger('click')
    await wrapper.vm.$nextTick()
    expect(store.state.showSupport).toBe(true)
  })
})
