import {Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import {ArtStore, createStore} from '@/store'
import {cleanUp, createVuetify, vueSetup, mount} from '@/specs/helpers'
import Router from 'vue-router'
import {dummyLineItems, genLineItem} from '@/lib/specs/helpers'
import AcLineItemEditor from '@/components/price_preview/AcLineItemEditor.vue'
import {getTotals} from '@/lib/lineItemFunctions'
import {LineTypes} from '@/types/LineTypes'
import Empty from '@/specs/helpers/dummy_components/empty.vue'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let vuetify: Vuetify
let empty: Vue

describe('AcLineItemEditor.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    empty = mount(Empty, {localVue, store, vuetify}).vm
  })
  it('Mounts', async() => {
    const lineItems = dummyLineItems()
    const line = empty.$getSingle('line', {endpoint: '/', x: lineItems[0]})
    wrapper = mount(AcLineItemEditor, {localVue, store, propsData: {line, priceData: getTotals(lineItems)}})
  })
  it('Gives a default label to a discount', async() => {
    const lineItems = dummyLineItems()
    const discount = genLineItem({type: LineTypes.ADD_ON, amount: -2, id: -500, priority: 100})
    lineItems.push(discount)
    const line = empty.$getSingle('line', {endpoint: '/', x: discount})
    wrapper = mount(AcLineItemEditor, {localVue, store, propsData: {line, priceData: getTotals(lineItems)}})
    await wrapper.vm.$nextTick()
    expect(wrapper.html()).toContain('Discount')
  })
  it('Gives a default label to an add-on', async() => {
    const lineItems = dummyLineItems()
    const addOn = genLineItem({type: LineTypes.ADD_ON, amount: 2, id: -500, priority: 100})
    lineItems.push(addOn)
    const line = empty.$getSingle('line', {endpoint: '/', x: addOn})
    wrapper = mount(AcLineItemEditor, {localVue, store, propsData: {line, priceData: getTotals(lineItems)}})
    await wrapper.vm.$nextTick()
    expect(wrapper.html()).toContain('Additional requirements')
  })
  it('Gives a default label to the base price', async() => {
    const lineItems = dummyLineItems()
    const addOn = genLineItem({type: LineTypes.BASE_PRICE, amount: 2, id: -500, priority: 100})
    lineItems.push(addOn)
    const line = empty.$getSingle('line', {endpoint: '/', x: addOn})
    wrapper = mount(AcLineItemEditor, {localVue, store, propsData: {line, priceData: getTotals(lineItems)}})
    await wrapper.vm.$nextTick()
    expect(wrapper.html()).toContain('Base price')
  })
  it('Gives a default label to other types', async() => {
    const lineItems = dummyLineItems()
    const addOn = genLineItem({type: LineTypes.EXTRA, amount: 2, id: -500, priority: 400})
    lineItems.push(addOn)
    const line = empty.$getSingle('line', {endpoint: '/', x: addOn})
    wrapper = mount(AcLineItemEditor, {localVue, store, propsData: {line, priceData: getTotals(lineItems)}})
    await wrapper.vm.$nextTick()
    expect(wrapper.html()).toContain('Accessory item')
  })
  it('Gives a blank label for an unknown type', async() => {
    const lineItems = dummyLineItems()
    const addOn = genLineItem({type: 1234, amount: 2, id: -500, priority: 400})
    lineItems.push(addOn)
    const line = empty.$getSingle('line', {endpoint: '/', x: addOn})
    wrapper = mount(AcLineItemEditor, {localVue, store, propsData: {line, priceData: getTotals(lineItems)}})
    await wrapper.vm.$nextTick()
    expect(wrapper.html()).toContain('Other')
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
})
