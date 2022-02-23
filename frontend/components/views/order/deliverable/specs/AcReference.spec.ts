import {cleanUp, qMount, mount} from '@/specs/helpers'
import {Wrapper} from '@vue/test-utils'
import AcReference from '@/components/views/order/deliverable/AcReference.vue'
import {genReference} from '@/specs/helpers/fixtures'

let wrapper: Wrapper<Vue>
let mockOpen: jest.MockedFn<any>

describe('AcReference.vue', () => {
  beforeAll(() => {
    mockOpen = jest.fn()
    window.open = mockOpen
  })
  afterEach(() => {
    cleanUp(wrapper)
    mockOpen.mockReset()
  })
  it('Pops into a new window', async() => {
    const reference = genReference()
    reference.file.full = 'https://example.com/stuff.jpg'
    const mockOpen = jest.spyOn(window, 'open')
    wrapper = qMount(AcReference, {
      propsData: {reference, baseName: 'Sales'},
      stubs: ['router-link'],
      mocks: {$route: {params: {}}},
    })
    const vm = wrapper.vm as any
    wrapper.find('.pop-out-button').trigger('click')
    await vm.$nextTick()
    expect(mockOpen).toHaveBeenCalledWith('https://example.com/stuff.jpg', '_blank')
  })
})
