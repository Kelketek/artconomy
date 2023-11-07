import {Router, createRouter, createWebHistory} from 'vue-router'
import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import {
  cleanUp,
  confirmAction,
  flushPromises,
  mount,
  rq,
  rs,
  setViewer,
  vueSetup, VuetifyWrapped,
} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import Premium from '@/components/views/settings/Premium.vue'
import Empty from '@/specs/helpers/dummy_components/empty'
import mockAxios from '@/__mocks__/axios'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

let store: ArtStore
let router: Router
let wrapper: VueWrapper<any>

const WrappedPremium = VuetifyWrapped(Premium)

describe('Premium.vue', () => {
  beforeEach(() => {
    store = createStore()
    router = createRouter({
      history: createWebHistory(),
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
      }, {
        name: 'Home',
        component: Empty,
        path: '/',
        props: true,
      }],
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Removes the subscription', async() => {
    const user = genUser()
    user.landscape_enabled = true
    user.landscape = true
    user.landscape_paid_through = '2019-07-26T15:04:41.078424-05:00'
    setViewer(store, user)
    wrapper = mount(WrappedPremium, {
      ...vueSetup({
        store,
        extraPlugins: [router],
      }),
      props: {username: 'Fox'},
    })
    const vm = wrapper.vm.$refs.vm as any
    await vm.$nextTick()
    mockAxios.reset()
    await confirmAction(wrapper, ['.cancel-subscription'])
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/api/sales/account/Fox/cancel-premium/', 'post', undefined, {}),
    )
    mockAxios.mockResponse(rs(genUser()))
    await flushPromises()
    expect(vm.subject.landscape).toBe(false)
  })
})
