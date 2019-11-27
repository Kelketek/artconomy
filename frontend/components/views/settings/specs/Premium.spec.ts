import Vue from 'vue'
import Router from 'vue-router'
import {mount, Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import {cleanUp, confirmAction, flushPromises, rq, rs, setViewer, vueSetup} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import Premium from '@/components/views/settings/Premium.vue'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import mockAxios from '@/__mocks__/axios';

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let router: Router
let wrapper: Wrapper<Vue>

describe('Premium.vue', () => {
  beforeEach(() => {
    store = createStore()
    router = new Router({
      mode: 'history',
      routes: [{
        name: 'Upgrade',
        component: Empty,
        path: '/upgrade/',
      }, {
        name: 'Premium',
        component: Empty,
        path: '/settings/:username/premium',
        props: true,
      }, {
        name: 'Payment',
        component: Empty,
        path: '/settings/:username/payment',
        props: true,
      }],
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Recognizes a portrait user', async() => {
    const user = genUser()
    user.portrait_enabled = true
    user.portrait = true
    user.portrait_paid_through = '2019-07-26T15:04:41.078424-05:00'
    setViewer(store, user)
    wrapper = mount(Premium, {
      localVue, store, router, propsData: {username: 'Fox'}, attachToDocument: true, sync: false,
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(vm.subscriptionType).toBe('Portrait')
    expect(vm.paidThrough).toBe('2019-07-26T15:04:41.078424-05:00')
  })
  it('Recognizes a landscape user', async() => {
    const user = genUser()
    user.portrait_enabled = true
    user.portrait = true
    user.portrait_paid_through = '2019-06-26T15:04:41.078424-05:00'
    user.landscape_enabled = true
    user.landscape = true
    user.landscape_paid_through = '2019-07-26T15:04:41.078424-05:00'
    setViewer(store, user)
    wrapper = mount(Premium, {
      localVue, store, router, propsData: {username: 'Fox'}, attachToDocument: true, sync: false,
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(vm.subscriptionType).toBe('Landscape')
    expect(vm.paidThrough).toBe('2019-07-26T15:04:41.078424-05:00')
  })
  it('Removes the subscription', async() => {
    const user = genUser()
    user.portrait_enabled = true
    user.portrait = true
    user.portrait_paid_through = '2019-07-26T15:04:41.078424-05:00'
    setViewer(store, user)
    wrapper = mount(Premium, {
      localVue, store, router, propsData: {username: 'Fox'}, attachToDocument: true, sync: false,
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    mockAxios.reset()
    await confirmAction(wrapper, ['.cancel-subscription'])
    expect(mockAxios.post).toHaveBeenCalledWith(
      ...rq('/api/sales/v1/account/Fox/cancel-premium/', 'post', undefined, {}),
    )
    mockAxios.mockResponse(rs(genUser()))
    await flushPromises()
    expect(vm.subject.portrait).toBe(false)
  })
})
