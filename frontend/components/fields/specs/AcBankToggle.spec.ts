import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {VueWrapper} from '@vue/test-utils'
import AcBankToggleStripe from '@/components/fields/AcBankToggle.vue'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {genId, setViewer} from '@/lib/lib.ts'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'
import type {StripeAccount} from '@/types/main'
import {BankStatus} from '@/store/profiles/types/enums.ts'

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
    setViewer({ store, user: genUser({ username: 'Fox' }) })
    wrapper = mount(AcBankToggleStripe, {
      ...vueSetup({store}),
      props: {
        username: 'Fox',
        modelValue: BankStatus.NO_SUPPORTED_COUNTRY,
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
