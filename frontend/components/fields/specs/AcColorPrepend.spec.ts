import {mount, vueSetup} from '@/specs/helpers'
import AcColorPrepend from '@/components/fields/AcColorPrepend.vue'
import {describe, expect, test, vi} from 'vitest'

describe('AcColorPrepend.vue', () => {
  test('Mounts', () => {
    const wrapper = mount(AcColorPrepend, vueSetup())
    const input = wrapper.find('.picker').element as HTMLInputElement
    const mockClick = vi.fn()
    input.onclick = mockClick
    wrapper.find('.picker-button').trigger('click')
    expect(mockClick).toHaveBeenCalled()
  })
})
