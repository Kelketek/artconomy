import Vue, {VueConstructor} from 'vue'
import Vuetify from 'vuetify/lib'
import {mount, Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import Router from 'vue-router'
import {genUser} from '@/specs/helpers/fixtures'
import {cleanUp, createVuetify, docTarget, flushPromises, setViewer, vueSetup} from '@/specs/helpers'
import Payment from '../Payment.vue'
import Purchase from '../Purchase.vue'
import Payout from '../Payout.vue'
import SubjectiveComponent from '@/specs/helpers/dummy_components/subjective-component.vue'

jest.useFakeTimers()

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
  let wrapper: Wrapper<Vue>
  let router: Router
  let vuetify: Vuetify
  const localVue = vueSetup()
  localVue.use(Router)
  beforeEach(() => {
    store = createStore()
    router = new Router({
      mode: 'history',
      routes: paymentRoutes,
    })
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Adds Purchase to the route if missing', async() => {
    setViewer(store, genUser())
    router.replace({name: 'Payment', params: {username: 'Fox'}})
    await flushPromises()
    wrapper = mount(Payment, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {username: 'Fox'},
      attachTo: docTarget(),

    })
    await wrapper.vm.$nextTick()
    expect(router.currentRoute.name).toBe('Purchase')
  })
  it('Loads the subordinate route', async() => {
    setViewer(store, genUser())
    router.push({name: 'Payment', params: {username: 'Fox'}})
    wrapper = mount(Payment, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {username: 'Fox'},
      attachTo: docTarget(),

    })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('#payout-component').exists()).toBe(false)
    router.push({name: 'Payout', params: {username: 'Fox'}})
    await wrapper.vm.$nextTick()
    expect(wrapper.find('#payout-component').exists()).toBe(true)
  })
})
