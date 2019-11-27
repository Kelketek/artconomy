import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import AcConfirmation from '../AcConfirmation.vue'
import {vuetifySetup} from '@/specs/helpers'
import Vue, {VueConstructor} from 'vue'
import Vuetify from 'vuetify'
import flushPromises from 'flush-promises'

Vue.use(Vuetify)
let localVue: VueConstructor
let wrapper: Wrapper<Vue>

describe('ac-confirmation.vue', () => {
  beforeEach(() => {
    localVue = createLocalVue()
    vuetifySetup()
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Asks for confirmation', async() => {
    const action = jest.fn()
    // Needed for that last bit of code coverage.
    wrapper = mount(AcConfirmation, {
      localVue,
      propsData: {action},
      sync: false,
      attachToDocument: true,
    })
    expect(wrapper.find('.v-dialog--active').exists()).toBe(false)
    wrapper.find('.confirm-launch').trigger('click')
    await wrapper.vm.$nextTick()
    expect(wrapper.find('.v-dialog--active').exists()).toBe(true)
  })
  it('Calls the action when sending', async() => {
    const action = jest.fn()
    action.mockImplementation(() => new Promise((resolve) => {
      resolve()
    }))
    // Needed for that last bit of code coverage.
    wrapper = mount(AcConfirmation, {
      localVue,
      propsData: {action},
      sync: false,
      attachToDocument: true,
    });
    (wrapper.vm as any).showModal = true
    await wrapper.vm.$nextTick()
    wrapper.find('.confirmation-button').trigger('click')
    await wrapper.vm.$nextTick()
    expect(action).toHaveBeenCalled()
  })
  it('Closes the dialog when finished sending', async() => {
    const action = jest.fn()
    action.mockImplementation(() => new Promise((resolve) => {
      resolve()
    }))
    // Needed for that last bit of code coverage.
    wrapper = mount(AcConfirmation, {
      localVue, propsData: {action}, sync: false, attachToDocument: true,
    });
    (wrapper.vm as any).showModal = true
    await wrapper.vm.$nextTick()
    wrapper.find('.confirmation-button').trigger('click')
    await wrapper.vm.$nextTick()
    await flushPromises()
    expect(wrapper.find('.v-dialog .v-dialog--active').exists()).toBe(false)
  })
})
