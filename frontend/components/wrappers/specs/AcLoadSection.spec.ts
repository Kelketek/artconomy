import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import Empty from '@/specs/helpers/dummy_components/empty'
import {ListController} from '@/store/lists/controller'
import {cleanUp, mount, vueSetup} from '@/specs/helpers'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

describe('AcLoadSection.vue', () => {
  let wrapper: VueWrapper<any>
  let store: ArtStore
  let empty: VueWrapper<any>
  let list: ListController<any>
  beforeEach(() => {
    store = createStore()
    empty = mount(Empty, vueSetup({store}))
    list = empty.vm.$getList('demo', {endpoint: '/endpoint/'})
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Shows a prompt if the controller fails', async() => {
    store.commit('lists/demo/setFailed', true)
    wrapper = mount(AcLoadSection, {
      ...vueSetup({store}),
      props: {controller: list},
    })
    expect(wrapper.find('.default-loaded-data').exists()).toBe(false)
    expect(wrapper.find('.retry-button').exists()).toBe(true)
    expect(wrapper.find('.support-button').exists()).toBe(true)
  })
  test('Opens the support menu when the support button is clicked', async() => {
    store.commit('lists/demo/setFailed', true)
    wrapper = mount(AcLoadSection, {
      ...vueSetup({
        store,
      }),
      props: {controller: list},
    })
    const button = wrapper.find('.support-button')
    expect(button.exists()).toBe(true)
    expect(store.state.showSupport).toBe(false)
    button.trigger('click')
    await wrapper.vm.$nextTick()
    expect(store.state.showSupport).toBe(true)
  })
  test('Does not show the spinner if loadOnGrow is set and the list has a length.', async() => {
    store.commit('lists/demo/setFailed', true)
    list.setList([{id: 1}, {id: 2}])
    list.fetching = true
    wrapper = mount(AcLoadSection, {
      ...vueSetup({
        store,
      }),
      props: {
        controller: list,
        loadOnGrow: false,
      },
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
