import Vue from 'vue'
import {createLocalVue, mount} from '@vue/test-utils'
import FormDialogContainer from '../../../specs/helpers/dummy_components/form-dialog-container.vue'
import Vuetify from 'vuetify'
import {vuetifySetup} from '@/specs/helpers'

// Must use it directly, due to issues with package imports upstream.
Vue.use(Vuetify)
const localVue = createLocalVue()

describe('ac-form-dialog.vue', () => {
  beforeEach(() => {
    vuetifySetup()
  })
  it('Handles model toggle', async() => {
    // Needed for that last bit of code coverage.
    const wrapper = mount(FormDialogContainer, {
      localVue,
    })
    expect((wrapper.vm as any).expanded).toBe(false);
    (wrapper.vm as any).expanded = true
    await wrapper.vm.$nextTick()
    wrapper.find('.dialog-closer').trigger('click')
    expect((wrapper.vm as any).expanded).toEqual(false)
  })
})
