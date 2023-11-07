import {mount} from '@vue/test-utils'
import FormattedComponent from '@/specs/helpers/dummy_components/formatting.vue'
import {describe, expect, test} from 'vitest'
import {vueSetup} from '@/specs/helpers'

describe('formatting.ts', () => {
  test('Mounts', () => {
    const wrapper = mount(FormattedComponent, vueSetup())
    expect((wrapper.vm as any).nameCheck).toBe(true)
  })
})
