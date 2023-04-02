import {createVuetify, mount, vueSetup} from '@/specs/helpers'
import AcColorPrepend from '@/components/fields/AcColorPrepend.vue'
import {VueConstructor} from 'vue'
import Vuetify from 'vuetify/lib'

let localVue: VueConstructor
let vuetify: Vuetify

describe('AcColorPrepend.vue', () => {
  beforeEach(() => {
    localVue = vueSetup()
    vuetify = createVuetify()
  })
  it('Mounts', () => {
    const wrapper = mount(AcColorPrepend, {localVue, vuetify})
    const input = wrapper.find('.picker').element as HTMLInputElement
    const mockClick = jest.fn()
    input.onclick = mockClick
    wrapper.find('.picker-button').trigger('click')
    expect(mockClick).toHaveBeenCalled()
  })
})
