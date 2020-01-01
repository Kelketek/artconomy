import {mount, Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import {Vuetify} from 'vuetify/types'
import {ArtStore, createStore} from '@/store'
import {
  cleanUp,
  confirmAction, createVuetify,
  flushPromises,
  rs,
  setPricing,
  setViewer,
  vueSetup,
} from '@/specs/helpers'
import ProductDetail from '@/components/views/product/ProductDetail.vue'
import {genArtistProfile, genProduct, genUser} from '@/specs/helpers/fixtures'
import mockAxios from '@/__mocks__/axios'
import {searchSchema} from '@/lib'
import {FormController} from '@/store/forms/form-controller'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import Router, {RouterOptions} from 'vue-router'

import {genSubmission} from '@/store/submissions/specs/fixtures'

const localVue = vueSetup()
localVue.use(Router)
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
    path: '/profiles/:username/',
    name: 'Profile',
    component: Empty,
    props: true,
    children: [{
      name: 'Products',
      path: '/products/',
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
    store = createStore()
    vuetify = createVuetify()
    router = new Router(routes)
    form = mount(Empty, {localVue, router, store}).vm.$getForm('search', searchSchema())
    setPricing(store, localVue)
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts', async() => {
    setViewer(store, genUser())
    setPricing(store, localVue)
    wrapper = mount(ProductDetail, {
      localVue, router, store, vuetify, sync: false, attachToDocument: true, propsData: {username: 'Fox', productId: 1},
    })
    expect((wrapper.vm as any).slides).toEqual([])
    const product = genProduct()
    product.primary_submission = null
    mockAxios.mockResponse(rs(product))
    await flushPromises()
    await wrapper.vm.$nextTick()
  })
  it('Deletes a product', async() => {
    const data = prepData()
    router.push({name: 'Product', params: {productId: '1'}})
    wrapper = mount(ProductDetail, {
      localVue,
      router,
      store,
      vuetify,
      sync: false,
      attachToDocument: true,
      propsData: {username: 'Fox', productId: 1},
      stubs: ['ac-sample-editor'],
    })
    mockAxios.reset()
    const vm = wrapper.vm as any
    await vm.$nextTick()
    await confirmAction(wrapper, ['.more-button', '.delete-button'])
    mockAxios.mockResponse(rs({}))
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.$route.name).toBe('Profile')
    expect(data.productSingle.x).toBe(false)
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
      sync: false,
      attachToDocument: true,
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
      sync: false,
      attachToDocument: true,
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
      sync: false,
      attachToDocument: true,
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
  it('Checks escrow disabled', async() => {
    prepData()
    wrapper = mount(ProductDetail, {
      localVue,
      router,
      store,
      vuetify,
      sync: false,
      attachToDocument: true,
      propsData: {username: 'Fox', productId: 1},
      stubs: ['ac-sample-editor', 'v-carousel', 'v-carousel-item'],
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    // No profile loaded yet.
    expect(vm.escrowDisabled).toBe(true)
    vm.subjectHandler.artistProfile.setX(genArtistProfile())
    vm.subjectHandler.artistProfile.ready = true
    await vm.$nextTick()
    expect(vm.escrowDisabled).toBe(false)
  })
  it('Handles meta content', async() => {
    const data = prepData()
    wrapper = mount(ProductDetail, {
      localVue,
      router,
      store,
      vuetify,
      sync: false,
      attachToDocument: true,
      propsData: {username: 'Fox', productId: 1},
      stubs: ['ac-sample-editor', 'v-carousel', 'v-carousel-item'],
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    let description = document.querySelector('meta[name="description"]')
    expect(description).toBeTruthy()
    expect(description!.textContent).toBe('[Starts at $10.00] - This is a test product')
    data.productSingle.updateX({price: 0})
    await vm.$nextTick()
    description = document.querySelector('meta[name="description"]')
    expect(description).toBeTruthy()
    expect(description!.textContent).toBe('[Starts at FREE] - This is a test product')
  })
})
