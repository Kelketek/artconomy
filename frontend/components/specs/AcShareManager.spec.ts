import {cleanUp, mount, vueSetup} from '@/specs/helpers'
import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import AcShareManager from '@/components/AcShareManager.vue'
import Empty from '@/specs/helpers/dummy_components/empty'
import {afterEach, beforeEach, describe, test} from 'vitest'

let wrapper: VueWrapper<any>
let store: ArtStore

describe('AcShareManager.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Mounts', async() => {
    const list = mount(Empty, vueSetup({store})).vm.$getList('stuff', {endpoint: '/'})
    wrapper = mount(AcShareManager, {
      ...vueSetup({
        store,
        stubs: ['ac-bound-field'],
      }),
      props: {controller: list},
    })
  })
})
