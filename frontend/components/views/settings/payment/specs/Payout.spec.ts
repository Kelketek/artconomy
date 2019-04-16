import Vue from 'vue'
import {setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {singleRegistry} from '@/store/singles/registry'
import {listRegistry} from '@/store/lists/registry'
import {profileRegistry} from '@/store/profiles/registry'
import {mount, Wrapper} from '@vue/test-utils'
import Payout from '@/components/views/settings/payment/Payout.vue'
import {genArtistProfile, genUser} from '@/specs/helpers/fixtures'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>

describe('Payout.vue', () => {
  beforeEach(() => {
    store = createStore()
    singleRegistry.reset()
    listRegistry.reset()
    profileRegistry.reset()
  })
  afterEach(() => {
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Mounts', async() => {
    setViewer(store, genUser())
    wrapper = mount(Payout, {localVue, store, propsData: {username: 'Fox'}, sync: false, attachToDocument: true})
  })
  it('Recognizes us or non-us account status', async() => {
    setViewer(store, genUser())
    wrapper = mount(Payout, {localVue, store, propsData: {username: 'Fox'}, sync: false, attachToDocument: true})
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
