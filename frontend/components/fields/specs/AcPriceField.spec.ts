import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import AcPriceField from '@/components/fields/AcPriceField.vue'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>

describe('AcPriceField.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Creates a field based on a field controller', async() => {
    wrapper = mount(AcPriceField, {
        ...vueSetup({store}),
        props: {modelValue: 1},
      },
    )
    const vm = wrapper.vm as any
    await vm.$nextTick()
    const input = wrapper.find('.price-input input')
    await input.trigger('focus')
    await input.setValue('10')
    await vm.$nextTick()
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['10'])
    await wrapper.setProps({modelValue: '10'})
    await wrapper.find('.price-input input').trigger('blur')
    await vm.$nextTick()
    await vm.$nextTick()
    expect(wrapper.emitted('update:modelValue')![1]).toEqual(['10.00'])
  })
})
