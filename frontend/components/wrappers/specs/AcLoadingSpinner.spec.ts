import {mount, Wrapper} from '@vue/test-utils'
import AcLoadingSpinner from '../AcLoadingSpinner.vue'
import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import {cleanUp, createVuetify, docTarget, vueSetup} from '@/specs/helpers'

// Must use it directly, due to issues with package imports upstream.
const localVue = vueSetup()
let vuetify: Vuetify
let wrapper: Wrapper<Vue>

describe('ac-form-container.vue', () => {
  beforeEach(() => {
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Shows a loading spinner', async() => {
    // Needed for that last bit of code coverage.
    wrapper = mount(AcLoadingSpinner, {
      localVue,
      vuetify,

      attachTo: docTarget(),
    })
    expect(wrapper.find('.v-progress-circular').exists()).toBe(true)
  })
})
