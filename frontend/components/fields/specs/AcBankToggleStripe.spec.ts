import Vue from 'vue'
import {createVuetify, vueSetup, mount, cleanUp, setViewer} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {Wrapper} from '@vue/test-utils'
import Vuetify from 'vuetify/lib'
import AcBankToggleStripe from '@/components/fields/AcBankToggleStripe.vue'
import {BANK_STATUSES} from '@/store/profiles/types/BANK_STATUSES'
import {genUser} from '@/specs/helpers/fixtures'
import StripeAccount from '@/types/StripeAccount'
import {genId} from '@/lib/lib'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

const genStripeAccount = (): StripeAccount => {
  return {active: true, country: 'US', id: genId()}
}

describe('AcBankToggleAuthorize.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Verifies if a Stripe account is needed', async() => {
    setViewer(store, genUser({username: 'Fox'}))
    wrapper = mount(AcBankToggleStripe, {
      localVue,
      store,
      vuetify,
      propsData: {username: 'Fox', value: BANK_STATUSES.NO_SUPPORTED_COUNTRY},
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
