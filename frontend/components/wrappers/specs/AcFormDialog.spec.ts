import {mount} from '@vue/test-utils'
import FormDialogContainer from '../../../specs/helpers/dummy_components/form-dialog-container.vue'
import {Vuetify} from 'vuetify/types'
import {createVuetify, vueSetup} from '@/specs/helpers'

const localVue = vueSetup()
let vuetify: Vuetify

describe('ac-form-dialog.vue', () => {
  beforeEach(() => {
    vuetify = createVuetify()
  })
  it('Handles model toggle', async() => {
    // Needed for that last bit of code coverage.
    const wrapper = mount(FormDialogContainer, {
      localVue,
      vuetify,
    })
    expect((wrapper.vm as any).expanded).toBe(false);
    (wrapper.vm as any).expanded = true
    await wrapper.vm.$nextTick()
    wrapper.find('.dialog-closer').trigger('click')
    expect((wrapper.vm as any).expanded).toEqual(false)
  })
})
