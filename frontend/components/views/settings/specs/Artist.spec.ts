import Vuetify from 'vuetify/lib'
import Artist from '@/components/views/settings/Artist.vue'
import {ArtStore, createStore} from '@/store'
import {cleanUp, createVuetify, setViewer, vueSetup, mount} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'

const localVue = vueSetup()
let store: ArtStore
let vuetify: Vuetify

describe('Artist.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp()
  })
  it('Mounts', () => {
    setViewer(store, genUser())
    mount(Artist, {localVue, store, propsData: {username: 'Fox'}})
  })
})
