import Vue from 'vue'
import {cleanUp, docTarget, vueSetup} from '@/specs/helpers'
import {mount, Wrapper} from '@vue/test-utils'
import AcAddButton from '@/components/AcAddButton.vue'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>

describe('AcAddButton.vue', () => {
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Sends an input event', async() => {
    const wrapper = mount(AcAddButton, {localVue, attachTo: docTarget()})
    const mockEmit = jest.spyOn(wrapper.vm, '$emit')
    wrapper.find('.ac-add-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(mockEmit).toHaveBeenCalledWith('input', true)
  })
})
