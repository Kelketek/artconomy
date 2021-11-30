import Vue from 'vue'
import Router from 'vue-router'
import {Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import {
  cleanUp,
  confirmAction,
  createVuetify,
  docTarget,
  flushPromises,
  rq,
  rs,
  setViewer,
  vueSetup,
  mount,
} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import Premium from '@/components/views/settings/Premium.vue'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import mockAxios from '@/__mocks__/axios'
import Vuetify from 'vuetify/lib'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let router: Router
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

describe('Premium.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
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
  it('Removes the subscription', async() => {
    const user = genUser()
    user.landscape_enabled = true
    user.landscape = true
    user.landscape_paid_through = '2019-07-26T15:04:41.078424-05:00'
    setViewer(store, user)
    wrapper = mount(Premium, {
      localVue, store, router, vuetify, propsData: {username: 'Fox'}, attachTo: docTarget(),
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
    expect(vm.subject.landscape).toBe(false)
  })
})
