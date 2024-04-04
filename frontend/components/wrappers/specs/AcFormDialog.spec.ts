import FormDialogContainer from '../../../specs/helpers/dummy_components/form-dialog-container.vue'
import {mount, vueSetup} from '@/specs/helpers/index.ts'
import {describe, expect, test} from 'vitest'
import {nextTick} from 'vue'
import {VCard} from 'vuetify/components'

describe('AcFormDialog.vue', () => {
  test('Handles model toggle', async() => {
    // Needed for that last bit of code coverage.
    const wrapper = mount(FormDialogContainer, vueSetup())
    await nextTick()
    expect((wrapper.vm as any).expanded).toBe(false);
    (wrapper.vm as any).expanded = true
    await wrapper.vm.$nextTick()
    await wrapper.findComponent(VCard).find('.dialog-closer').trigger('click')
    expect((wrapper.vm as any).expanded).toEqual(false)
  })
})
