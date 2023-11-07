import Artist from '@/components/views/settings/Artist.vue'
import {ArtStore, createStore} from '@/store'
import {cleanUp, mount, setViewer, vueSetup} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import {describe, beforeEach, afterEach, test, vi} from 'vitest'

let store: ArtStore

describe('Artist.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp()
  })
  test('Mounts', () => {
    setViewer(store, genUser())
    mount(Artist, {
      ...vueSetup({store}),
      props: {username: 'Fox'},
    })
  })
})
