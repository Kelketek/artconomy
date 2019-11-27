import {mount, Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import {ArtStore, createStore} from '@/store'
import {cleanUp, vueSetup, vuetifySetup} from '@/specs/helpers'
import AcPriceField from '@/components/fields/AcPriceField.vue'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>

describe('AcPriceField.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetifySetup()
  })
  afterEach(() => {
    cleanUp()
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Creates a field based on a field controller', async() => {
    wrapper = mount(AcPriceField, {
      localVue, store, sync: false, attachToDocument: true, propsData: {value: 1}}
    )
    const vm = wrapper.vm as any
    await vm.$nextTick()
    const mockEmit = jest.spyOn(vm, '$emit')
    const input = wrapper.find('.price-input input')
    input.trigger('focus')
    input.setValue('10')
    await vm.$nextTick()
    expect(mockEmit).toHaveBeenCalledWith('input', '10')
    wrapper.setProps({value: '10'})
    wrapper.find('.price-input input').trigger('blur')
    await vm.$nextTick()
    await vm.$nextTick()
    expect(mockEmit).toHaveBeenCalledWith('input', '10.00')
  })
})
