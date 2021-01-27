import {cleanUp, qMount, mount} from '@/specs/helpers'
import {Wrapper} from '@vue/test-utils'
import AcReference from '@/components/views/order/deliverable/AcReference.vue'
import {genReference} from '@/specs/helpers/fixtures'

let wrapper: Wrapper<Vue>

describe('AcReference.vue', () => {
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Pops into a new window', async() => {
    const reference = genReference()
    reference.file.full = 'https://example.com/stuff.jpg'
    wrapper = qMount(AcReference, {
      propsData: {reference, baseName: 'Sales'},
      stubs: ['router-link'],
      mocks: {$route: {params: {}}},
    })
    const vm = wrapper.vm as any
    const mockOpen = spyOn(window, 'open')
    wrapper.find('.pop-out-button').trigger('click')
    await vm.$nextTick()
    expect(mockOpen).toHaveBeenCalledWith('https://example.com/stuff.jpg', '_blank')
  })
})
