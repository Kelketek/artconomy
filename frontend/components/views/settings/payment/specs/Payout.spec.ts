import Vue from 'vue'
import {Vuetify} from 'vuetify/types'
import {cleanUp, createVuetify, docTarget, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import Payout from '@/components/views/settings/payment/Payout.vue'
import {genArtistProfile, genUser} from '@/specs/helpers/fixtures'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

describe('Payout.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts', async() => {
    setViewer(store, genUser())
    wrapper = mount(Payout, {localVue, store, propsData: {username: 'Fox'}, attachTo: docTarget()})
  })
  it('Recognizes us or non-us account status', async() => {
    setViewer(store, genUser())
    wrapper = mount(Payout, {localVue, store, propsData: {username: 'Fox'}, attachTo: docTarget()})
    const vm = wrapper.vm as any
    expect(vm.nonUsAccount).toBe(null)
    vm.subjectHandler.artistProfile.setX(genArtistProfile())
    await vm.$nextTick()
    expect(vm.nonUsAccount).toBe(false)
    vm.subjectHandler.artistProfile.updateX({bank_account_status: 2})
    await vm.$nextTick()
    expect(vm.nonUsAccount).toBe(true)
  })
})
