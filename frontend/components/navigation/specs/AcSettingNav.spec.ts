import AcSettingNav from '@/components/navigation/AcSettingNav.vue'
import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import {genArtistProfile, genUser} from '@/specs/helpers/fixtures.ts'
import {BANK_STATUSES} from '@/store/profiles/types/BANK_STATUSES.ts'
import {cleanUp, createVuetify, mount, vueSetup} from '@/specs/helpers/index.ts'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>

describe('AcSettingNav.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Shows artist panel when artist mode is on', async() => {
    const wrapper = mount(
      AcSettingNav, {
        ...vueSetup({
          store,
          stubs: ['router-link'],
        }),
        props: {username: 'Fox'},
      },
    )
    const vm = wrapper.vm as any
    vm.subjectHandler.user.setX(genUser())
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.artist-panel-link').exists()).toBe(true)
  })
  test('Hides artist panel when artist mode is off', async() => {
    const wrapper = mount(
      AcSettingNav, {
        ...vueSetup({
          store,
          stubs: ['router-link'],
        }),
        props: {username: 'Fox'},
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
  test('Shows payout panel if banking is configured, even if not an artist', async() => {
    const wrapper = mount(
      AcSettingNav, {
        ...vueSetup({
          store,
          stubs: ['router-link'],
        }),
        props: {username: 'Fox'},
      },
    )
    const vm = wrapper.vm as any
    const user = genUser()
    user.artist_mode = false
    vm.subjectHandler.user.setX(user)
    const profile = genArtistProfile()
    profile.bank_account_status = 1 as BANK_STATUSES
    vm.subjectHandler.artistProfile.setX(profile)
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.payout-link').exists()).toBe(true)
  })
})
