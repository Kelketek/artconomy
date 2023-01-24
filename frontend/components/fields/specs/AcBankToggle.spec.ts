import Vue from 'vue'
import {createVuetify, vueSetup, mount, cleanUp, setViewer} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {Wrapper} from '@vue/test-utils'
import Vuetify from 'vuetify/lib'
import AcBankToggle from '@/components/fields/AcBankToggle.vue'
import {SHIELD_STATUSES} from '@/store/profiles/types/SHIELD_STATUSES'
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

describe('AcBankToggle.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Verifies if a Stripe account is needed', async() => {
    setViewer(store, genUser({username: 'Fox'}))
    wrapper = mount(AcBankToggle, {
      localVue,
      store,
      vuetify,
      propsData: {username: 'Fox', value: SHIELD_STATUSES.SHIELD_DISABLED},
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
