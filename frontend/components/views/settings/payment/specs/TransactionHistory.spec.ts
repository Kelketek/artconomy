import Vue from 'vue'
import {cleanUp, createVuetify, docTarget, setViewer, vueSetup, mount} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {Wrapper} from '@vue/test-utils'
import {genUser} from '@/specs/helpers/fixtures'
import TransactionHistory from '@/components/views/settings/payment/TransactionHistory.vue'
import Vuetify from 'vuetify/lib'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

describe('AcTransaction.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Identifies the current list type', async() => {
    setViewer(store, genUser())
    wrapper = mount(TransactionHistory, {
      localVue,
      store,
      vuetify,
      propsData: {username: 'Fox'},
      attachTo: docTarget(),
    })
    const vm = wrapper.vm as any
    expect(vm.transactionFilter.fields.account.value).toBe(300)
    expect(vm.purchaseList).toBe(true)
    expect(vm.escrowList).toBe(false)
    vm.transactionFilter.fields.account.update(302)
    await vm.$nextTick()
    expect(vm.purchaseList).toBe(false)
    expect(vm.escrowList).toBe(true)
  })
})
