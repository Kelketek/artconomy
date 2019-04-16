import Vue, {VueConstructor} from 'vue'
import Vuex from 'vuex'
import Vuetify from 'vuetify'
import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import Router from 'vue-router'
import {genUser} from '@/specs/helpers/fixtures'
import {flushPromises, setViewer, vuetifySetup} from '@/specs/helpers'
import Payment from '../Payment.vue'
import Purchase from '../Purchase.vue'
import {Singles} from '@/store/singles/registry'
import {Profiles} from '@/store/profiles/registry'
import Payout from '../Payout.vue'
import SubjectiveComponent from '@/specs/helpers/dummy_components/subjective-component.vue'
import {Lists} from '@/store/lists/registry'

// Must use it directly, due to issues with package imports upstream.
Vue.use(Vuetify)
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

describe('Payment.vue', () => {
  let store: ArtStore
  let localVue: VueConstructor
  let wrapper: Wrapper<Vue>
  let router: Router
  beforeEach(() => {
    localVue = createLocalVue()
    localVue.use(Router)
    localVue.use(Vuex)
    localVue.use(Singles)
    localVue.use(Lists)
    localVue.use(Profiles)
    store = createStore()
    router = new Router({
      mode: 'history',
      routes: paymentRoutes,
    })
    vuetifySetup()
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Adds Purchase to the route if missing', async() => {
    setViewer(store, genUser())
    router.replace({name: 'Payment', params: {username: 'Fox'}})
    await flushPromises()
    wrapper = mount(Payment, {
      localVue,
      store,
      router,
      propsData: {username: 'Fox'},
      attachToDocument: true,
      sync: false,
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
      propsData: {username: 'Fox'},
      attachToDocument: true,
      sync: false,
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.find('#payout-component').exists()).toBe(false)
    router.push({name: 'Payout', params: {username: 'Fox'}})
    await wrapper.vm.$nextTick()
    expect(wrapper.find('#payout-component').exists()).toBe(true)
  })
})
