import {cleanUp, mount, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {VueWrapper} from '@vue/test-utils'
import AcBankToggleStripe from '@/components/fields/AcBankToggle.vue'
import {BANK_STATUSES} from '@/store/profiles/types/BANK_STATUSES'
import {genUser} from '@/specs/helpers/fixtures'
import StripeAccount from '@/types/StripeAccount'
import {genId} from '@/lib/lib'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>

const genStripeAccount = (): StripeAccount => {
  return {
    active: true,
    country: 'US',
    id: genId(),
  }
}

describe('AcBankToggle.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Verifies if a Stripe account is needed', async() => {
    setViewer(store, genUser({username: 'Fox'}))
    wrapper = mount(AcBankToggleStripe, {
      ...vueSetup({store}),
      props: {
        username: 'Fox',
        modelValue: BANK_STATUSES.NO_SUPPORTED_COUNTRY,
      },
    })
    const vm = wrapper.vm as any
    vm.stripeAccounts.makeReady([])
    expect(vm.needStripe).toBe(true)
    expect(vm.hasActiveStripe).toBe(false)
    vm.stripeAccounts.setList([genStripeAccount()])
    await vm.$nextTick()
    expect(vm.stripeSetupForm.fields.country.value).toBe('US')
    expect(vm.needStripe).toBe(false)
    expect(vm.hasActiveStripe).toBe(true)
    // Make sure the trigger for populating the country doesn't break when we drop this account, and that other stuff
    // still works too.
    vm.stripeAccounts.setList([])
    expect(vm.needStripe).toBe(true)
    expect(vm.hasActiveStripe).toBe(false)
  })
})
