import {cleanUp, flushPromises, mount, rs, vueSetup, waitFor} from '@/specs/helpers/index.ts'
import {createRouter, createWebHistory, Router} from 'vue-router'
import {ArtStore, createStore} from '@/store/index.ts'
import {VueWrapper} from '@vue/test-utils'
import {genAnon, genArtistProfile, genOrder, genProduct, genUser} from '@/specs/helpers/fixtures.ts'
import NewOrder from '@/components/views/product/NewOrder.vue'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import mockAxios from '@/__mocks__/axios.ts'
import {genCharacter} from '@/store/characters/specs/fixtures.ts'
import {afterEach, beforeEach, describe, expect, test, vi} from 'vitest'
import {nextTick} from 'vue'
import {setViewer} from '@/lib/lib.ts'

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router

describe('NewOrder.vue', () => {
  beforeEach(() => {
    window.fbq = vi.fn()
    store = createStore()
    router = createRouter({
      history: createWebHistory(),
      routes: [
        {
          path: '/',
          name: 'Home',
          component: Empty,
        },
        {
          path: '/test/',
          name: 'Test',
          component: Empty,
        },
        {
          path: '/commission-agreement/',
          name: 'CommissionAgreement',
          component: Empty,
        },
        {
          path: '/user/:username/about/',
          name: 'AboutUser',
          component: Empty,
        },
        {
          path: '/orders/:username/order/:orderId',
          name: 'Order',
          component: Empty,
        },
        {
          path: '/auth/login/',
          name: 'Login',
          component: Empty,
        },
        {
          path: '/faq/buy-and-sell/:question',
          name: 'BuyAndSell',
          component: Empty,
        },
        {
          path: '/orders/:username/order/:orderId/:deliverableId',
          name: 'Deliverable',
          component: Empty,
        },
        {
          path: '/orders/:username/order/:orderId/:deliverableId/payment',
          name: 'SaleDeliverablePayment',
          component: Empty,
        },
        {
          path: '/store/:username/products/:productId/order/:stepId?/',
          name: 'NewOrder',
          component: Empty,
        },
      ],
    })
    router.push({
      name: 'NewOrder',
      params: {
        productId: '1',
        username: 'Fox',
        stepId: '1',
      },
    })
    const mockScrollTo = vi.spyOn(window, 'scrollTo')
    mockScrollTo.mockImplementationOnce(() => undefined)
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Resets scroll', async() => {
    const user = genUser()
    setViewer(store, user)
    wrapper = mount(NewOrder, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        productId: '1',
        username: 'Fox',
      },
    })
    await nextTick()
    expect(window.scrollTo).toHaveBeenCalledWith(0, 0)
  })
  test('Submits a form with a registered user', async() => {
    const user = genUser({username: 'OtherPerson'})
    setViewer(store, user)
    wrapper = mount(NewOrder, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        productId: '1',
        username: 'Fox',
      },
    })
    const vm = wrapper.vm as any
    vm.subjectHandler.user.makeReady(genUser())
    vm.subjectHandler.artistProfile.makeReady(genArtistProfile())
    vm.product.makeReady(genProduct({id: 1}))
    vm.orderForm.step = 2
    await nextTick()
    await waitFor(() => expect(wrapper.find('#field-newOrder__details').exists()).toBeTruthy())
    vm.orderForm.step = 3
    await nextTick()
    await wrapper.find('.submit-button').trigger('click')
    await nextTick()
    const submitted = mockAxios.getReqByUrl('/api/sales/account/Fox/products/1/order/')
    mockAxios.mockResponse(rs(genOrder()), submitted)
    await flushPromises()
    await nextTick()
    await waitFor(() => expect(router.currentRoute.value.name).toBe('Order'))
    expect(router.currentRoute.value.params).toEqual({
      orderId: '1',
      username: 'Fox',
    })
    expect(router.currentRoute.value.query).toEqual({
      showConfirm: 'true',
    })
  })
  test('Creates an invoice for an artist', async() => {
    const user = genUser()
    setViewer(store, user)
    wrapper = mount(NewOrder, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        productId: '1',
        username: 'Fox',
      },
    })
    const vm = wrapper.vm as any
    vm.subjectHandler.user.makeReady(genUser())
    vm.subjectHandler.artistProfile.makeReady(genArtistProfile())
    vm.product.makeReady(genProduct({id: 1}))
    vm.orderForm.step = 2
    await nextTick()
    expect(wrapper.find('#field-newOrder__details').exists()).toBeTruthy()
    vm.orderForm.step = 3
    await nextTick()
    await wrapper.find('.submit-button').trigger('click')
    await nextTick()
    const submitted = mockAxios.getReqByUrl('/api/sales/account/Fox/products/1/order/')
    mockAxios.mockResponse(rs(genOrder({
      default_path: {
        name: 'SaleDeliverableOverview',
        params: {
          orderId: '1',
          deliverableId: '5',
          username: 'Fox',
        },
      },
    })), submitted)
    await waitFor(() => expect(router.currentRoute.value.name).toEqual('SaleDeliverablePayment'))
    expect(router.currentRoute.value.params).toEqual({
      orderId: '1',
      deliverableId: '5',
      username: 'Fox',
    })
    expect(router.currentRoute.value.query).toEqual({
      view_as: 'Seller',
    })
  })
  test('Submits a table order', async() => {
    const user = genUser()
    setViewer(store, user)
    wrapper = mount(NewOrder, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        productId: '1',
        username: 'Fox',
      },
    })
    const vm = wrapper.vm as any
    vm.subjectHandler.user.makeReady(genUser({is_staff: true}))
    vm.subjectHandler.artistProfile.makeReady(genArtistProfile())
    vm.product.makeReady(genProduct({
      id: 1,
      table_product: true,
    }))
    vm.orderForm.step = 2
    await nextTick()
    expect(wrapper.find('#field-newOrder__details').exists()).toBeTruthy()
    vm.orderForm.step = 3
    await nextTick()
    await wrapper.find('.submit-button').trigger('click')
    await nextTick()
    const submitted = mockAxios.getReqByUrl('/api/sales/account/Fox/products/1/order/')
    mockAxios.mockResponse(rs(genOrder({
      default_path: {
        name: 'OrderDeliverableOverview',
        params: {
          orderId: '1',
          deliverableId: '1',
          username: 'Fox',
        },
      },
    })), submitted)
    await flushPromises()
    await nextTick()
    await waitFor(() => expect(router.currentRoute.value.name).toEqual('SaleDeliverablePayment'))
    expect(router.currentRoute.value.params).toEqual({
      orderId: '1',
      deliverableId: '1',
      username: 'Fox',
    })
    expect(router.currentRoute.value.query).toEqual({
      view_as: 'Seller',
    })
  })
  test('Submits a form with an unregistered user', async() => {
    setViewer(store, genAnon())
    // Need to be on a route for the 'viewer reset' controller code to be able to run.
    wrapper = mount(NewOrder, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        productId: '1',
        username: 'Fox',
      },
    })
    const vm = wrapper.vm as any
    await router.replace({name: 'Test'})
    vm.subjectHandler.user.makeReady(genUser())
    vm.subjectHandler.artistProfile.makeReady(genArtistProfile())
    vm.product.makeReady(genProduct({id: 1}))
    vm.orderForm.step = 2
    await nextTick()
    expect(wrapper.find('#field-newOrder__details').exists()).toBeTruthy()
    vm.orderForm.step = 3
    await nextTick()
    await waitFor(() => expect(router.currentRoute.value.query).toEqual({stepId: '3'}))
    await wrapper.find('.submit-button').trigger('click')
    await nextTick()
    const submitted = mockAxios.getReqByUrl('/api/sales/account/Fox/products/1/order/')
    mockAxios.mockResponse(rs(genOrder()), submitted)
    await flushPromises()
    await nextTick()
    const refresh = mockAxios.getReqByUrl('/api/profiles/data/requester/')
    mockAxios.mockResponse(rs(genAnon()), refresh)
    await flushPromises()
    await waitFor(() => expect(router.currentRoute.value.name).toEqual('Order'))
    expect(router.currentRoute.value.params).toEqual({
      orderId: '1',
      username: '_',
    })
    expect(router.currentRoute.value.query).toEqual({
      showConfirm: 'true',
    })
  })
  test('Fetches character info', async() => {
    const user = genUser()
    setViewer(store, user)
    const form = mount(Empty, vueSetup({store})).vm.$getForm('newOrder', {
      endpoint: '/boop/',
      persistent: true,
      step: 1,
      fields: {
        productId: {value: 0},
        email: {
          value: '',
          step: 1,
          validators: [{name: 'email'}],
        },
        private: {
          value: false,
          step: 1,
        },
        characters: {
          value: [23, 50],
          step: 2,
        },
        rating: {
          value: 0,
          step: 2,
        },
        details: {
          value: '',
          step: 2,
        },
        references: {
          value: [],
          step: 2,
        },
        invoicing: {
          value: false,
          step: 3,
        },
        // Let there be a 'step 3' even if there's not an actual field there.
        dummy: {
          value: '',
          step: 3,
        },
        named_price: {
          value: null,
          step: 1,
        },
        escrow_upgrade: {
          value: false,
          step: 3,
        },
      },
    })
    wrapper = mount(
      NewOrder,
      {
        ...vueSetup({
          store,
          router,
        }),
        props: {
          productId: '1',
          username: 'Fox',
        },
      })
    const vm = wrapper.vm as any
    vm.subjectHandler.user.makeReady(genUser())
    vm.subjectHandler.artistProfile.makeReady(genArtistProfile())
    vm.product.makeReady(genProduct())
    await nextTick()
    const successfulRequest = mockAxios.getReqByUrl('/api/profiles/data/character/id/50/')
    const failedRequest = mockAxios.getReqByUrl('/api/profiles/data/character/id/23/')
    const character = genCharacter({name: 'Goof'})
    mockAxios.mockResponse(rs(genCharacter({name: 'Goof'})), successfulRequest)
    mockAxios.mockError(Error('Boop'), failedRequest)
    await flushPromises()
    await nextTick()
    expect(form.fields.characters.model).toEqual([50])
    expect(vm.initCharacters).toEqual([character])
    expect(vm.showCharacters).toBeTruthy()
  })
  test('Updates the form when the user is silently registered', async() => {
    const user = genAnon()
    setViewer(store, user)
    const form = mount(Empty, vueSetup({store})).vm.$getForm('newOrder', {
      endpoint: '/boop/',
      persistent: true,
      fields: {
        productId: {value: 0},
        email: {value: ('')},
        private: {value: false},
        characters: {value: [23, 50]},
        rating: {value: 0},
        details: {value: ''},
        invoicing: {
          value: false,
          step: 3,
        },
        references: {
          value: [],
          step: 2,
        },
        named_price: {
          value: null,
          step: 1,
        },
        escrow_upgrade: {
          value: false,
          step: 3,
        },
      },
    })
    wrapper = mount(NewOrder, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        productId: '1',
        username: 'Fox',
      },
    })
    const vm = wrapper.vm as any
    await nextTick()
    expect(form.fields.email.value).toEqual('')
    vm.viewerHandler.user.updateX({guest_email: 'boop@snoot.com'})
    await nextTick()
    expect(form.fields.email.value).toEqual('boop@snoot.com')
  })
  test('Sets the details template when starting from nothing.', async() => {
    const user = genAnon()
    setViewer(store, user)
    wrapper = mount(NewOrder, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        productId: '1',
        username: 'Fox',
      },
    })
    const vm = wrapper.vm as any
    vm.product.makeReady(genProduct({details_template: 'Beep boop'}))
    await nextTick()
    expect(vm.orderForm.fields.details.model).toEqual('Beep boop')
  })
  test('Does not set the details template when revisiting.', async() => {
    mount(Empty, vueSetup({store})).vm.$getForm('newOrder', {
      endpoint: '/boop/',
      persistent: true,
      fields: {
        productId: {value: 5},
        email: {value: ('')},
        private: {value: false},
        characters: {value: [23, 50]},
        rating: {value: 0},
        details: {value: 'This is a test.'},
        invoicing: {
          value: false,
          step: 3,
        },
        references: {
          value: [],
          step: 2,
        },
        named_price: {
          value: null,
          step: 1,
        },
        escrow_upgrade: {
          value: false,
          step: 3,
        },
      },
    })
    const user = genAnon()
    setViewer(store, user)
    wrapper = mount(NewOrder, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        productId: '1',
        username: 'Fox',
      },
    })
    const vm = wrapper.vm as any
    vm.product.makeReady(genProduct({
      id: 5,
      details_template: 'Beep boop',
    }))
    await nextTick()
    expect(vm.orderForm.fields.details.model).toEqual('This is a test.')
  })
  test('Does not set the details template when it is blank.', async() => {
    mount(Empty, vueSetup({store})).vm.$getForm('newOrder', {
      endpoint: '/boop/',
      persistent: true,
      fields: {
        productId: {value: 1},
        email: {value: ('')},
        private: {value: false},
        characters: {value: [23, 50]},
        rating: {value: 0},
        details: {value: 'This is a test.'},
        invoicing: {
          value: false,
          step: 3,
        },
        references: {
          value: [],
          step: 2,
        },
        named_price: {
          value: null,
          step: 1,
        },
        escrow_upgrade: {
          value: false,
          step: 3,
        },
      },
    })
    const user = genAnon()
    setViewer(store, user)
    wrapper = mount(NewOrder, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        productId: '1',
        username: 'Fox',
      },
    })
    const vm = wrapper.vm as any
    vm.product.makeReady(genProduct({
      id: 5,
      details_template: '',
    }))
    await nextTick()
    expect(vm.orderForm.fields.details.model).toEqual('This is a test.')
  })
  test('Sets the details template when the order ID changes.', async() => {
    mount(Empty, vueSetup({store})).vm.$getForm('newOrder', {
      endpoint: '/boop/',
      persistent: true,
      fields: {
        productId: {value: 1},
        email: {value: ('')},
        private: {value: false},
        characters: {value: [23, 50]},
        rating: {value: 0},
        details: {value: 'This is a test.'},
        invoicing: {
          value: false,
          step: 3,
        },
        references: {
          value: [],
          step: 2,
        },
        named_price: {
          value: null,
          step: 1,
        },
        escrow_upgrade: {
          value: false,
          step: 3,
        },
      },
    })
    const user = genAnon()
    setViewer(store, user)
    wrapper = mount(NewOrder, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        productId: '1',
        username: 'Fox',
      },
    })
    const vm = wrapper.vm as any
    vm.product.makeReady(genProduct({
      id: 5,
      details_template: 'Beep Boop',
    }))
    await nextTick()
    expect(vm.orderForm.fields.details.model).toEqual('Beep Boop')
  })
  test('Redirects to step one if using the old order URL', async() => {
    const user = genAnon()
    setViewer(store, user)
    await router.replace({
      name: 'NewOrder',
      params: {
        username: 'Fox',
        productId: '1',
      },
    })
    const mockReplace = vi.spyOn(router, 'replace')
    wrapper = mount(NewOrder, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        productId: '1',
        username: 'Fox',
      },
    })
    await nextTick()
    expect(mockReplace).toHaveBeenCalledWith({query: {stepId: '1'}})
  })
  test('Redirects to step one if the starting URL marks a lower number', async() => {
    const user = genAnon()
    setViewer(store, user)
    await router.replace({
      name: 'NewOrder',
      params: {
        username: 'Fox',
        productId: '1',
      },
      query: {stepId: '-1'},
    })
    const mockReplace = vi.spyOn(router, 'replace')
    wrapper = mount(NewOrder, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        productId: '1',
        username: 'Fox',
      },
    })
    const vm = wrapper.vm as any
    await nextTick()
    expect(mockReplace).toHaveBeenCalledWith({query: {stepId: '1'}})
  })
  test('Redirects to step three if the starting URL marks a higher number', async() => {
    const user = genAnon()
    setViewer(store, user)
    await router.replace({
      name: 'NewOrder',
      params: {
        username: 'Fox',
        productId: '1',
      },
      query: {stepId: '4'},
    })
    wrapper = mount(NewOrder, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        productId: '1',
        username: 'Fox',
      },
    })
    await waitFor(() => expect(router.currentRoute.value.query.stepId).toEqual('3'))
  })
  test('Does not submit if the last step is not selected.', async() => {
    const user = genAnon()
    setViewer(store, user)
    await router.replace({
      name: 'NewOrder',
      params: {
        username: 'Fox',
        productId: '1',
      },
      query: {stepId: '2'},
    })
    const mockReplace = vi.spyOn(router, 'replace')
    wrapper = mount(NewOrder, {
      ...vueSetup({
        store,
        router,
      }),
      props: {
        productId: '1',
        username: 'Fox',
      },
    })
    await nextTick()
    const vm = wrapper.vm as any
    vm.product.makeReady(genProduct())
    await nextTick()
    mockReplace.mockReset()
    const mockSubmitThen = vi.spyOn(vm.orderForm, 'submitThen')
    await waitFor(() => expect(wrapper.find('input').exists()).toBeTruthy())
    await wrapper.find('input').trigger('submit')
    await nextTick()
    expect(mockReplace).toHaveBeenCalledWith({query: {stepId: '3'}})
    expect(mockSubmitThen).not.toHaveBeenCalled()
  })
})
