import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import {dummyLineItems, genLineItem} from '@/lib/specs/helpers.ts'
import AcLineItemEditor from '@/components/price_preview/AcLineItemEditor.vue'
import {getTotals} from '@/lib/lineItemFunctions.ts'
import {LineTypes} from '@/types/LineTypes.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'
import {ArtVueInterface} from '@/types/ArtVueInterface.ts'
import {nextTick} from 'vue'

let store: ArtStore
let wrapper: VueWrapper<any>
let empty: ArtVueInterface

describe('AcLineItemEditor.vue', () => {
  beforeEach(() => {
    store = createStore()
    empty = mount(Empty, vueSetup({store})).vm
  })
  test('Mounts', async() => {
    const lineItems = dummyLineItems()
    const line = empty.$getSingle('line', {
      endpoint: '/',
      x: lineItems[0],
    })
    wrapper = mount(AcLineItemEditor, {
      ...vueSetup({store}),
      props: {
        line,
        priceData: getTotals(lineItems),
      },
    })
    await nextTick()
  })
  test('Gives a default label to a discount', async() => {
    const lineItems = dummyLineItems()
    const discount = genLineItem({
      type: LineTypes.ADD_ON,
      amount: '-2',
      id: -500,
      priority: 100,
    })
    lineItems.push(discount)
    const line = empty.$getSingle('line', {
      endpoint: '/',
      x: discount,
    })
    wrapper = mount(AcLineItemEditor, {
      ...vueSetup({store}),
      props: {
        line,
        priceData: getTotals(lineItems),
      },
    })
    await nextTick()
    await nextTick()
    expect(wrapper.html()).toContain('Discount')
  })
  test('Gives a default label to an add-on', async() => {
    const lineItems = dummyLineItems()
    const addOn = genLineItem({
      type: LineTypes.ADD_ON,
      amount: '2',
      id: -500,
      priority: 100,
    })
    lineItems.push(addOn)
    const line = empty.$getSingle('line', {
      endpoint: '/',
      x: addOn,
    })
    wrapper = mount(AcLineItemEditor, {
      ...vueSetup({store}),
      props: {
        line,
        priceData: getTotals(lineItems),
      },
    })
    await nextTick()
    await nextTick()
    expect(wrapper.html()).toContain('Additional requirements')
  })
  test('Gives a default label to the base price', async() => {
    const lineItems = dummyLineItems()
    const addOn = genLineItem({
      type: LineTypes.BASE_PRICE,
      amount: '2',
      id: -500,
      priority: 100,
    })
    lineItems.push(addOn)
    const line = empty.$getSingle('line', {
      endpoint: '/',
      x: addOn,
    })
    wrapper = mount(AcLineItemEditor, {
      ...vueSetup({store}),
      props: {
        line,
        priceData: getTotals(lineItems),
      },
    })
    await nextTick()
    await nextTick()
    expect(wrapper.html()).toContain('Base price')
  })
  test('Gives a default label to other types', async() => {
    const lineItems = dummyLineItems()
    const addOn = genLineItem({
      type: LineTypes.EXTRA,
      amount: '2',
      id: -500,
      priority: 400,
    })
    lineItems.push(addOn)
    const line = empty.$getSingle('line', {
      endpoint: '/',
      x: addOn,
    })
    wrapper = mount(AcLineItemEditor, {
      ...vueSetup({store}),
      props: {
        line,
        priceData: getTotals(lineItems),
      },
    })
    await nextTick()
    await nextTick()
    expect(wrapper.html()).toContain('Accessory item')
  })
  test('Gives a blank label for an unknown type', async() => {
    const lineItems = dummyLineItems()
    const addOn = genLineItem({
      type: 1234,
      amount: '2',
      id: -500,
      priority: 400,
    })
    lineItems.push(addOn)
    const line = empty.$getSingle('line', {
      endpoint: '/',
      x: addOn,
    })
    wrapper = mount(AcLineItemEditor, {
      ...vueSetup({store}),
      props: {
        line,
        priceData: getTotals(lineItems),
      },
    })
    await nextTick()
    await nextTick()
    expect(wrapper.html()).toContain('Other')
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
})
