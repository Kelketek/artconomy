import Vue from 'vue'
import AcSpeedButton from '@/components/wrappers/AcSpeedButton.vue'
import {mount, Wrapper} from '@vue/test-utils'
import Vuetify from 'vuetify/lib'
import {cleanUp, createVuetify, docTarget, vueSetup} from '@/specs/helpers'

describe('AcSpeedButton.vue', () => {
  const localVue = vueSetup()
  let vuetify: Vuetify
  let wrapper: Wrapper<Vue>
  beforeEach(() => {
    vuetify = createVuetify()
    jest.resetAllMocks()
    jest.useFakeTimers()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Toggles its tooltip', async() => {
    wrapper = mount(AcSpeedButton, {
      localVue,
      vuetify,
      propsData: {value: false, text: 'I am a label'},

      attachTo: docTarget(),
    })
    const vm = wrapper.vm as any
    expect(vm.showTooltip).toBe(false)
    expect(wrapper.text()).toEqual('I am a label')
    wrapper.setProps({value: true, text: 'I am a label, too'})
    await vm.$nextTick()
    await jest.runAllTimers()
    expect(wrapper.text()).toEqual('I am a label, too')
    expect(vm.showTooltip).toBe(true)
    wrapper.setProps({value: false, text: 'I am a label, too'})
    await vm.$nextTick()
    expect(vm.showTooltip).toBe(false)
  })
})
