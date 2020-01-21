import {mount, Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import {Vuetify} from 'vuetify'
import {ArtStore, createStore} from '@/store'
import {cleanUp, createVuetify, setViewer, vueSetup} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import Router from 'vue-router'
import {dummyLineItems, genLineItem} from '@/lib/specs/helpers'
import AcLineItemPreview from '@/components/price_preview/AcLineItemPreview.vue'
import {getTotals} from '@/lib/lineItemFunctions'
import {LineTypes} from '@/types/LineTypes'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

describe('AcLineItemPreview.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  it('Mounts', async() => {
    const user = genUser()
    setViewer(store, user)
    const lineItems = dummyLineItems()
    wrapper = mount(AcLineItemPreview, {localVue, store, propsData: {line: lineItems[0], priceData: getTotals(lineItems)}})
  })
  it('Mounts in edit mode', async() => {
    const user = genUser()
    setViewer(store, user)
    const lineItems = dummyLineItems()
    wrapper = mount(AcLineItemPreview, {
      localVue,
      store,
      propsData: {
        line: lineItems[0],
        priceData: getTotals(lineItems),
        editing: true,
      },
    })
  })
  it('Handles a line item description', async() => {
    const user = genUser()
    setViewer(store, user)
    const lineItems = dummyLineItems()
    lineItems[0].description = 'Stuff and things'
    wrapper = mount(AcLineItemPreview, {
      localVue,
      store,
      propsData: {
        line: lineItems[0],
        priceData: getTotals(lineItems),
        editing: true,
      },
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Stuff and things')
  })
  it('Uses a default descriptor for a discount', async() => {
    const user = genUser()
    setViewer(store, user)
    const lineItems = dummyLineItems()
    const line = genLineItem({
      id: -500,
      priority: 100,
      type: LineTypes.ADD_ON,
      amount: -2,
    })
    lineItems.push(line)
    wrapper = mount(AcLineItemPreview, {
      localVue,
      store,
      propsData: {
        line,
        priceData: getTotals(lineItems),
      },
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Discount')
  })
  it('Uses a default descriptor for an additional requirement', async() => {
    const user = genUser()
    setViewer(store, user)
    const lineItems = dummyLineItems()
    const line = genLineItem({
      id: -500,
      priority: 100,
      type: LineTypes.ADD_ON,
      amount: 2,
    })
    lineItems.push(line)
    wrapper = mount(AcLineItemPreview, {
      localVue,
      store,
      propsData: {
        line,
        priceData: getTotals(lineItems),
      },
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Additional requirements')
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
})
