import {VueWrapper} from '@vue/test-utils'
import AcConfirmation from '../AcConfirmation.vue'
import {mount, vueSetup, VuetifyWrapped, confirmAction} from '@/specs/helpers'
import {describe, beforeEach, expect, test, vi} from 'vitest'

let wrapper: VueWrapper<any>

const WrappedConfirmation = VuetifyWrapped(AcConfirmation)

describe('AcConfirmation.vue', () => {
  test('Calls the action when sending', async() => {
    const action = vi.fn()
    action.mockImplementation(() => new Promise<void>((resolve) => {
      resolve()
    }))
    wrapper = mount(WrappedConfirmation, {
      ...vueSetup(),
      props: {action},
    })
    expect(wrapper.find('.v-dialog').exists()).toBe(false)
    await confirmAction(wrapper, ['.confirm-launch'])
    expect(action).toHaveBeenCalled()
    expect(wrapper.find('.v-dialog .v-dialog--active').exists()).toBe(false)
  })
})
