import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import {
  cleanUp,
  confirmAction, createTestRouter,
  docTarget,
  flushPromises,
  mount,
  rs,
  setPricing,
  vueSetup,
  waitFor,
} from '@/specs/helpers/index.ts'
import ProductDetail from '@/components/views/product/ProductDetail.vue'
import {genAnon, genArtistProfile, genProduct, genUser} from '@/specs/helpers/fixtures.ts'
import mockAxios from '@/__mocks__/axios.ts'
import {searchSchema, setViewer} from '@/lib/lib.ts'
import {FormController} from '@/store/forms/form-controller.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {Router} from 'vue-router'

import {genSubmission} from '@/store/submissions/specs/fixtures.ts'
import {getTotals, totalForTypes} from '@/lib/lineItemFunctions.ts'
import {LineType} from '@/types/LineType.ts'
import {SingleController} from '@/store/singles/controller.ts'
import LineItem from '@/types/LineItem.ts'
import {Ratings} from '@/types/Ratings.ts'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'
import {nextTick} from 'vue'

let store: ArtStore
let wrapper: VueWrapper<any>
let form: FormController
let router: Router

function prepData() {
  setViewer(store, genUser())
  setPricing(store)
  const options = vueSetup({store})
  const data = {
    productSingle: mount(
      Empty, options).vm.$getSingle('product__1', {endpoint: '/wat/'}),
    samplesList: mount(
      Empty, options).vm.$getList('product__1__samples', {endpoint: '/dude/'}),
    recommendedList: mount(
      Empty, options).vm.$getList('product__1__recommendations', {endpoint: '/sweet/'}),
  }
  data.productSingle.setX(genProduct())
  data.productSingle.ready = true
  data.productSingle.fetching = false
  data.samplesList.setList([])
  data.samplesList.ready = true
  data.samplesList.fetching = false
  data.recommendedList.setList([])
  data.recommendedList.ready = true
  data.recommendedList.fetching = false
  return data
}

describe('ProductDetail.vue', () => {
  beforeEach(() => {
    store = createStore()
    router = createTestRouter()
    form = mount(Empty, vueSetup({store})).vm.$getForm('search', searchSchema())
    setPricing(store)
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Determines the slides to show for a product.', async() => {
    setViewer(store, genUser())
    setPricing(store)
    wrapper = mount(ProductDetail, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        username: 'Fox',
        productId: 1,
      },
    })
    const vm = wrapper.vm as any
    expect(vm.slides).toEqual([])
    const submission = genSubmission()
    const product = genProduct({primary_submission: submission})
    vm.product.makeReady(product)
    await nextTick()
    expect(submission).toEqual(vm.slides[0])
    vm.product.updateX({primary_submission: null})
    expect(vm.slides).toEqual([])
  })
  test('Prompts for age if the main sample is above the rating.', async() => {
    setViewer(store, genAnon())
    setPricing(store)
    wrapper = mount(ProductDetail, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        username: 'Fox',
        productId: 1,
      },
    })
    const vm = wrapper.vm as any
    vm.samples.setList([])
    await nextTick()
    vm.product.makeReady(genProduct({primary_submission: genSubmission({rating: Ratings.ADULT})}))
    await nextTick()
    expect(vm.maxSampleRating).toBe(Ratings.ADULT)
    await flushPromises()
    await waitFor(() => expect(store.state.showAgeVerification).toBe(true))
  })
  // This test fails due to an infinite recursion issue in a computed property. It's not clear how it happens because
  // we can't get a useful traceback. Revisit when the tooling improves.
  test('Deletes a product', async() => {
    const data = prepData()
    // The following line breaks things.
    await router.push({
      name: 'Product',
      params: {productId: '1', username: 'Fox'},
    })
    wrapper = mount(ProductDetail, {
      ...vueSetup({
        store,
        router,
        stubs: ['ac-sample-editor'],
      }),
      props: {
        username: 'Fox',
        productId: 1,
      },
    })
    mockAxios.reset()
    await nextTick()
    await confirmAction(wrapper, ['.more-button', '.delete-button'])
    mockAxios.mockResponse(rs({}))
    await flushPromises()
    await nextTick()
    await waitFor(() => expect(router.currentRoute.value.name).toBe('Profile'))
    expect(data.productSingle.x).toBe(null)
    expect(data.productSingle.ready).toBe(false)
    expect(data.productSingle.deleted).toBe(true)
  })
  test('Knows if there is more', async() => {
    const data = prepData()
    const submissions = [
      {
        id: 7,
        submission: genSubmission(),
      },
      {
        id: 8,
        submission: genSubmission(),
      },
      {
        id: 9,
        submission: genSubmission(),
      },
      {
        id: 10,
        submission: genSubmission(),
      },
      {
        id: 11,
        submission: genSubmission(),
      },
    ]
    // @ts-ignore
    submissions[0].submission.id = 1
    // @ts-ignore
    submissions[1].submission.id = 2
    // @ts-ignore
    submissions[2].submission.id = 3
    // @ts-ignore
    submissions[3].submission.id = 5
    // @ts-ignore
    submissions[4].submission.id = 6
    data.samplesList.setList(submissions)
    wrapper = mount(ProductDetail, {
      ...vueSetup({
        store,
        router,
        stubs: ['ac-sample-editor'],
      }),
      props: {
        username: 'Fox',
        productId: 1,
      },
    })
    const vm = wrapper.vm as any
    await nextTick()
    expect(vm.more).toBe(false)
    const product = {...vm.product.x}
    product.primary_submission = null
    vm.product.setX(product)
    expect(vm.more).toBe(true)
  })
  test('Can tell you whether the max at once is toggled', async() => {
    prepData()
    wrapper = mount(ProductDetail, {
      ...vueSetup({
        store,
        router,
        stubs: ['ac-sample-editor', 'v-carousel', 'v-carousel-item'],
      }),
      props: {
        username: 'Fox',
        productId: 1,
      },
    })
    const vm = wrapper.vm as any
    await nextTick()
    expect(vm.limitAtOnce).toBe(false)
    expect(vm.product.patchers.max_parallel.model).toBe(0)
    vm.limitAtOnce = true
    expect(vm.limitAtOnce).toBe(true)
    expect(vm.product.patchers.max_parallel.model).toBe(1)
    vm.limitAtOnce = false
    expect(vm.limitAtOnce).toBe(false)
    expect(vm.product.patchers.max_parallel.model).toBe(0)
  })
  test('Generates the submission link', async() => {
    prepData()
    wrapper = mount(ProductDetail, {
      ...vueSetup({
        store,
        router,
        stubs: ['ac-sample-editor', 'v-carousel', 'v-carousel-item'],
      }),
      props: {
        username: 'Fox',
        productId: 1,
      },
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    vm.shown = null
    expect(vm.shownSubmissionLink).toBeNull()
    const submission = genSubmission()
    submission.id = 1337
    vm.shown = submission
    expect(vm.shownSubmissionLink).toEqual({
      name: 'Submission',
      params: {submissionId: '1337'},
    })
    await router.replace({query: {editing: 'true'}})
    expect(vm.shownSubmissionLink).toBeNull()
  })
  test('Checks escrow availability', async() => {
    prepData()
    wrapper = mount(ProductDetail, {
      ...vueSetup({
        store,
        router,
        stubs: ['ac-sample-editor', 'v-carousel', 'v-carousel-item'],
      }),
      props: {
        username: 'Fox',
        productId: 1,
      },
    })
    const vm = wrapper.vm as any
    await nextTick()
    // No profile loaded yet.
    expect(vm.escrow).toBe(false)
    // This property is checking whether the user has access to escrow, not whether the particular product is escrow
    // enabled. So this change shouldn't affect anythigng.
    vm.product.updateX({table_product: false})
    await nextTick()
    expect(vm.escrow).toBe(false)
    vm.subjectHandler.artistProfile.makeReady(genArtistProfile({escrow_enabled: false}))
    await nextTick()
    expect(vm.escrow).toBe(false)
    vm.subjectHandler.artistProfile.updateX({escrow_enabled: true})
    await nextTick()
    expect(vm.escrow).toBe(true)
  })
  test('Handles meta content', async() => {
    const data = prepData()
    wrapper = mount(ProductDetail, {
      ...vueSetup({
        store,
        router,
        stubs: ['ac-sample-editor', 'v-carousel', 'v-carousel-item'],
      }),
      props: {
        username: 'Fox',
        productId: 1,
      },
    })
    const vm = wrapper.vm as any
    await nextTick()
    let description = document.querySelector('meta[name="description"]')
    expect(description).toBeTruthy()
    expect(description!.textContent).toBe('[Starts at $10.00] - This is a test product')
    data.productSingle.updateX({
      base_price: 0,
      starting_price: 0,
    })
    await nextTick()
    description = document.querySelector('meta[name="description"]')
    expect(description).toBeTruthy()
    expect(description!.textContent).toBe('[Starts at FREE] - This is a test product')
  })
  test('Gives a clear list if pricing info is not yet gathered', async() => {
    prepData()
    wrapper = mount(ProductDetail, {
      ...vueSetup({
        store,
        router,
        stubs: ['ac-sample-editor', 'v-carousel', 'v-carousel-item'],
      }),
      props: {
        username: 'Fox',
        productId: 1,
      },
    })
    const vm = wrapper.vm as any
    vm.pricing.setX(null)
    await nextTick()
    const product = genProduct()
    vm.product.setX(product)
    vm.product.ready = true
    await nextTick()
    expect(vm.lineItemSetMaps.length).toBe(1)
    expect(vm.lineItemSetMaps[0].lineItems.list).toMatchObject([])
  })
  test('Refreshes the product after closing out the workload settings', async() => {
    prepData()
    wrapper = mount(ProductDetail, {
      ...vueSetup({
        store,
        router,
        stubs: ['ac-sample-editor', 'v-carousel', 'v-carousel-item'],
      }),
      props: {
        username: 'Fox',
        productId: 1,
      },
    })
    const vm = wrapper.vm as any
    const mockRefresh = vi.spyOn(vm.product, 'refresh')
    await nextTick()
    const product = genProduct()
    vm.product.setX(product)
    vm.product.ready = true
    await nextTick()
    vm.showWorkload = true
    await nextTick()
    expect(mockRefresh).not.toHaveBeenCalled()
    vm.showWorkload = false
    await nextTick()
    expect(mockRefresh).toHaveBeenCalled()
  })
  test('Clears inventory settings and refetches when inventory disabled.', async() => {
    prepData()
    wrapper = mount(ProductDetail, {
      ...vueSetup({
        store,
        router,
        stubs: ['ac-sample-editor', 'v-carousel', 'v-carousel-item'],
      }),
      attachTo: docTarget(),
      props: {
        username: 'Fox',
        productId: 1,
      },
    })
    const vm = wrapper.vm as any
    vm.product.updateX({track_inventory: true})
    vm.inventory.setX({count: 20})
    expect(vm.inventory.x).toEqual({count: 20})
    await nextTick()
    vm.product.updateX({track_inventory: false})
    await flushPromises()
    await nextTick()
    expect(vm.inventory.x).toBe(null)
  })
  test('Handles a table product', async() => {
    const data = prepData()
    data.productSingle.updateX({table_product: true})
    wrapper = mount(ProductDetail, {
      ...vueSetup({
        store,
        router,
        stubs: ['ac-sample-editor', 'v-carousel', 'v-carousel-item'],
      }),
      props: {
        username: 'Fox',
        productId: 1,
      },
    })
    const vm = wrapper.vm as any
    vm.subjectHandler.user.makeReady(genUser())
    await waitFor(() => expect(totalForTypes(getTotals(vm.lineItemSetMaps[0].lineItems.list.map(
        (x: SingleController<LineItem>) => x.x)),
      [LineType.TABLE_SERVICE]),
    ).toEqual('5.54'))
    expect(totalForTypes(getTotals(vm.lineItemSetMaps[0].lineItems.list.map(
        (x: SingleController<LineItem>) => x.x)),
      [LineType.SHIELD, LineType.BONUS, LineType.DELIVERABLE_TRACKING]),
    ).toEqual('0.00')
    expect(getTotals(vm.lineItemSetMaps[0].lineItems.list.map(
      (x: SingleController<LineItem>) => x.x)).total,
    ).toEqual('15.00')
  })
  test('Handles a shield product', async() => {
    prepData()
    wrapper = mount(ProductDetail, {
      ...vueSetup({
        store,
        router,
        stubs: ['ac-sample-editor', 'v-carousel', 'v-carousel-item'],
      }),
      props: {
        username: 'Fox',
        productId: 1,
      },
    })
    const vm = wrapper.vm as any
    vm.subjectHandler.user.makeReady(genUser())
    vm.subjectHandler.artistProfile.setX(genArtistProfile())
    vm.subjectHandler.artistProfile.ready = true
    await waitFor(() => expect(totalForTypes(getTotals(vm.lineItemSetMaps[0].lineItems.list.map(
        (x: SingleController<LineItem>) => x.x)),
      [LineType.SHIELD]),
    ).toEqual('4.05'))
    expect(totalForTypes(getTotals(vm.lineItemSetMaps[0].lineItems.list.map(
        (x: SingleController<LineItem>) => x.x)),
      [LineType.TABLE_SERVICE]),
    ).toEqual('0.00')
  })
  test('Shows the rating modal only when editing', async() => {
    prepData()
    wrapper = mount(ProductDetail, {
      ...vueSetup({
        store,
        router,
        stubs: ['ac-sample-editor', 'v-carousel', 'v-carousel-item'],
      }),
      attachTo: docTarget(),
      props: {
        username: 'Fox',
        productId: 1,
      },
    })
    const vm = wrapper.vm as any
    await router.replace({query: {}})
    vm.subjectHandler.artistProfile.makeReady(genArtistProfile())
    await nextTick()
    expect(vm.ratingDialog).toBe(false)
    vm.showRating()
    expect(vm.ratingDialog).toBe(false)
    await router.replace({query: {editing: 'true'}})
    vm.showRating()
    expect(vm.ratingDialog).toBe(true)
  })
})
