import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {cleanUp, mount, setViewer, vueSetup} from '@/specs/helpers/index.ts'
import Options from '../Options.vue'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

vi.useFakeTimers()

describe('Options.vue', () => {
  let store: ArtStore
  let wrapper: VueWrapper<any>
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Mounts the options page', async() => {
    setViewer(store, genUser())
    wrapper = mount(Options, {
      ...vueSetup({store}),
      props: {username: 'Fox'},
    })
    await wrapper.vm.$nextTick()
  })
  test('Conditionally permits the rating to be adjusted', async() => {
    setViewer(store, genUser({
      birthday: null,
      username: 'Fox',
    }))
    wrapper = mount(Options, {
      ...vueSetup({store}),
      props: {username: 'Fox'},
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(vm.adultAllowed).toBe(false)
    vm.subjectHandler.user.updateX({birthday: '1988-08-01'})
    await vm.$nextTick()
    expect(vm.adultAllowed).toBe(true)
    vm.subjectHandler.user.updateX({sfw_mode: true})
    await vm.$nextTick()
    expect(vm.adultAllowed).toBe(false)
  })
  test('Reopens the cookie dialog', async() => {
    setViewer(store, genUser({
      birthday: null,
      username: 'Fox',
    }))
    wrapper = mount(Options, {
      ...vueSetup({store}),
      props: {username: 'Fox'},
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(store.state.showCookieDialog).toBe(false)
    await wrapper.find('.cookie-settings-button').trigger('click')
    await vm.$nextTick()
    expect(store.state.showCookieDialog).toBe(true)
  })
})
