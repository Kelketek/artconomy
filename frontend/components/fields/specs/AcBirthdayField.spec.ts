import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import {cleanUp, mount, vueSetup, VuetifyWrapped} from '@/specs/helpers'
import AcBirthdayField from '@/components/fields/AcBirthdayField.vue'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'
import {parseISO} from 'date-fns'

let store: ArtStore
let wrapper: VueWrapper<any>

describe('AcBirthdayField.vue', () => {
  beforeEach(() => {
    store = createStore()
    vi.useFakeTimers()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Creates a datepicker in year mode by default.', async() => {
    wrapper = mount(VuetifyWrapped(AcBirthdayField), {
      ...vueSetup({store}),
      props: {modelValue: null},
    })
    const vm = wrapper.vm.$refs.vm as any
    await vm.$nextTick()
    vm.menu = true
    await vm.$nextTick()
    vi.runAllTimers()
    await vm.$nextTick()
    expect(vm.$refs.picker.viewMode).toBe('year')
  })
  test('Sends an updated value.', async() => {
    wrapper = mount(AcBirthdayField, {
      ...vueSetup({store}),
      props: {modelValue: null},
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    vm.converted = parseISO('1988-08-01')
    await vm.$nextTick()
    expect(wrapper.emitted('update:modelValue')).toHaveLength(1)
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['1988-08-01'])
  })
})
