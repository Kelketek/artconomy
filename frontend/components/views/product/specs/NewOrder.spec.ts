import {cleanUp, createVuetify, docTarget, flushPromises, genAnon, rs, setViewer, vueSetup} from '@/specs/helpers'
import Router from 'vue-router'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import {genArtistProfile, genOrder, genProduct, genUser} from '@/specs/helpers/fixtures'
import NewOrder from '@/components/views/product/NewOrder.vue'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import mockAxios from '@/__mocks__/axios'
import {genCharacter} from '@/store/characters/specs/fixtures'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let router: Router
let vuetify: Vuetify

describe('NewOrder.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    router = new Router({
      mode: 'history',
      routes: [
        {path: '/test/', name: 'Test', component: Empty},
        {path: '/commission-agreement/', name: 'CommissionAgreement', component: Empty},
        {path: '/user/:username/products/', name: 'Products', component: Empty},
        {path: '/orders/:username/order/:orderId', name: 'Order', component: Empty},
        {path: '/auth/login', name: 'Login', component: Empty},
        {path: '/orders/:username/order/:orderId/:deliverableId', name: 'Deliverable', component: Empty},
      ],
    })
    window.scrollTo = jest.fn()
    window.pintrk = jest.fn()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Resets scroll', async() => {
    const user = genUser()
    setViewer(store, user)
    wrapper = mount(NewOrder, {localVue, store, vuetify, router, propsData: {productId: '1', username: 'Fox'}})
    await wrapper.vm.$nextTick()
    expect(window.scrollTo).toHaveBeenCalledWith(0, 0)
  })
  it('Submits a form with a registered user', async() => {
    const user = genUser()
    setViewer(store, user)
    wrapper = mount(NewOrder, {
      localVue, store, vuetify, router, propsData: {productId: '1', username: 'Fox'}, attachTo: docTarget(),
    })
    const vm = wrapper.vm as any
    vm.subjectHandler.user.makeReady(genUser())
    vm.subjectHandler.artistProfile.makeReady(genArtistProfile())
    vm.product.makeReady(genProduct({id: 1}))
    await vm.$nextTick()
    expect(wrapper.find('#field-newOrder__details').exists()).toBeTruthy()
    const mockPush = jest.spyOn(vm.$router, 'push')
    wrapper.find('#place-order-button').trigger('click')
    await vm.$nextTick()
    const submitted = mockAxios.getReqByUrl('/api/sales/v1/account/Fox/products/1/order/')
    mockAxios.mockResponse(rs(genOrder()), submitted)
    await flushPromises()
    await vm.$nextTick()
    expect(mockPush).toHaveBeenCalledWith({
      name: 'Order',
      params: {
        orderId: '1',
        username: 'Fox',
      },
      query: {
        showConfirm: 'true',
      },
    })
  })
  it('Submits a form with an unregistered user', async() => {
    setViewer(store, genAnon())
    // Need to be on a route for the 'viewer reset' controller code to be able to run.
    wrapper = mount(NewOrder, {
      localVue, store, vuetify, router, propsData: {productId: '1', username: 'Fox'}, attachTo: docTarget(),
    })
    const vm = wrapper.vm as any
    await vm.$router.replace({name: 'Test'})
    vm.subjectHandler.user.makeReady(genUser())
    vm.subjectHandler.artistProfile.makeReady(genArtistProfile())
    vm.product.makeReady(genProduct({id: 1}))
    await vm.$nextTick()
    expect(wrapper.find('#field-newOrder__details').exists()).toBeTruthy()
    const mockPush = jest.spyOn(vm.$router, 'push')
    wrapper.find('#place-order-button').trigger('click')
    await vm.$nextTick()
    const submitted = mockAxios.getReqByUrl('/api/sales/v1/account/Fox/products/1/order/')
    mockAxios.mockResponse(rs(genOrder()), submitted)
    await flushPromises()
    await vm.$nextTick()
    const refresh = mockAxios.getReqByUrl('/api/profiles/v1/data/requester/')
    mockAxios.mockResponse(rs(genAnon()), refresh)
    await flushPromises()
    await vm.$nextTick()
    expect(mockPush).toHaveBeenCalledWith({
      name: 'Order',
      params: {
        orderId: '1',
        username: '_',
      },
      query: {
        showConfirm: 'true',
      },
    })
  })
  it('Fetches character info', async() => {
    const user = genUser()
    setViewer(store, user)
    const form = mount(Empty, {localVue, store, vuetify, router}).vm.$getForm('newOrder', {
      endpoint: '/boop/',
      persistent: true,
      fields: {
        email: {value: ('')},
        private: {value: false},
        characters: {value: [23, 50]},
        rating: {value: 0},
        details: {value: ''},
      },
    })
    wrapper = mount(NewOrder, {localVue, store, vuetify, router, propsData: {productId: '1', username: 'Fox'}})
    const vm = wrapper.vm as any
    vm.subjectHandler.user.makeReady(genUser())
    vm.subjectHandler.artistProfile.makeReady(genArtistProfile())
    vm.product.makeReady(genProduct())
    await vm.$nextTick()
    const successfulRequest = mockAxios.getReqByUrl('/api/profiles/v1/data/character/id/50/')
    const failedRequest = mockAxios.getReqByUrl('/api/profiles/v1/data/character/id/23/')
    const character = genCharacter({name: 'Goof'})
    mockAxios.mockResponse(rs(genCharacter({name: 'Goof'})), successfulRequest)
    mockAxios.mockError(Error('Boop'), failedRequest)
    await flushPromises()
    await vm.$nextTick()
    expect(form.fields.characters.model).toEqual([50])
    expect(vm.initCharacters).toEqual([character])
    expect(vm.showCharacters).toBeTruthy()
  })
})
