import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import Vuex from 'vuex'
import Vue from 'vue'
import Vuetify from 'vuetify'
import {FormControllers, formRegistry} from '@/store/forms/registry'
import BoundField from '@/specs/helpers/dummy_components/bound-field.vue'
import {ArtStore, createStore} from '@/store'
import {vuetifySetup} from '@/specs/helpers'

Vue.use(Vuex)
Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.use(FormControllers)
let store: ArtStore
let wrapper: Wrapper<Vue>

describe('AcBoundField.ts', () => {
  beforeEach(() => {
    formRegistry.reset()
    store = createStore()
    vuetifySetup()
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Creates a field based on a field controller', async() => {
    wrapper = mount(BoundField, {localVue, store, sync: false, attachToDocument: true})
    await wrapper.vm.$nextTick()
    const controller = (wrapper.vm as any).form
    expect(wrapper.find('#' + controller.fields.name.id).exists()).toBe(true)
  })
})
