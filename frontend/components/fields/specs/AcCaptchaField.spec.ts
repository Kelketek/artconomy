import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import {cleanUp, mount, vueSetup} from '@/specs/helpers'
import AcCaptchaField from '@/components/fields/AcCaptchaField.vue'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>

describe('AcCaptchaField.vue', () => {
  beforeEach(() => {
    store = createStore()
    vi.useFakeTimers()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Handles a verification event.', async() => {
    wrapper = mount(AcCaptchaField, {
      ...vueSetup({
        store,
        stubs: ['vue-hcaptcha'],
      }),
      props: {value: null},
    })
    const vm = wrapper.vm as any
    vm.$refs.recaptcha.$emit('verify', 'beep')
    await vm.$nextTick()
    expect(wrapper.emitted()['update:modelValue']).toBeTruthy()
    expect(wrapper.emitted()['update:modelValue']!.length).toBe(1)
    expect(wrapper.emitted()['update:modelValue']![0]).toEqual(['beep'])
  })
  test('Handles expiration.', async() => {
    wrapper = mount(AcCaptchaField, {
      ...vueSetup({
        store,
        stubs: ['vue-hcaptcha'],
      }),
      props: {value: null},
    })
    const vm = wrapper.vm as any
    vm.$refs.recaptcha.$emit('expired')
    await vm.$nextTick()
    expect(wrapper.emitted()['update:modelValue']).toBeTruthy()
    expect(wrapper.emitted()['update:modelValue']!.length).toBe(1)
    expect(wrapper.emitted()['update:modelValue']![0]).toEqual([''])
  })
})
