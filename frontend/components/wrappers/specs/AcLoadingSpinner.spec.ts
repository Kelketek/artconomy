import {VueWrapper} from '@vue/test-utils'
import AcLoadingSpinner from '../AcLoadingSpinner.vue'
import {cleanUp, mount, vueSetup} from '@/specs/helpers'
import {describe, expect, afterEach, test} from 'vitest'

let wrapper: VueWrapper<any>

describe('ac-form-container.vue', () => {
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Shows a loading spinner', async() => {
    // Needed for that last bit of code coverage.
    wrapper = mount(AcLoadingSpinner, vueSetup())
    expect(wrapper.find('.v-progress-circular').exists()).toBe(true)
  })
})
