import {createLocalVue, mount} from '@vue/test-utils'
import FormattedComponent from '@/specs/helpers/dummy_components/formatting.vue'

describe('formatting.ts', () => {
  const localVue = createLocalVue()
  it('Mounts', () => {
    const wrapper = mount(FormattedComponent, {localVue})
    expect((wrapper.vm as any).nameCheck).toBe(true)
  })
})
