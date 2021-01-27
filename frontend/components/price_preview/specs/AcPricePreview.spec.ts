import {Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import {ArtStore, createStore} from '@/store'
import {cleanUp, createVuetify, docTarget, setPricing, setViewer, vueSetup, mount} from '@/specs/helpers'
import AcPricePreview from '@/components/price_preview/AcPricePreview.vue'
import {genUser} from '@/specs/helpers/fixtures'
import Router from 'vue-router'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {dummyLineItems} from '@/lib/specs/helpers'
import {ListController} from '@/store/lists/controller'
import LineItem from '@/types/LineItem'
import {User} from '@/store/profiles/types/User'
import Big from 'big.js'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let router: Router
let vuetify: Vuetify
let lineItems: ListController<LineItem>
let user: User

describe('AcPricePreview.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    router = new Router({
      mode: 'history',
      routes: [{
        name: 'Upgrade',
        path: '/upgrade/',
        component: Empty,
        props: true,
      }],
    })
    setPricing(store, localVue)
    lineItems = mount(Empty, {localVue, store}).vm.$getList('lines', {endpoint: '/'})
    lineItems.setList(dummyLineItems())
    lineItems.ready = true
    user = genUser()
  })
  it('Integrates add-on forms', async() => {
    setViewer(store, user)
    const wrapper = mount(AcPricePreview, {
      localVue,
      store,
      vuetify,
      router,

      attachTo: docTarget(),
      propsData: {
        lineItems,
        username: user.username,
        isSeller: true,
        escrow: true,
      },
    })
    const vm = wrapper.vm as any
    expect(vm.rawPrice).toEqual(Big('80'))
    vm.addOnForm.fields.amount.update(Big('5'))
    await vm.$nextTick()
    expect(vm.rawPrice).toEqual(Big('85'))
    vm.extraForm.fields.amount.update(Big('10'))
    await vm.$nextTick()
    expect(vm.rawPrice).toEqual(Big('95'))
  })
  it('Adds in the payout bonus if landscape user', async() => {
    setViewer(store, user)
    const wrapper = mount(AcPricePreview, {
      localVue,
      store,
      vuetify,
      router,

      attachTo: docTarget(),
      propsData: {
        lineItems,
        username: user.username,
        isSeller: true,
        escrow: true,
      },
    })
    const vm = wrapper.vm as any
    expect(vm.payout).toEqual(Big('72.85'))
    vm.viewerHandler.user.updateX({landscape: true})
    await vm.$nextTick()
    expect(vm.payout).toEqual(Big('76.30'))
  })
  it('Calculates hourly rate for escrow', async() => {
    setViewer(store, user)
    const wrapper = mount(AcPricePreview, {
      localVue,
      store,
      vuetify,
      router,

      attachTo: docTarget(),
      propsData: {
        lineItems,
        username: user.username,
        isSeller: true,
        escrow: true,
      },
    })
    const vm = wrapper.vm as any
    vm.hours = 2
    expect(vm.hourly).toEqual('36.42')
  })
  it('Calculates hourly rate for non-escrow', async() => {
    setViewer(store, user)
    const wrapper = mount(AcPricePreview, {
      localVue,
      store,
      vuetify,
      router,

      attachTo: docTarget(),
      propsData: {
        lineItems,
        username: user.username,
        isSeller: true,
        escrow: false,
      },
    })
    const vm = wrapper.vm as any
    vm.hours = 2
    expect(vm.hourly).toEqual('40')
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
})
