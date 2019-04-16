import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import Vuex from 'vuex'
import Vue from 'vue'
import Vuetify from 'vuetify'
import {FormControllers, formRegistry} from '@/store/forms/registry'
import {ArtStore, createStore} from '@/store'
import {vuetifySetup} from '@/specs/helpers'
import AcRatingField from '@/components/fields/AcRatingField.vue'

Vue.use(Vuex)
Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.use(FormControllers)
let store: ArtStore
let wrapper: Wrapper<Vue>

describe('AcRatingField.vue', () => {
  beforeEach(() => {
    formRegistry.reset()
    store = createStore()
    vuetifySetup()
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Creates a field based on a field controller', async() => {
    wrapper = mount(AcRatingField, {
      localVue, store, sync: false, attachToDocument: true, propsData: {value: 1}}
    )
    const vm = wrapper.vm as any
    await vm.$nextTick()
    const mockEmit = jest.spyOn(vm, '$emit')
    vm.scratch = 2
    expect(mockEmit).toHaveBeenCalledWith('input', 2)
  })
})
