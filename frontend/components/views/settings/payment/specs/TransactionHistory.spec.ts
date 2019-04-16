import Vue from 'vue'
import {cleanUp, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import {genUser} from '@/specs/helpers/fixtures'
import TransactionHistory from '@/components/views/settings/payment/TransactionHistory.vue'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>

describe('AcTransaction.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
    cleanUp()
  })
  it('Identifies the current list type', async() => {
    setViewer(store, genUser())
    wrapper = mount(TransactionHistory, {
      localVue,
      store,
      propsData: {username: 'Fox'},
      sync: false,
      attachToDocument: true,
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
