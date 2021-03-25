import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import {cleanUp, createVuetify, docTarget, setViewer, vueSetup, mount} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {Wrapper} from '@vue/test-utils'
import Payout from '@/components/views/settings/payment/Payout.vue'
import {genUser} from '@/specs/helpers/fixtures'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

describe('Payout.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts', async() => {
    setViewer(store, genUser())
    wrapper = mount(Payout, {localVue, store, propsData: {username: 'Fox'}, attachTo: docTarget()})
  })
})
