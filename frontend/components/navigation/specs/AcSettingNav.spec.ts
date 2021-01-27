import Vue from 'vue'
import AcSettingNav from '@/components/navigation/AcSettingNav.vue'
import {Wrapper} from '@vue/test-utils'
import Vuetify from 'vuetify/lib'
import {ArtStore, createStore} from '@/store'
import {genArtistProfile, genUser} from '@/specs/helpers/fixtures'
import {BankStatus} from '@/store/profiles/types/BankStatus'
import {cleanUp, createVuetify, vueSetup, mount} from '@/specs/helpers'

const localVue = vueSetup()
let store: ArtStore
let vuetify: Vuetify
let wrapper: Wrapper<Vue>

describe('AcSettingNav.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Shows artist panel when artist mode is on', async() => {
    const wrapper = mount(
      AcSettingNav, {
        localVue,
        store,
        vuetify,
        stubs: ['router-link'],
        propsData: {username: 'Fox'},
      },
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
        vuetify,
        stubs: ['router-link'],
        propsData: {username: 'Fox'},
      },
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
        vuetify,
        stubs: ['router-link'],
        propsData: {username: 'Fox'},
      },
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
