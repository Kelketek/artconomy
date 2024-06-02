import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import AcBirthdayField from '@/components/fields/AcBirthdayField.vue'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'
import {parseISO} from 'date-fns'
import {nextTick} from 'vue'

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
    wrapper = mount(AcBirthdayField, {
      ...vueSetup({store}),
      props: {modelValue: null},
    })
    await nextTick()
    wrapper.vm.menu = true
    await nextTick()
    vi.runAllTimers()
    await nextTick()
    expect(wrapper.vm.activePicker).toBe('year')
  })
  test('Sends an updated value.', async() => {
    wrapper = mount(AcBirthdayField, {
      ...vueSetup({store}),
      props: {modelValue: null},
    })
    const vm = wrapper.vm as any
    await nextTick()
    vm.converted = parseISO('1988-08-01')
    await nextTick()
    expect(wrapper.emitted('update:modelValue')).toHaveLength(1)
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['1988-08-01'])
  })
})
