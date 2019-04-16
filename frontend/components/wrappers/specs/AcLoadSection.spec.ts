import {vuetifySetup} from '@/specs/helpers'
import Vuetify from 'vuetify'
import Vue from 'vue'
import Vuex from 'vuex'
import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import {singleRegistry, Singles} from '@/store/singles/registry'
import {listRegistry, Lists} from '@/store/lists/registry'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {ListController} from '@/store/lists/controller'

Vue.use(Vuetify)
Vue.use(Vuex)

describe('AcLoadSection.vue', () => {
  const localVue = createLocalVue()
  localVue.use(Singles)
  localVue.use(Lists)
  let wrapper: Wrapper<Vue>
  let store: ArtStore
  let empty: Wrapper<Vue>
  let list: ListController<any>
  beforeEach(() => {
    vuetifySetup()
    store = createStore()
    listRegistry.reset()
    singleRegistry.reset()
    empty = mount(Empty, {localVue, store, sync: false})
    list = empty.vm.$getList('demo', {endpoint: '/endpoint/'})
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Shows a prompt if the controller fails', async() => {
    store.commit('lists/demo/setFailed', true)
    wrapper = mount(AcLoadSection, {
      localVue, store, propsData: {controller: list}, sync: false, attachToDocument: true,
    })
    expect(wrapper.find('.default-loaded-data').exists()).toBe(false)
    expect(wrapper.find('.retry-button').exists()).toBe(true)
    expect(wrapper.find('.support-button').exists()).toBe(true)
  })
  it('Opens the support menu when the support button is clicked', async() => {
    store.commit('lists/demo/setFailed', true)
    wrapper = mount(AcLoadSection, {
      localVue, store, propsData: {controller: list}, sync: false, attachToDocument: true,
    })
    const button = wrapper.find('.support-button')
    expect(button.exists()).toBe(true)
    expect(store.state.showSupport).toBe(false)
    button.trigger('click')
    await wrapper.vm.$nextTick()
    expect(store.state.showSupport).toBe(true)
  })
})
