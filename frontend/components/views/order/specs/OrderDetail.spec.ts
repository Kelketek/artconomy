import Vue from 'vue'
import {Vuetify} from 'vuetify/types'
import {cleanUp, confirmAction, createVuetify, flushPromises, rs, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import OrderDetail from '@/components/views/order/OrderDetail.vue'
import {genGuest, genOrder, genUser} from '@/specs/helpers/fixtures'
import {genCharacter} from '@/store/characters/specs/fixtures'
import mockAxios from '@/__mocks__/axios'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import {OrderStatus} from '@/types/OrderStatus'
import moment from 'moment'
import Router from 'vue-router'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import Order from '@/types/Order'
import SessionSettings from '@/components/views/SessionSettings.vue'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let router: Router
let vuetify: Vuetify

describe('OrderDetail.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    router = new Router({
      mode: 'history',
      routes: [{
        name: 'Login',
        component: Empty,
        path: '/login/:tabName/',
        props: true,
      }, {
        name: 'Order',
        component: Empty,
        path: '/orders/:username/order/:orderId/',
        props: true,
      }, {
        name: 'Submission',
        component: Empty,
        path: '/submissions/:submissionId/',
        props: true,
      }, {
        name: 'Products',
        component: Empty,
        path: '/profiles/:username/products/',
        props: true,
      }, {
        name: 'BuyAndSell',
        component: Empty,
        path: '/buy-and-sell/:question',
        props: true,
      }, {
        name: 'Settings',
        component: Empty,
        path: '/:username/settings/',
        props: true,
      }, {
        name: 'TermsOfService',
        component: Empty,
        path: '/terms/',
      }, {
        name: 'SessionSettings',
        component: Empty,
        path: '/settings/session/',
      }, {
        name: 'CommissionAgreement',
        component: Empty,
        path: '/agreement/',
      }],
    })
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Adds character tags to submission form', async() => {
    setViewer(store, genUser())
    await router.push('/orders/Fox/order/1/')
    wrapper = mount(
      OrderDetail, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 3},
        sync: false,
        attachToDocument: true,
        stubs: ['router-link'],
      })
    const vm = wrapper.vm as any
    vm.order.setX(genOrder())
    vm.order.fetching = false
    vm.order.ready = true
    vm.fetching = false
    vm.revisions.setList([])
    vm.revisions.fetching = false
    vm.revisions.ready = true
    const characterRequest = mockAxios.getReqByUrl('/api/sales/v1/order/3/characters/')
    const character = genCharacter()
    character.tags = ['stuff', 'things', 'wat']
    mockAxios.mockResponse(rs([{id: 1, character}]), characterRequest)
    await flushPromises()
    await vm.$nextTick()
    expect([...vm.addSubmission.fields.tags.value].sort()).toEqual(['stuff', 'things', 'wat'])
  })
  it('Updates after payment', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    await router.push('/orders/Fox/order/1/')
    wrapper = mount(
      OrderDetail, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 3},
        sync: false,
        attachToDocument: true,
        stubs: ['router-link', 'ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    const order = genOrder()
    order.status = OrderStatus.PAYMENT_PENDING
    const orderRequest = mockAxios.getReqByUrl('/api/sales/v1/order/3/')
    mockAxios.mockResponse(rs(order), orderRequest)
    await flushPromises()
    await vm.$nextTick()
    vm.fetching = false
    vm.revisions.ready = true
    vm.characters.setList([])
    vm.characters.fetching = false
    vm.characters.ready = false
    mockAxios.reset()
    await vm.$nextTick()
    wrapper.find('.payment-button').trigger('click')
    await vm.$nextTick()
    wrapper.find('.dialog-submit').trigger('click')
    const paymentRequest = mockAxios.lastReqGet()
    expect(paymentRequest.url).toBe('/api/sales/v1/order/3/pay/')
    mockAxios.mockResponse(rs({...order, status: OrderStatus.QUEUED}), paymentRequest)
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect(vm.order.x.status).toBe(OrderStatus.QUEUED)
  })
  it('Identifies seller and buyer outputs', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    await router.push('/orders/Fox/order/1/')
    wrapper = mount(
      OrderDetail, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 3},
        sync: false,
        attachToDocument: true,
        stubs: ['router-link', 'ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    const order = genOrder()
    order.status = OrderStatus.PAYMENT_PENDING
    const orderRequest = mockAxios.getReqByUrl('/api/sales/v1/order/3/')
    mockAxios.mockResponse(rs(order), orderRequest)
    await flushPromises()
    await vm.$nextTick()
    expect(vm.buyerSubmission).toBeNull()
    expect(vm.sellerSubmission).toBeNull()
    const buyerSubmission = genSubmission()
    buyerSubmission.id = 398
    buyerSubmission.owner.username = 'Fox'
    vm.outputs.uniquePush(buyerSubmission)
    await vm.$nextTick()
    expect(vm.buyerSubmission.x.id).toBe(398)
    expect(vm.sellerSubmission).toBeNull()
    const sellerSubmission = genSubmission()
    sellerSubmission.id = 409
    sellerSubmission.owner.username = 'Vulpes'
    vm.outputs.uniquePush(sellerSubmission)
    expect(vm.buyerSubmission.x.id).toBe(398)
    expect(vm.sellerSubmission.x.id).toBe(409)
  })
  it('Identifies seller, buyer, and arbitrator', async() => {
    const fox = genUser()
    fox.username = 'Fox'
    setViewer(store, fox)
    await router.push('/orders/Fox/order/1/')
    wrapper = mount(
      OrderDetail, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 3},
        sync: false,
        attachToDocument: true,
        stubs: ['router-link', 'ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    const order = genOrder()
    const arbitrartor = genUser()
    arbitrartor.username = 'Foxxo'
    order.arbitrator = arbitrartor
    const orderRequest = mockAxios.getReqByUrl('/api/sales/v1/order/3/')
    mockAxios.mockResponse(rs(order), orderRequest)
    await flushPromises()
    await vm.$nextTick()
    expect(vm.buyer.username).toBe('Fox')
    expect(vm.seller.username).toBe('Vulpes')
    expect(vm.arbitrator.username).toBe('Foxxo')
  })
  it('Handles a null buyer', async() => {
    const vulpes = genUser()
    vulpes.username = 'Fox'
    setViewer(store, vulpes)
    await router.push('/orders/Fox/order/1/')
    wrapper = mount(
      OrderDetail, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 3},
        sync: false,
        attachToDocument: true,
        stubs: ['router-link', 'ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    const order = genOrder()
    order.buyer = null
    const orderRequest = mockAxios.getReqByUrl('/api/sales/v1/order/3/')
    mockAxios.mockResponse(rs(order), orderRequest)
    expect(vm.buyer).toBe(null)
    expect(vm.buyerSubmission).toBe(null)
  })
  it('Sends a status update', async() => {
    const vulpes = genUser()
    vulpes.username = 'Vulpes'
    setViewer(store, vulpes)
    await router.push('/orders/Fox/order/1/')
    wrapper = mount(
      OrderDetail, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 3},
        sync: false,
        attachToDocument: true,
        stubs: ['router-link', 'ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    const order = genOrder()
    order.buyer = null
    const orderRequest = mockAxios.getReqByUrl('/api/sales/v1/order/3/')
    mockAxios.mockResponse(rs(order), orderRequest)
    await flushPromises()
    await vm.$nextTick()
    mockAxios.reset()
    await confirmAction(wrapper, ['.accept-order'])
    const lastRequest = mockAxios.lastReqGet()
    expect(lastRequest.url).toBe('/api/sales/v1/order/3/accept/')
    mockAxios.mockResponse(rs({...order, ...{status: 2}}))
    await flushPromises()
    await vm.$nextTick()
    expect(vm.order.x.status).toBe(2)
  })
  it('Sends a user to their new submission', async() => {
    const vulpes = genUser()
    vulpes.username = 'Vulpes'
    setViewer(store, vulpes)
    await router.push('/orders/Fox/order/1/')
    wrapper = mount(
      OrderDetail, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 3},
        sync: false,
        attachToDocument: true,
        stubs: ['router-link', 'ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    const order = genOrder()
    order.status = OrderStatus.COMPLETED
    const orderRequest = mockAxios.getReqByUrl('/api/sales/v1/order/3/')
    mockAxios.mockResponse(rs(order), orderRequest)
    await flushPromises()
    await vm.$nextTick()
    mockAxios.reset()
    vm.showAddSubmission = true
    await vm.$nextTick()
    wrapper.find('.dialog-submit').trigger('click')
    const newSubmission = genSubmission()
    newSubmission.id = 101
    const newSubmissionRequest = mockAxios.lastReqGet()
    expect(newSubmissionRequest.url).toBe('/api/sales/v1/order/3/outputs/')
    mockAxios.mockResponse(rs(newSubmission))
    await flushPromises()
    await vm.$nextTick()
    expect(router.currentRoute.name).toBe('Submission')
    expect(router.currentRoute.params).toEqual({submissionId: '101'})
    expect(router.currentRoute.query).toEqual({editing: 'true'})
  })
  it('Handles an order without a product', async() => {
    setViewer(store, genUser())
    await router.push('/orders/Fox/order/1/')
    wrapper = mount(
      OrderDetail, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 3},
        sync: false,
        attachToDocument: true,
        stubs: ['router-link', 'ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    const order = genOrder()
    order.product = null
    order.status = OrderStatus.COMPLETED
    const orderRequest = mockAxios.getReqByUrl('/api/sales/v1/order/3/')
    mockAxios.mockResponse(rs(order), orderRequest)
    await flushPromises()
    await vm.$nextTick()
  })
  it('Handles different view modes', async() => {
    let user = genUser()
    user.username = 'Dude'
    setViewer(store, user)
    await router.push('/orders/Fox/order/1/')
    wrapper = mount(
      OrderDetail, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 3},
        sync: false,
        attachToDocument: true,
        stubs: ['router-link', 'ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    const order = genOrder()
    order.product = null
    order.status = OrderStatus.COMPLETED
    const orderRequest = mockAxios.getReqByUrl('/api/sales/v1/order/3/')
    mockAxios.mockResponse(rs(order), orderRequest)
    await flushPromises()
    await vm.$nextTick()
    expect(wrapper.find('.view-mode-select').exists()).toBe(true)
    expect(vm.viewMode).toBe(0)
    expect(vm.isBuyer).toBe(false)
    expect(vm.isSeller).toBe(false)
    expect(vm.isBuyer).toBe(false)
    vm.viewMode = 1
    await vm.$nextTick()
    expect(vm.isBuyer).toBe(true)
    expect(vm.isSeller).toBe(false)
    expect(vm.isArbitrator).toBe(false)
    vm.viewMode = 2
    await vm.$nextTick()
    expect(vm.isBuyer).toBe(false)
    expect(vm.isSeller).toBe(true)
    expect(vm.isArbitrator).toBe(false)
    vm.viewMode = 3
    await vm.$nextTick()
    expect(vm.isBuyer).toBe(false)
    expect(vm.isSeller).toBe(false)
    expect(vm.isArbitrator).toBe(true)
  })
  it('Figures if non-completion time has elapsed', async() => {
    let user = genUser()
    user.username = 'Dude'
    setViewer(store, user)
    await router.push('/orders/Fox/order/1/')
    wrapper = mount(
      OrderDetail, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 3},
        sync: false,
        attachToDocument: true,
        stubs: ['router-link', 'ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    const order = genOrder()
    order.product = null
    order.status = OrderStatus.COMPLETED
    const orderRequest = mockAxios.getReqByUrl('/api/sales/v1/order/3/')
    mockAxios.mockResponse(rs(order), orderRequest)
    await flushPromises()
    await vm.$nextTick()
    // @ts-ignore
    vm.order.updateX({dispute_available_on: moment().add(7, 'days').toISOString()})
    await vm.$nextTick()
    // '2019-07-26T15:04:41.078424-05:00'
    expect(vm.disputeTimeElapsed).toBe(false)
    vm.order.updateX({dispute_available_on: '2019-07-26T15:04:41.078424-05:00'})
    await vm.$nextTick()
    expect(vm.disputeTimeElapsed).toBe(true)
    vm.order.updateX({dispute_available_on: null})
    await vm.$nextTick()
    expect(vm.disputeTimeElapsed).toBe(false)
  })
  it('Fetches revisions if they are newly permitted to be seen', async() => {
    setViewer(store, genUser())
    await router.push('/orders/Fox/order/1/')
    wrapper = mount(
      OrderDetail, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 3},
        sync: false,
        attachToDocument: true,
        stubs: ['router-link', 'ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    const order = genOrder()
    order.product = null
    order.status = OrderStatus.PAYMENT_PENDING
    order.revisions_hidden = true
    const orderRequest = mockAxios.getReqByUrl('/api/sales/v1/order/3/')
    mockAxios.mockResponse(rs(order), orderRequest)
    await flushPromises()
    await vm.$nextTick()
    const mockGet = jest.spyOn(vm.revisions, 'get')
    vm.order.updateX({revisions_hidden: false})
    await vm.$nextTick()
    expect(mockGet).toHaveBeenCalled()
  })
  it('Prompts to add revision to collection', async() => {
    setViewer(store, genUser())
    await router.push('/orders/Fox/order/1/')
    wrapper = mount(
      OrderDetail, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 3},
        sync: false,
        attachToDocument: true,
        stubs: ['router-link', 'ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    const order = genOrder()
    order.product = null
    order.status = OrderStatus.COMPLETED
    order.revisions_hidden = false
    vm.order.setX(order)
    vm.order.ready = true
    vm.order.fetching = false
    await vm.$nextTick()
    expect(vm.showAdd)
    wrapper.find('.collection-add').trigger('click')
    expect(vm.showAddSubmission).toBe(true)
  })
  it('Prompts to add revision to collection by registering if they are a guest', async() => {
    const user = genGuest()
    setViewer(store, user)
    await router.push('/orders/Fox/order/1/')
    wrapper = mount(
      OrderDetail, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 3},
        sync: false,
        attachToDocument: true,
        stubs: ['router-link', 'ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    const order = genOrder()
    order.buyer = {...user}
    order.product = null
    order.status = OrderStatus.COMPLETED
    order.claim_token = 'sdvi397awr'
    order.revisions_hidden = false
    vm.order.setX(order)
    vm.order.ready = true
    vm.order.fetching = false
    await vm.$nextTick()
    wrapper.find('.collection-add').trigger('click')
    await vm.$nextTick()
    expect(router.currentRoute.fullPath).toEqual(
      '/login/register?claim=sdvi397awr&next=%2Forders%2FFox%2Forder%2F1%3FshowAdd%3Dtrue',
    )
  })
  it('Does not have the submission adding form loaded by default', async() => {
    setViewer(store, genUser())
    await router.push('/orders/Fox/order/1/')
    wrapper = mount(
      OrderDetail, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 3},
        sync: false,
        attachToDocument: true,
        stubs: ['router-link', 'ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    expect(vm.showAddSubmission).toBe(false)
  })
  it('Loads with the submission prompt triggered', async() => {
    setViewer(store, genUser())
    await router.push('/orders/Fox/order/1/?showAdd=true')
    wrapper = mount(
      OrderDetail, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 3},
        sync: false,
        attachToDocument: true,
        stubs: ['router-link', 'ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    expect(vm.showAddSubmission).toBe(true)
  })
  it('Loads with the order confirmation triggered', async() => {
    setViewer(store, genUser())
    await router.push('/orders/Fox/order/1/?showConfirm=true')
    wrapper = mount(
      OrderDetail, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 3},
        sync: false,
        attachToDocument: true,
        stubs: ['router-link', 'ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(vm.showConfirm).toBe(true)
  })
  it('Prompts to link a guest account', async() => {
    const user = genGuest()
    setViewer(store, user)
    await router.push('/orders/Fox/order/1/')
    wrapper = mount(
      OrderDetail, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 3},
        sync: false,
        attachToDocument: true,
        stubs: ['ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    const order = genOrder()
    order.buyer = {...user}
    order.claim_token = 'sdvi397awr'
    order.revisions_hidden = false
    vm.order.setX(order)
    vm.order.ready = true
    vm.order.fetching = false
    await vm.$nextTick()
    wrapper.find('.link-account').trigger('click')
    await vm.$nextTick()
    expect(router.currentRoute.fullPath).toEqual(
      '/login/register?claim=sdvi397awr&next=%2Forders%2FFox%2Forder%2F1',
    )
  })
  it('Sends an invite email', async() => {
    const user = genUser()
    setViewer(store, user)
    await router.push('/orders/Fox/order/1/')
    wrapper = mount(
      OrderDetail, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 3},
        sync: false,
        attachToDocument: true,
        stubs: ['ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    const order = genOrder()
    order.buyer = null
    order.customer_email = 'stuff@example.com'
    vm.order.setX(order)
    vm.order.fetching = false
    vm.order.ready = true
    await vm.$nextTick()
    mockAxios.reset()
    wrapper.find('.send-invite-button').trigger('click')
    const lastRequest = mockAxios.lastReqGet()
    expect(lastRequest.url).toBe('/api/sales/v1/order/3/invite/')
    mockAxios.mockResponse(rs(order))
    await flushPromises()
    await vm.$nextTick()
    expect(vm.inviteSent).toBe(true)
  })
  it('Gracefully handles commission info', async() => {
    const user = genUser()
    setViewer(store, user)
    await router.push('/orders/Fox/order/1/')
    wrapper = mount(
      OrderDetail, {
        localVue,
        store,
        router,
        vuetify,
        propsData: {orderId: 3},
        sync: false,
        attachToDocument: true,
        stubs: ['ac-revision-manager'],
      })
    const vm = wrapper.vm as any
    expect(vm.commissionInfo).toBe('')
    const order = genOrder()
    order.status = OrderStatus.PAYMENT_PENDING
    vm.order.setX(order)
    vm.order.fetching = false
    vm.order.ready = true
    await vm.$nextTick()
    vm.order.updateX({commission_info: 'Stuff and things'})
    vm.sellerHandler.artistProfile.updateX({commission_info: 'This is a test'})
    await vm.$nextTick()
    expect(vm.commissionInfo).toBe('This is a test')
    vm.order.updateX({status: OrderStatus.NEW})
    await vm.$nextTick()
    expect(vm.commissionInfo).toBe('This is a test')
    vm.order.updateX({status: OrderStatus.QUEUED})
    await vm.$nextTick()
    expect(vm.commissionInfo).toBe('Stuff and things')
  })
})
