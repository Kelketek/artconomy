import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {dummyLineItems, genLineItem} from '@/lib/specs/helpers.ts'
import AcLineItemPreview from '@/components/price_preview/AcLineItemPreview.vue'
import {getTotals} from '@/lib/lineItemFunctions.ts'
import {LineTypes} from '@/types/LineTypes.ts'
import {describe, expect, beforeEach, afterEach, test} from 'vitest'
import {setViewer} from '@/lib/lib.ts'

let store: ArtStore
let wrapper: VueWrapper<any>

describe('AcLineItemPreview.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  test('Mounts', async() => {
    const user = genUser()
    setViewer(store, user)
    const lineItems = dummyLineItems()
    wrapper = mount(AcLineItemPreview, {
      ...vueSetup({store}),
      props: {
        line: lineItems[0],
        priceData: getTotals(lineItems),
      },
    })
  })
  test('Mounts in edit mode', async() => {
    const user = genUser()
    setViewer(store, user)
    const lineItems = dummyLineItems()
    wrapper = mount(AcLineItemPreview, {
      ...vueSetup({store}),
      props: {
        line: lineItems[0],
        priceData: getTotals(lineItems),
        editing: true,
      },
    })
  })
  test('Handles a line item description', async() => {
    const user = genUser()
    setViewer(store, user)
    const lineItems = dummyLineItems()
    lineItems[0].description = 'Stuff and things'
    wrapper = mount(AcLineItemPreview, {
      ...vueSetup({store}),
      props: {
        line: lineItems[0],
        priceData: getTotals(lineItems),
        editing: true,
      },
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Stuff and things')
  })
  test('Uses a default descriptor for a discount', async() => {
    const user = genUser()
    setViewer(store, user)
    const lineItems = dummyLineItems()
    const line = genLineItem({
      id: -500,
      priority: 100,
      type: LineTypes.ADD_ON,
      amount: '-2',
    })
    lineItems.push(line)
    wrapper = mount(AcLineItemPreview, {
      ...vueSetup({store}),
      props: {
        line,
        priceData: getTotals(lineItems),
      },
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Discount')
  })
  test('Uses a default descriptor for an additional requirement', async() => {
    const user = genUser()
    setViewer(store, user)
    const lineItems = dummyLineItems()
    const line = genLineItem({
      id: -500,
      priority: 100,
      type: LineTypes.ADD_ON,
      amount: '2',
    })
    lineItems.push(line)
    wrapper = mount(AcLineItemPreview, {
      ...vueSetup({store}),
      props: {
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
