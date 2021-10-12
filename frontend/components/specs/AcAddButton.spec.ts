import Vue from 'vue'
import {cleanUp, docTarget, vueSetup, mount, createVuetify} from '@/specs/helpers'
import {Wrapper} from '@vue/test-utils'
import AcAddButton from '@/components/AcAddButton.vue'
import Vuetify from 'vuetify/lib'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

describe('AcAddButton.vue', () => {
  beforeEach(() => {
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Sends an input event', async() => {
    // @ts-ignore
    const wrapper = mount(AcAddButton, {localVue, attachTo: docTarget(), vuetify})
    const mockEmit = jest.spyOn(wrapper.vm, '$emit')
    wrapper.find('.ac-add-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(mockEmit).toHaveBeenCalledWith('input', true)
  })
})
