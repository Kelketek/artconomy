import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import AcShareManager from '@/components/AcShareManager.vue'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
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
