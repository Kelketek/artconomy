import Vue from 'vue'
import AcSpeedButton from '@/components/wrappers/AcSpeedButton.vue'
import {createLocalVue, mount} from '@vue/test-utils'
import Vuetify from 'vuetify'
import {vuetifySetup} from '@/specs/helpers'

Vue.use(Vuetify)

describe('AcSpeedButton.vue', () => {
  const localVue = createLocalVue()
  beforeEach(() => {
    vuetifySetup()
    jest.resetAllMocks()
    jest.useFakeTimers()
  })
  it('Toggles its tooltip', async() => {
    const wrapper = mount(AcSpeedButton, {localVue, propsData: {value: false, text: 'I am a label'}})
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
