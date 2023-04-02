import {Wrapper} from '@vue/test-utils'
import Vue, {VueConstructor} from 'vue'
import Vuetify from 'vuetify/lib'
import {ArtStore, createStore} from '@/store'
import {
  cleanUp,
  confirmAction,
  createVuetify,
  docTarget,
  flushPromises, genAnon,
  mount,
  rs,
  setPricing,
  setViewer,
  vueSetup,
} from '@/specs/helpers'
import ProductDetail from '@/components/views/product/ProductDetail.vue'
import {genArtistProfile, genProduct, genUser} from '@/specs/helpers/fixtures'
import mockAxios from '@/__mocks__/axios'
import {searchSchema} from '@/lib/lib'
import {FormController} from '@/store/forms/form-controller'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import Router, {RouterOptions} from 'vue-router'

import {genSubmission} from '@/store/submissions/specs/fixtures'
import {getTotals, totalForTypes} from '@/lib/lineItemFunctions'
import {LineTypes} from '@/types/LineTypes'
import {SingleController} from '@/store/singles/controller'
import LineItem from '@/types/LineItem'
import {Decimal} from 'decimal.js'
import {Ratings} from '@/store/profiles/types/Ratings'

let localVue: VueConstructor
let store: ArtStore
let wrapper: Wrapper<Vue>
let form: FormController
let router: Router
let vuetify: Vuetify

function prepData() {
  setViewer(store, genUser())
  setPricing(store, localVue)
  const data = {
    productSingle: mount(
      Empty, {localVue, router, store}).vm.$getSingle('product__1', {endpoint: '/wat/'}),
    samplesList: mount(
      Empty, {localVue, router, store}).vm.$getList('product__1__samples', {endpoint: '/dude/'}),
    recommendedList: mount(
      Empty, {localVue, router, store}).vm.$getList('product__1__recommendations', {endpoint: '/sweet/'}),
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

const routes: RouterOptions = {
  mode: 'history',
  routes: [{
    path: '/upgrade/',
    name: 'Upgrade',
    component: Empty,
    props: true,
  }, {
    path: '/submission/:submissionId/',
    name: 'Submission',
    component: Empty,
    props: true,
  }, {
    path: '/profiles/:username/ratings/',
    name: 'Ratings',
    component: Empty,
    props: true,
  }, {
    path: '/profiles/:username/',
    name: 'Profile',
    component: Empty,
    props: true,
    children: [{
      name: 'AboutUser',
      path: '/about/',
      component: Empty,
      props: true,
    }],
  }, {
    path: '/faq/',
    name: 'FAQ',
    component: Empty,
    props: true,
    children: [{
      name: 'BuyAndSell',
      path: '/buy-and-sell/:question/',
      component: Empty,
      props: true,
    }, {
      path: '/product/:productId/',
      name: 'Product',
      component: Empty,
      props: true,
      children: [{
        name: 'NewOrder',
        path: 'order/',
        component: Empty,
        props: true,
      }],
    }],
  }],
}

describe('ProductDetail.vue', () => {
  beforeEach(() => {
    localVue = vueSetup()
    localVue.use(Router)
    store = createStore()
    vuetify = createVuetify()
    router = new Router(routes)
    form = mount(Empty, {localVue, router, store}).vm.$getForm('search', searchSchema())
    setPricing(store, localVue)
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Determines the slides to show for a product.', async() => {
    setViewer(store, genUser())
    setPricing(store, localVue)
    wrapper = mount(ProductDetail, {
      localVue, router, store, vuetify, attachTo: docTarget(), propsData: {username: 'Fox', productId: 1},
    })
    const vm = wrapper.vm as any
    expect(vm.slides).toEqual([])
    const submission = genSubmission()
    const product = genProduct({primary_submission: submission})
    vm.product.makeReady(product)
    await vm.$nextTick()
    expect(submission).toEqual(vm.slides[0])
    vm.product.updateX({primary_submission: null})
    expect(vm.slides).toEqual([])
  })
  it('Prompts for age if the main sample is above the rating.', async() => {
    setViewer(store, genAnon())
    setPricing(store, localVue)
    wrapper = mount(ProductDetail, {
      localVue, router, store, vuetify, attachTo: docTarget(), propsData: {username: 'Fox', productId: 1},
    })
    const vm = wrapper.vm as any
    vm.samples.setList([])
    await vm.$nextTick()
    vm.product.makeReady(genProduct({primary_submission: genSubmission({rating: Ratings.ADULT})}))
    await vm.$nextTick()
    expect(store.state.showAgeVerification).toBe(true)
  })
  it('Deletes a product', async() => {
    const data = prepData()
    // The following line breaks things.
    await router.push({name: 'Product', params: {productId: '1'}})
    wrapper = mount(ProductDetail, {
      localVue,
      router,
      store,
      vuetify,
      attachTo: docTarget(),
      propsData: {username: 'Fox', productId: 1},
      stubs: ['ac-sample-editor'],
    })
    const vm = wrapper.vm as any
    mockAxios.reset()
    await vm.$nextTick()
    await confirmAction(wrapper, ['.more-button', '.delete-button'])
    mockAxios.mockResponse(rs({}))
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.$route.name).toBe('Profile')
    expect(data.productSingle.x).toBe(null)
    expect(data.productSingle.ready).toBe(false)
    expect(data.productSingle.deleted).toBe(true)
  })
  it('Knows if there is more', async() => {
    const data = prepData()
    const submissions = [
      {id: 7, submission: genSubmission()},
      {id: 8, submission: genSubmission()},
      {id: 9, submission: genSubmission()},
      {id: 10, submission: genSubmission()},
      {id: 11, submission: genSubmission()},
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
      localVue,
      router,
      store,
      vuetify,
      attachTo: docTarget(),
      propsData: {username: 'Fox', productId: 1},
      stubs: ['ac-sample-editor', 'v-carousel', 'v-carousel-item'],
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(vm.more).toBe(false)
    const product = {...vm.product.x}
    product.primary_submission = null
    vm.product.setX(product)
    expect(vm.more).toBe(true)
  })
  it('Can tell you whether the max at once is toggled', async() => {
    prepData()
    wrapper = mount(ProductDetail, {
      localVue,
      router,
      store,
      vuetify,
      attachTo: docTarget(),
      propsData: {username: 'Fox', productId: 1},
      stubs: ['ac-sample-editor', 'v-carousel', 'v-carousel-item'],
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(vm.limitAtOnce).toBe(false)
    expect(vm.product.patchers.max_parallel.model).toBe(0)
    vm.limitAtOnce = true
    expect(vm.limitAtOnce).toBe(true)
    expect(vm.product.patchers.max_parallel.model).toBe(1)
    vm.limitAtOnce = false
    expect(vm.limitAtOnce).toBe(false)
    expect(vm.product.patchers.max_parallel.model).toBe(0)
  })
  it('Generates the submission link', async() => {
    prepData()
    wrapper = mount(ProductDetail, {
      localVue,
      router,
      store,
      vuetify,
      attachTo: docTarget(),
      propsData: {username: 'Fox', productId: 1},
      stubs: ['ac-sample-editor', 'v-carousel', 'v-carousel-item'],
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    vm.shown = null
    expect(vm.shownSubmissionLink).toBeNull()
    const submission = genSubmission()
    submission.id = 1337
    vm.shown = submission
    expect(vm.shownSubmissionLink).toEqual({name: 'Submission', params: {submissionId: '1337'}})
    vm.$router.replace({query: {editing: true}})
    expect(vm.shownSubmissionLink).toBeNull()
  })
  it('Checks escrow availability', async() => {
    prepData()
    wrapper = mount(ProductDetail, {
      localVue,
      router,
      store,
      vuetify,
      attachTo: docTarget(),
      propsData: {username: 'Fox', productId: 1},
      stubs: ['ac-sample-editor', 'v-carousel', 'v-carousel-item'],
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    // No profile loaded yet.
    expect(vm.escrow).toBe(false)
    // This property is checking whether the user has access to escrow, not whether the particular product is escrow
    // enabled. So this change shouldn't affect anythigng.
    vm.product.updateX({table_product: false})
    await vm.$nextTick()
    expect(vm.escrow).toBe(false)
    vm.subjectHandler.artistProfile.makeReady(genArtistProfile({escrow_enabled: false}))
    await vm.$nextTick()
    expect(vm.escrow).toBe(false)
    vm.subjectHandler.artistProfile.updateX({escrow_enabled: true})
    await vm.$nextTick()
    expect(vm.escrow).toBe(true)
  })
  it('Handles meta content', async() => {
    const data = prepData()
    wrapper = mount(ProductDetail, {
      localVue,
      router,
      store,
      vuetify,
      attachTo: docTarget(),
      propsData: {username: 'Fox', productId: 1},
      stubs: ['ac-sample-editor', 'v-carousel', 'v-carousel-item'],
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    let description = document.querySelector('meta[name="description"]')
    expect(description).toBeTruthy()
    expect(description!.textContent).toBe('[Starts at $10.00] - This is a test product')
    data.productSingle.updateX({base_price: 0, starting_price: 0})
    await vm.$nextTick()
    description = document.querySelector('meta[name="description"]')
    expect(description).toBeTruthy()
    expect(description!.textContent).toBe('[Starts at FREE] - This is a test product')
  })
  it('Gives a clear list if pricing info is not yet gathered', async() => {
    prepData()
    wrapper = mount(ProductDetail, {
      localVue,
      router,
      store,
      vuetify,
      attachTo: docTarget(),
      propsData: {username: 'Fox', productId: 1},
      stubs: ['ac-sample-editor', 'v-carousel', 'v-carousel-item'],
    })
    const vm = wrapper.vm as any
    vm.pricing.setX(null)
    await vm.$nextTick()
    const product = genProduct()
    vm.product.setX(product)
    vm.product.ready = true
    await vm.$nextTick()
    expect(vm.lineItemSetMaps.length).toBe(1)
    expect(vm.lineItemSetMaps[0].lineItems.list).toMatchObject([])
  })
  it('Refreshes the product after closing out the workload settings', async() => {
    prepData()
    wrapper = mount(ProductDetail, {
      localVue,
      router,
      store,
      vuetify,
      attachTo: docTarget(),
      propsData: {username: 'Fox', productId: 1},
      stubs: ['ac-sample-editor', 'v-carousel', 'v-carousel-item'],
    })
    const vm = wrapper.vm as any
    const mockRefresh = jest.spyOn(vm.product, 'refresh')
    await vm.$nextTick()
    const product = genProduct()
    vm.product.setX(product)
    vm.product.ready = true
    await vm.$nextTick()
    vm.showWorkload = true
    await vm.$nextTick()
    expect(mockRefresh).not.toHaveBeenCalled()
    vm.showWorkload = false
    await vm.$nextTick()
    expect(mockRefresh).toHaveBeenCalled()
  })
  it('Clears inventory settings and refetches when inventory disabled.', async() => {
    prepData()
    wrapper = mount(ProductDetail, {
      localVue,
      router,
      store,
      vuetify,
      attachTo: docTarget(),
      propsData: {username: 'Fox', productId: 1},
      stubs: ['ac-sample-editor', 'v-carousel', 'v-carousel-item'],
    })
    const vm = wrapper.vm as any
    vm.product.updateX({track_inventory: true})
    vm.inventory.setX({count: 20})
    expect(vm.inventory.x).toEqual({count: 20})
    await vm.$nextTick()
    vm.product.updateX({track_inventory: false})
    await flushPromises()
    await vm.$nextTick()
    expect(vm.inventory.x).toBe(null)
  })
  it('Handles a table product', async() => {
    const data = prepData()
    data.productSingle.updateX({table_product: true})
    wrapper = mount(ProductDetail, {
      localVue,
      router,
      store,
      vuetify,
      attachTo: docTarget(),
      propsData: {username: 'Fox', productId: 1},
      stubs: ['ac-sample-editor', 'v-carousel', 'v-carousel-item'],
    })
    const vm = wrapper.vm as any
    vm.subjectHandler.user.makeReady(genUser())
    expect(totalForTypes(getTotals(vm.lineItemSetMaps[0].lineItems.list.map(
      (x: SingleController<LineItem>) => x.x)),
    [LineTypes.TABLE_SERVICE]),
    ).toEqual(new Decimal('5.54'))
    expect(totalForTypes(getTotals(vm.lineItemSetMaps[0].lineItems.list.map(
      (x: SingleController<LineItem>) => x.x)),
    [LineTypes.SHIELD, LineTypes.BONUS, LineTypes.DELIVERABLE_TRACKING]),
    ).toEqual(new Decimal('0'))
    expect(getTotals(vm.lineItemSetMaps[0].lineItems.list.map(
      (x: SingleController<LineItem>) => x.x)).total,
    ).toEqual(new Decimal('15'))
  })
  it('Handles a shield product', async() => {
    prepData()
    wrapper = mount(ProductDetail, {
      localVue,
      router,
      store,
      vuetify,
      attachTo: docTarget(),
      propsData: {username: 'Fox', productId: 1},
      stubs: ['ac-sample-editor', 'v-carousel', 'v-carousel-item'],
    })
    const vm = wrapper.vm as any
    vm.subjectHandler.user.makeReady(genUser())
    vm.subjectHandler.artistProfile.setX(genArtistProfile())
    vm.subjectHandler.artistProfile.ready = true
    await vm.$nextTick()
    expect(totalForTypes(getTotals(vm.lineItemSetMaps[0].lineItems.list.map(
      (x: SingleController<LineItem>) => x.x)),
    [LineTypes.TABLE_SERVICE]),
    ).toEqual(new Decimal('0'))
    expect(totalForTypes(getTotals(vm.lineItemSetMaps[0].lineItems.list.map(
      (x: SingleController<LineItem>) => x.x)),
    [LineTypes.SHIELD]),
    ).toEqual(new Decimal('4.05'))
  })
  it('Shows the rating modal only when editing', async() => {
    prepData()
    wrapper = mount(ProductDetail, {
      localVue,
      router,
      store,
      vuetify,
      attachTo: docTarget(),
      propsData: {username: 'Fox', productId: 1},
      stubs: ['ac-sample-editor', 'v-carousel', 'v-carousel-item'],
    })
    const vm = wrapper.vm as any
    await router.replace({query: {}})
    vm.subjectHandler.artistProfile.makeReady(genArtistProfile())
    await vm.$nextTick()
    expect(vm.ratingDialog).toBe(false)
    vm.showRating()
    expect(vm.ratingDialog).toBe(false)
    router.replace({query: {editing: 'true'}})
    vm.showRating()
    expect(vm.ratingDialog).toBe(true)
  })
})
