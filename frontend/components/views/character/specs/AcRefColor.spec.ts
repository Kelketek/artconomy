import {VueWrapper} from '@vue/test-utils'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import AcRefColor from '@/components/views/character/AcRefColor.vue'
import {cleanUp, createTestRouter, createVuetify, mount, vueSetup} from '@/specs/helpers/index.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'
import {createRouter, Router} from 'vue-router'
import {setViewer} from '@/lib/lib.ts'

describe('AcRefColor.vue', () => {
  let store: ArtStore
  let wrapper: VueWrapper<any>
  let router: Router
  beforeEach(() => {
    store = createStore()
    router = createTestRouter()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Mounts', async() => {
    setViewer(store, genUser())
    await router.push('/')
    await router.isReady()
    const empty = mount(Empty, vueSetup({store, extraPlugins: [router]}))
    const color = empty.vm.$getSingle('color', {endpoint: '/endpoint/'})
    color.setX({
      color: '#555555',
      note: 'This is a test color',
    })
    wrapper = mount(AcRefColor, {
      ...vueSetup({store, extraPlugins: [router]}),
      props: {
        color,
        username: 'Fox',
      },
    })
  })
})
