import Artist from '@/components/views/settings/Artist.vue'
import {ArtStore, createStore} from '@/store/index.ts'
import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {describe, beforeEach, afterEach, test, vi} from 'vitest'
import {setViewer} from '@/lib/lib.ts'

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
