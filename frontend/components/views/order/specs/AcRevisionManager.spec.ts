import Vue from 'vue'
import {cleanUp, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import AcRevisionManager from '@/components/views/order/AcRevisionManager.vue'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {genOrder, genRevision} from '@/specs/helpers/fixtures'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>

describe('AcRevisionManager.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Determines the final', async() => {
    const empty = mount(
      Empty, {localVue, store, attachToDocument: true, sync: false}).vm
    const revisions = empty.$getList('revisions', {endpoint: '/test/'})
    const order = empty.$getSingle('order', {endpoint: '/order/'})
    order.setX(genOrder())
    order.ready = true
    order.fetching = false
    revisions.setList([genRevision()])
    revisions.ready = true
    revisions.fetching = false
    wrapper = mount(AcRevisionManager, {
      localVue,
      store,
      propsData: {orderId: 3, list: revisions, order, hidden: false, archived: false, isSeller: true, revisionCount: 2},
      sync: false,
      attachToDocument: true,
    })
    const vm = wrapper.vm as any
    expect(vm.final).toBeFalsy()
    order.updateX({final_uploaded: true})
    expect(vm.final).toBeTruthy()
  })
  it('Refreshes the order when the list changes', async() => {
    const empty = mount(
      Empty, {localVue, store, attachToDocument: true, sync: false}).vm
    const revisions = empty.$getList('revisions', {endpoint: '/test/'})
    const order = empty.$getSingle('order', {endpoint: '/order/'})
    order.setX(genOrder())
    order.ready = true
    order.fetching = false
    revisions.setList([])
    revisions.ready = true
    revisions.fetching = false
    wrapper = mount(AcRevisionManager, {
      localVue,
      store,
      propsData: {orderId: 3, list: revisions, order, hidden: false, archived: false, isSeller: true, revisionCount: 2},
      sync: false,
      attachToDocument: true,
    })
    const vm = wrapper.vm as any
    const spyRefresh = jest.spyOn(order, 'refresh')
    revisions.uniquePush(genRevision())
    await vm.$nextTick()
    expect(spyRefresh).toHaveBeenCalled()
  })
  it('Autosubmits when a new file is added', async() => {
    const empty = mount(
      Empty, {localVue, store, attachToDocument: true, sync: false}).vm
    const revisions = empty.$getList('revisions', {endpoint: '/test/'})
    const order = empty.$getSingle('order', {endpoint: '/order/'})
    order.setX(genOrder())
    order.ready = true
    order.fetching = false
    revisions.setList([])
    revisions.ready = true
    revisions.fetching = false
    wrapper = mount(AcRevisionManager, {
      localVue,
      store,
      propsData: {orderId: 3, list: revisions, order, hidden: false, archived: false, isSeller: true, revisionCount: 3},
      sync: false,
      attachToDocument: true,
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    const spySubmit = jest.spyOn(vm.newRevision, 'submitThen')
    vm.newRevision.fields.file.update('Stuff')
    await vm.$nextTick()
    expect(spySubmit).toHaveBeenCalledWith(revisions.uniquePush)
  })
})
