import {mount, Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import {cleanUp, createVuetify, docTarget, flushPromises, rs, setViewer, vueSetup, vuetifySetup} from '@/specs/helpers'
import AcCharacterSelect from '@/components/fields/AcCharacterSelect.vue'
import mockAxios from '@/__mocks__/axios'
import Vuetify from 'vuetify/lib'
import {ArtStore, createStore} from '@/store'
import {genUser} from '@/specs/helpers/fixtures'

const localVue = vueSetup()
jest.useFakeTimers()
let wrapper: Wrapper<Vue>
let vuetify: Vuetify
let store: ArtStore

describe('AcCharacterSelect.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    jest.clearAllTimers()
    cleanUp(wrapper)
  })
  it('Accepts a response from the server on its query', async() => {
    setViewer(store, genUser())
    const tagList: number[] = []
    wrapper = mount(AcCharacterSelect, {
      localVue,
      vuetify,
      store,

      attachTo: docTarget(),
      propsData: {value: tagList},
    })
    wrapper.find('input').setValue('Test')
    await wrapper.vm.$nextTick()
    await jest.runAllTimers()
    mockAxios.mockResponse(rs({
      results: [
        {name: 'Test', id: 1, user: {username: 'Fox'}},
        {name: 'Test2', id: 2, user: {username: 'Dude'}},
      ],
    },
    ))
    await flushPromises()
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).items).toEqual([
      {name: 'Test', id: 1, user: {username: 'Fox'}},
      {name: 'Test2', id: 2, user: {username: 'Dude'}},
    ])
  })
})
