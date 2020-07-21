import Vue from 'vue'
import {Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import VueRouter from 'vue-router'
import {genUser} from '@/specs/helpers/fixtures'
import {cleanUp, qMount, setViewer, vueSetup} from '@/specs/helpers'
import Options from '../Options.vue'

jest.useFakeTimers()

describe('Options.vue', () => {
  let store: ArtStore
  let wrapper: Wrapper<Vue>
  const localVue = vueSetup()
  beforeEach(() => {
    store = createStore()
    localVue.use(VueRouter)
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts the options page', async() => {
    setViewer(store, genUser())
    wrapper = qMount(Options, {
      localVue,
      store,
      propsData: {username: 'Fox'},
    })
    await wrapper.vm.$nextTick()
  })
  it('Conditionally permits the rating to be adjusted', async() => {
    setViewer(store, genUser({birthday: null, username: 'Fox'}))
    wrapper = qMount(Options, {
      localVue,
      store,
      propsData: {username: 'Fox'},
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
})
