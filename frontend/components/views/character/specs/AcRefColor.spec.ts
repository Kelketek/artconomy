import {VueWrapper} from '@vue/test-utils'
import Empty from '@/specs/helpers/dummy_components/empty'
import {ArtStore, createStore} from '@/store'
import AcRefColor from '@/components/views/character/AcRefColor.vue'
import {cleanUp, createVuetify, mount, setViewer, vueSetup} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

describe('AcRefColor.vue', () => {
  let store: ArtStore
  let wrapper: VueWrapper<any>
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Mounts', async() => {
    setViewer(store, genUser())
    const empty = mount(Empty, vueSetup({store}))
    const color = empty.vm.$getSingle('color', {endpoint: '/endpoint/'})
    color.setX({
      color: '#555555',
      note: 'This is a test color',
    })
    wrapper = mount(AcRefColor, {
      ...vueSetup({
        store,
        mocks: {
          $route: {
            name: 'Character',
            params: {},
            query: {},
          },
        },
      }),
      props: {
        color,
        username: 'Fox',
      },
    })
  })
})
