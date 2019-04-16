import AcSettingNav from '@/components/navigation/AcSettingNav.vue'
import {createLocalVue, mount} from '@vue/test-utils'
import Vue from 'vue'
import Vuex from 'vuex'
import Vuetify from 'vuetify'
import {ArtStore, createStore} from '@/store'
import {profileRegistry, Profiles} from '@/store/profiles/registry'
import {singleRegistry, Singles} from '@/store/singles/registry'
import {genArtistProfile, genUser} from '@/specs/helpers/fixtures'
import {BankStatus} from '@/store/profiles/types/BankStatus'
import {Lists} from '@/store/lists/registry'

Vue.use(Vuex)
Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.use(Singles)
localVue.use(Lists)
localVue.use(Profiles)
let store: ArtStore

describe('AcSettingNav.vue', () => {
  beforeEach(() => {
    store = createStore()
    profileRegistry.reset()
    singleRegistry.reset()
  })
  it('Shows artist panel when artist mode is on', async() => {
    const wrapper = mount(
      AcSettingNav, {
        localVue,
        store,
        stubs: ['router-link'],
        propsData: {username: 'Fox'}}
    )
    const vm = wrapper.vm as any
    vm.subjectHandler.user.setX(genUser())
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.artist-panel-link').exists()).toBe(true)
  })
  it('Hides artist panel when artist mode is off', async() => {
    const wrapper = mount(
      AcSettingNav, {
        localVue,
        store,
        stubs: ['router-link'],
        propsData: {username: 'Fox'}}
    )
    const vm = wrapper.vm as any
    const user = genUser()
    user.artist_mode = false
    vm.subjectHandler.user.setX(user)
    vm.subjectHandler.artistProfile.setX(genArtistProfile())
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.artist-panel-link').exists()).toBe(false)
    expect(wrapper.find('.payout-link').exists()).toBe(false)
  })
  it('Shows payout panel if banking is configured, even if not an artist', async() => {
    const wrapper = mount(
      AcSettingNav, {
        localVue,
        store,
        stubs: ['router-link'],
        propsData: {username: 'Fox'}}
    )
    const vm = wrapper.vm as any
    const user = genUser()
    user.artist_mode = false
    vm.subjectHandler.user.setX(user)
    const profile = genArtistProfile()
    profile.bank_account_status = 1 as BankStatus
    vm.subjectHandler.artistProfile.setX(profile)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.payout-link').exists()).toBe(true)
  })
})
