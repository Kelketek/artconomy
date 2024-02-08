import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import {ArtStore, createStore} from '@/store/index.ts'
import {VueWrapper} from '@vue/test-utils'
import AcDeliverableRating from '@/components/views/order/AcDeliverableRating.vue'
import {afterEach, beforeEach, describe, test} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>

describe('AcDeliverableRating.vue', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Mounts', async() => {
    wrapper = mount(AcDeliverableRating, {
      ...vueSetup({store}),
      props: {
        orderId: 3,
        end: 'buyer',
        deliverableId: 5,
      },
    })
  })
})
