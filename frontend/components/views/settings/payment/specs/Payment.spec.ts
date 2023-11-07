import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import {Router, createRouter, createWebHistory} from 'vue-router'
import {genUser} from '@/specs/helpers/fixtures'
import {cleanUp, flushPromises, mount, setViewer, vueSetup} from '@/specs/helpers'
import Payment from '../Payment.vue'
import SubjectiveComponent from '@/specs/helpers/dummy_components/subjective-component.vue'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

vi.useFakeTimers()

const paymentRoutes = [
  {
    name: 'Payment',
    path: '/accounts/settings/:username/payment',
    component: Payment,
    props: true,
    children: [
      {
        name: 'Purchase',
        path: 'purchase',
        component: SubjectiveComponent,
        props: true,
      },
      {
        name: 'Payout',
        path: 'payout',
        component: SubjectiveComponent,
        props: true,
      },
      {
        name: 'TransactionHistory',
        path: 'transactions',
        component: SubjectiveComponent,
        props: true,
      },
    ],
  }]

describe('DeliverablePayment.vue', () => {
  let store: ArtStore
  let wrapper: VueWrapper<any>
  let router: Router
  beforeEach(() => {
    store = createStore()
    router = createRouter({
      history: createWebHistory(),
      routes: paymentRoutes,
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Adds Purchase to the route if missing', async() => {
    setViewer(store, genUser())
    await router.replace({
      name: 'Payment',
      params: {username: 'Fox'},
    })
    await flushPromises()
    wrapper = mount(Payment, {
      ...vueSetup({
        store,
        extraPlugins: [router],
      }),
      props: {username: 'Fox'},
    })
    await wrapper.vm.$nextTick()
    await flushPromises()
    expect(router.currentRoute.value.name).toBe('Purchase')
  })
  test('Loads the subordinate route', async() => {
    setViewer(store, genUser())
    await router.push({
      name: 'Payment',
      params: {username: 'Fox'},
    })
    wrapper = mount(Payment, {
      ...vueSetup({
        store,
        extraPlugins: [router],
      }),
      props: {username: 'Fox'},
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('#payout-component').exists()).toBe(false)
    await router.push({
      name: 'Payout',
      params: {username: 'Fox'},
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('#payout-component').exists()).toBe(true)
  })
})
