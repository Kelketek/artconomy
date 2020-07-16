import {ArtStore, createStore} from '@/store'
import {createVuetify, vueSetup} from '@/specs/helpers'
import {Vuetify} from 'vuetify'
import {mount} from '@vue/test-utils'
import OrderList from '@/components/views/orders/OrderList.vue'

let store: ArtStore
let vuetify: Vuetify
const localVue = vueSetup()

describe('OrderList.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  it('Recognizes when it is on the waiting list page.', async() => {
    const wrapper = mount(OrderList, {
      localVue,
      vuetify,
      store,
      propsData: {
        type: 'sales',
        category: 'waiting',
        username: 'Fox',
      },
    })
    const vm = wrapper.vm as any
    expect(vm.salesWaiting).toBe(true)
    wrapper.setProps({category: 'current'})
    await vm.$nextTick()
    expect(vm.salesWaiting).toBe(false)
    wrapper.setProps({category: 'orders'})
    await vm.$nextTick()
    expect(vm.salesWaiting).toBe(false)
  })
})
