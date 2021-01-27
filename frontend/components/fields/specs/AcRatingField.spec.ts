import Vuetify from 'vuetify/lib'
import {Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import {ArtStore, createStore} from '@/store'
import {cleanUp, createVuetify, docTarget, vueSetup, mount} from '@/specs/helpers'
import AcRatingField from '@/components/fields/AcRatingField.vue'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

describe('AcRatingField.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Creates a field based on a field controller', async() => {
    wrapper = mount(AcRatingField, {
      localVue,
      store,
      vuetify,

      attachTo: docTarget(),
      propsData: {value: 1},
    })
    const vm = wrapper.vm as any
    await vm.$nextTick()
    const mockEmit = jest.spyOn(vm, '$emit')
    vm.scratch = 2
    expect(mockEmit).toHaveBeenCalledWith('input', 2)
  })
})
