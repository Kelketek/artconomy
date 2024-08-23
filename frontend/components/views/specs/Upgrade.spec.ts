import Upgrade from '@/components/views/Upgrade.vue'
import {cleanUp, vueSetup, waitFor} from '@/specs/helpers'
import {describe, beforeEach, afterEach, it, expect} from 'vitest'
import {ArtStore, createStore} from '@/store'
import {genPricing} from '@/lib/specs/helpers.ts'
import {mount, VueWrapper} from '@vue/test-utils'
import {nextTick} from 'vue'
import Pricing from '@/types/Pricing.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {setViewer} from '@/lib/lib.ts'
import mockAxios from '@/specs/helpers/mock-axios.ts'

let store: ArtStore
let wrapper: VueWrapper<any>
let pricing: Pricing

describe("Upgrade.vue", () => {
  beforeEach(() => {
    store = createStore()
    pricing = genPricing()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Loads a set of plans', async () => {
    const user = genUser()
    setViewer(store, user)
    wrapper = mount(Upgrade, {...vueSetup({store}), props: {username: user.username}})
    wrapper.vm.pricing.makeReady(genPricing())
    await nextTick()
    expect(pricing.plans.length).toBeTruthy()
    expect(wrapper.findAll('.plan-column').length).toBe(pricing.plans.length)
    for (const plan of pricing.plans) {
      expect(wrapper.find(`#plan-${plan.name}-column`).exists()).toBe(true)
    }
  })
  it('Discovers the current free plan', async () => {
    const user = genUser({service_plan: 'Basic', next_service_plan: 'Free'})
    setViewer(store, user)
    wrapper = mount(Upgrade, {...vueSetup({store}), props: {username: user.username}})
    wrapper.vm.pricing.makeReady(genPricing())
    await nextTick()
    expect(wrapper.find('#plan-Free-column .current-plan-indicator').exists()).toBe(true)
    expect(wrapper.findAll('.current-plan-indicator').length).toBe(1)
  })
  it('Discovers the current monthly fee plan', async () => {
    const user = genUser({service_plan: 'Free', next_service_plan: 'Landscape'})
    setViewer(store, user)
    wrapper = mount(Upgrade, {...vueSetup({store}), props: {username: user.username}})
    wrapper.vm.pricing.makeReady(genPricing())
    await nextTick()
    expect(wrapper.findAll('.current-plan-indicator').length).toBe(0)
    expect(wrapper.find('#plan-Landscape-column .manage-plan-button').exists()).toBe(true)
  })
  it('Prepares for a plan with tracking fees but no monthly charge', async () => {
    const user = genUser({username: 'Fox', service_plan: 'Free', next_service_plan: 'Free'})
    setViewer(store, user)
    wrapper = mount(Upgrade, {...vueSetup({store}), props: {username: user.username}})
    wrapper.vm.pricing.makeReady(genPricing())
    await nextTick()
    mockAxios.reset()
    await wrapper.find('#plan-Basic-column .select-plan-button').trigger('click')
    await waitFor(() => expect(mockAxios.getReqByUrl('/api/sales/account/Fox/cards/setup-intent/')).toBeTruthy())
    expect(mockAxios.getReqByUrl('/api/sales/account/Fox/premium/intent/')).toBeFalsy()
  })
  it('Prepares for a plan with a monthly charge', async () => {
    const user = genUser({username: 'Fox', service_plan: 'Free', next_service_plan: 'Free'})
    setViewer(store, user)
    wrapper = mount(Upgrade, {...vueSetup({store}), props: {username: user.username}})
    wrapper.vm.pricing.makeReady(genPricing())
    await nextTick()
    mockAxios.reset()
    await wrapper.find('#plan-Landscape-column .select-plan-button').trigger('click')
    await waitFor(() => expect(mockAxios.getReqByUrl('/api/sales/account/Fox/premium/intent/')).toBeTruthy())
    expect(mockAxios.getReqByUrl('/api/sales/account/Fox/cards/setup-intent/')).toBeFalsy()
  })
})
