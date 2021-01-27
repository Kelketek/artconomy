import {Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import BoundField from '@/specs/helpers/dummy_components/bound-field.vue'
import {ArtStore, createStore} from '@/store'
import {cleanUp, createVuetify, docTarget, vueSetup, mount} from '@/specs/helpers'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

describe('AcBoundField.ts', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Creates a field based on a field controller', async() => {
    wrapper = mount(BoundField, {localVue, store, vuetify, attachTo: docTarget()})
    await wrapper.vm.$nextTick()
    const controller = (wrapper.vm as any).form
    expect(wrapper.find('#' + controller.fields.name.id).exists()).toBe(true)
  })
})
