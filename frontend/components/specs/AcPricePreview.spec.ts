import {mount, Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import {ArtStore, createStore} from '@/store'
import {cleanUp, setPricing, setViewer, vueSetup, vuetifySetup} from '@/specs/helpers'
import AcPricePreview from '@/components/AcPricePreview.vue'
import {genUser} from '@/specs/helpers/fixtures'
import Router from 'vue-router'
import Empty from '@/specs/helpers/dummy_components/empty.vue'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let router: Router

describe('AcPricePreview.vue', () => {
  beforeEach(() => {
    store = createStore()
    router = new Router({
      mode: 'history',
      routes: [{
        name: 'Upgrade',
        path: '/upgrade/',
        component: Empty,
        props: true,
      }],
    })
  })
  afterEach(() => {
    cleanUp()
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Previews the affected fees for a user', async() => {
    setViewer(store, genUser())
    setPricing(store, localVue)
    wrapper = mount(AcPricePreview, {
      localVue, store, router, sync: false, attachToDocument: true, propsData: {price: '10.00', username: 'Fox'}}
    )
    const vm = wrapper.vm as any
    expect(vm.serviceFee).toEqual(1.55)
    expect(vm.validPrice).toBe(true)
    expect(vm.landscapeBonus).toBe(0.65)
    expect(vm.userBonus).toBe(0)
    expect(vm.rawPrice).toBe(10.00)
  })
  it('Shows bonuses for landscape', async() => {
    const user = genUser()
    user.landscape = true
    setViewer(store, user)
    setPricing(store, localVue)
    wrapper = mount(AcPricePreview, {
      localVue, store, router, sync: false, attachToDocument: true, propsData: {price: '10.00', username: 'Fox'}}
    )
    const vm = wrapper.vm as any
    expect(vm.serviceFee).toEqual(1.55)
    expect(vm.validPrice).toBe(true)
    expect(vm.landscapeBonus).toBe(0.65)
    expect(vm.userBonus).toBe(0.65)
    expect(vm.rawPrice).toBe(10.00)
  })
  it('Gives NaNs for non-determined pricing', async() => {
    setViewer(store, genUser())
    wrapper = mount(AcPricePreview, {
      localVue, store, sync: false, attachToDocument: true, propsData: {price: '10.00', username: 'Fox'}}
    )
    const vm = wrapper.vm as any
    expect(vm.serviceFee).toBeNaN()
    expect(vm.validPrice).toBe(false)
    expect(vm.landscapeBonus).toBeNaN()
    expect(vm.userBonus).toBe(0)
    expect(vm.rawPrice).toBe(10.00)
  })
  it('Does not count fees when escrow is disabled', async() => {
    setViewer(store, genUser())
    setPricing(store, localVue)
    wrapper = mount(AcPricePreview, {
      localVue, store, router, sync: false, attachToDocument: true, propsData: {price: '10.00', username: 'Fox', escrow: false}}
    )
    const vm = wrapper.vm as any
    expect(vm.serviceFee).toBe(0)
  })
})
