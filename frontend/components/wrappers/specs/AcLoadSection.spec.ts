import Vuetify from 'vuetify/lib'
import Vue from 'vue'
import {mount, Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {ListController} from '@/store/lists/controller'
import {cleanUp, createVuetify, docTarget, vueSetup} from '@/specs/helpers'

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

      attachTo: docTarget(),
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

      attachTo: docTarget(),
    })
    const button = wrapper.find('.support-button')
    expect(button.exists()).toBe(true)
    expect(store.state.showSupport).toBe(false)
    button.trigger('click')
    await wrapper.vm.$nextTick()
    expect(store.state.showSupport).toBe(true)
  })
  it('Does not show the spinner if loadOnGrow is set and the list has a length.', async() => {
    store.commit('lists/demo/setFailed', true)
    list.setList([{id: 1}, {id: 2}])
    list.fetching = true
    wrapper = mount(AcLoadSection, {
      localVue,
      store,
      vuetify,
      propsData: {controller: list, loadOnGrow: false},

      attachTo: docTarget(),
    })
    await wrapper.vm.$nextTick()
    let button = wrapper.find('.loading-spinner-container')
    expect(button.exists()).toBe(true)
    list.grow = true
    await wrapper.vm.$nextTick()
    button = wrapper.find('.loading-spinner-container')
    expect(button.exists()).toBe(false)
    list.setList([])
    await wrapper.vm.$nextTick()
    button = wrapper.find('.loading-spinner-container')
    expect(button.exists()).toBe(true)
  })
})
