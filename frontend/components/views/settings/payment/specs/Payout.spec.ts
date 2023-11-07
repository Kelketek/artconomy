import {cleanUp, mount, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {VueWrapper} from '@vue/test-utils'
import Payout from '@/components/views/settings/payment/Payout.vue'
import {genUser} from '@/specs/helpers/fixtures'
import {describe, beforeEach, afterEach, test} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>

describe('Payout.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Mounts', async() => {
    setViewer(store, genUser())
    wrapper = mount(Payout, {
      ...vueSetup({
        store,
        stubs: ['router-link'],
      }),
      props: {username: 'Fox'},
    })
  })
})
