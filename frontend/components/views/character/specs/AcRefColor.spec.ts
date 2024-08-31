import {VueWrapper} from '@vue/test-utils'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import AcRefColor from '@/components/views/character/AcRefColor.vue'
import {cleanUp, createTestRouter, mount, vueSetup} from '@/specs/helpers/index.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {describe, beforeEach, afterEach, test} from 'vitest'
import {Router} from 'vue-router'
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
    setViewer({ store, user: genUser() })
    await router.push('/')
    await router.isReady()
    const empty = mount(Empty, vueSetup({store, router}))
    const color = empty.vm.$getSingle('color', {endpoint: '/endpoint/'})
    color.setX({
      color: '#555555',
      note: 'This is a test color',
    })
    wrapper = mount(AcRefColor, {
      ...vueSetup({store, router}),
      props: {
        color,
        username: 'Fox',
      },
    })
  })
})
