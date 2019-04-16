import Vue from 'vue'
import Vuex from 'vuex'
import {createLocalVue, mount} from '@vue/test-utils'
import Vuetify from 'vuetify'
import {Singles} from '@/store/singles/registry'
import {Profiles} from '@/store/profiles/registry'
import Artist from '@/components/views/settings/Artist.vue'
import {ArtStore, createStore} from '@/store'
import {setViewer} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import {Lists} from '@/store/lists/registry'

Vue.use(Vuex)
Vue.use(Vuetify)
const localVue = createLocalVue()
localVue.use(Singles)
localVue.use(Lists)
localVue.use(Profiles)
let store: ArtStore

describe('Artist.VUE', () => {
  beforeEach(() => {
    store = createStore()
  })
  it('Mounts', () => {
    setViewer(store, genUser())
    mount(Artist, {localVue, store, propsData: {username: 'Fox'}})
  })
})
