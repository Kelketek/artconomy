import {VueWrapper} from '@vue/test-utils'
import BoundField from '@/specs/helpers/dummy_components/bound-field.vue'
import {ArtStore, createStore} from '@/store/index.ts'
import {cleanUp, mount, vueSetup} from '@/specs/helpers/index.ts'
import {describe, expect, beforeEach, afterEach, test} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>

describe('AcBoundField.ts', () => {
  beforeEach(() => {
    store = createStore()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Creates a field based on a field controller', async() => {
    wrapper = mount(BoundField, vueSetup({store}))
    await wrapper.vm.$nextTick()
    const controller = (wrapper.vm as any).form
    expect(wrapper.find('#' + controller.fields.name.id).exists()).toBe(true)
  })
})
