import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import {cleanUp, mount, setPricing, vueSetup} from '@/specs/helpers/index.ts'
import AcPricePreview from '@/components/price_preview/AcPricePreview.vue'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {createRouter, createWebHistory, Router} from 'vue-router'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {dummyLineItems} from '@/lib/specs/helpers.ts'
import {ListController} from '@/store/lists/controller.ts'
import LineItem from '@/types/LineItem.ts'
import {User} from '@/store/profiles/types/User.ts'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'
import {setViewer} from '@/lib/lib.ts'
import {nextTick} from 'vue'

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router
let lineItems: ListController<LineItem>
let user: User

describe('AcPricePreview.vue', () => {
  beforeEach(() => {
    store = createStore()
    router = createRouter({
      history: createWebHistory(),
      routes: [{
        name: 'Upgrade',
        path: '/upgrade/',
        component: Empty,
        props: true,
      }, {
        name: 'Index',
        path: '/',
        component: Empty,
        props: true,
      }],
    })
    setPricing(store)
    lineItems = mount(Empty, vueSetup({store})).vm.$getList('lines', {endpoint: '/'})
    lineItems.setList(dummyLineItems())
    lineItems.ready = true
    user = genUser()
  })
  test('Integrates add-on forms', async() => {
    setViewer(store, user)
    const wrapper = mount(AcPricePreview, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        lineItems,
        username: user.username,
        isSeller: true,
        escrow: true,
      },
    })
    const vm = wrapper.vm as any
    expect(vm.rawPrice).toEqual('80.00')
    vm.addOnForm.fields.amount.update('5.00')
    await nextTick()
    expect(vm.rawPrice).toEqual('85.00')
    vm.extraForm.fields.amount.update('10.00')
    await nextTick()
    expect(vm.rawPrice).toEqual('95.00')
  })
  test('Calculates hourly rate for escrow', async() => {
    setViewer(store, user)
    const wrapper = mount(AcPricePreview, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        lineItems,
        username: user.username,
        isSeller: true,
        escrow: true,
      },
    })
    const vm = wrapper.vm as any
    vm.hourlyForm.fields.hours.model = 2
    await vm.$nextTick()
    expect(vm.hourly).toEqual('36.42')
  })
  test('Calculates hourly rate for non-escrow', async() => {
    setViewer(store, user)
    const wrapper = mount(AcPricePreview, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        lineItems,
        username: user.username,
        isSeller: true,
        escrow: false,
      },
    })
    const vm = wrapper.vm as any
    vm.hourlyForm.fields.hours.model = 2
    await vm.$nextTick()
    expect(vm.hourly).toEqual('40.00')
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
})
