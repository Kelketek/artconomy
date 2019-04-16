import {createLocalVue, mount} from '@vue/test-utils'
import AcLoadingSpinner from '../AcLoadingSpinner.vue'
import Vue from 'vue'
import Vuetify from 'vuetify'

// Must use it directly, due to issues with package imports upstream.
Vue.use(Vuetify)
const localVue = createLocalVue()

describe('ac-form-container.vue', () => {
  it('Shows a loading spinner', async() => {
    // Needed for that last bit of code coverage.
    const wrapper = mount(AcLoadingSpinner, {
      localVue,
    })
    expect(wrapper.find('.v-progress-circular').exists()).toBe(true)
  })
})
