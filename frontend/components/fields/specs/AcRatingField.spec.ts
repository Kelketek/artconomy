import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import AcRatingField from '@/components/fields/AcRatingField.vue'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>

describe('AcRatingField.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Creates a field based on a field controller', async() => {
    wrapper = mount(AcRatingField, {
      ...vueSetup({store}),
      props: {modelValue: 1, label: 'Beep'},
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    vm.scratch = 2
    await vm.$nextTick()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual([2])
  })
})
