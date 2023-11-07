import {cleanUp, mount, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {VueWrapper} from '@vue/test-utils'
import {genUser} from '@/specs/helpers/fixtures'
import TransactionHistory from '@/components/views/settings/payment/TransactionHistory.vue'
import {describe, expect, beforeEach, afterEach, test} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>

describe('AcTransaction.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Identifies the current list type', async() => {
    setViewer(store, genUser())
    wrapper = mount(TransactionHistory, {
      ...vueSetup({store}),
      props: {username: 'Fox'},
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
