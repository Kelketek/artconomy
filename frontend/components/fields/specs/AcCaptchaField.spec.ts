import {Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import {ArtStore, createStore} from '@/store'
import {cleanUp, qMount, vueSetup} from '@/specs/helpers'
import AcCaptchaField from '@/components/fields/AcCaptchaField.vue'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>

describe('AcCaptchaField.vue', () => {
  beforeEach(() => {
    store = createStore()
    jest.useFakeTimers()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Handles a verification event.', async() => {
    wrapper = qMount(AcCaptchaField, {localVue, store, propsData: {value: null}, stubs: {VueHcaptcha: true}})
    const vm = wrapper.vm as any
    vm.$refs.recaptcha.$emit('verify', 'beep')
    await vm.$nextTick()
    expect(wrapper.emitted().input).toBeTruthy()
    expect(wrapper.emitted().input!.length).toBe(1)
    expect(wrapper.emitted().input![0]).toEqual(['beep'])
  })
  it('Handles expiration.', async() => {
    wrapper = qMount(AcCaptchaField, {localVue, store, propsData: {value: null}, stubs: {VueHcaptcha: true}})
    const vm = wrapper.vm as any
    vm.$refs.recaptcha.$emit('expired')
    await vm.$nextTick()
    expect(wrapper.emitted().input).toBeTruthy()
    expect(wrapper.emitted().input!.length).toBe(1)
    expect(wrapper.emitted().input![0]).toEqual([''])
  })
})
