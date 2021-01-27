import {Wrapper} from '@vue/test-utils'
import AcConfirmation from '../AcConfirmation.vue'
import {createVuetify, docTarget, vueSetup, mount} from '@/specs/helpers'
import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import flushPromises from 'flush-promises'

const localVue = vueSetup()
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

describe('ac-confirmation.vue', () => {
  beforeEach(() => {
    vuetify = createVuetify()
  })
  it('Asks for confirmation', async() => {
    const action = jest.fn()
    // Needed for that last bit of code coverage.
    wrapper = mount(AcConfirmation, {
      localVue,
      vuetify,
      propsData: {action},

      attachTo: docTarget(),
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
      vuetify,
      propsData: {action},

      attachTo: docTarget(),
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
      localVue,
      vuetify,
      propsData: {action},

      attachTo: docTarget(),
    });
    (wrapper.vm as any).showModal = true
    await wrapper.vm.$nextTick()
    wrapper.find('.confirmation-button').trigger('click')
    await wrapper.vm.$nextTick()
    await flushPromises()
    expect(wrapper.find('.v-dialog .v-dialog--active').exists()).toBe(false)
  })
})
