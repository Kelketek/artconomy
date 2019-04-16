import Vue from 'vue'
import Vuex from 'vuex'
import Vuetify from 'vuetify'
import {createLocalVue, shallowMount} from '@vue/test-utils'
import NotFound from '../NotFound.vue'
import {ArtStore, createStore} from '@/store'

// Must use it directly, due to issues with package imports upstream.
Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.use(Vuex)

describe('App.vue', () => {
  let store: ArtStore
  beforeEach(() => {
    store = createStore()
  })
  it('Sets the error code upon creation', async() => {
    const wrapper = shallowMount(NotFound, {
      store, localVue,
    })
    expect((store.state as any).errors.code).toBe(404)
  })
})
