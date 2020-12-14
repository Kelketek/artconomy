import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import {shallowMount, Wrapper} from '@vue/test-utils'
import NotFound from '../NotFound.vue'
import {ArtStore, createStore} from '@/store'
import {cleanUp, createVuetify, vueSetup} from '@/specs/helpers'

const localVue = vueSetup()
let vuetify: Vuetify
let wrapper: Wrapper<Vue>

describe('NotFound.vue', () => {
  let store: ArtStore
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Sets the error code upon creation', async() => {
    wrapper = shallowMount(NotFound, {
      store, localVue, vuetify,
    })
    expect((store.state as any).errors.code).toBe(404)
  })
})
