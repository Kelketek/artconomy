import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import {cleanUp, docTarget, mount, vueSetup} from '@/specs/helpers/index.ts'
import {LineType} from '@/types/enums/LineType.ts'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import AcNewLineItem from '@/components/price_preview/AcNewLineItem.vue'
import {FormController} from '@/store/forms/form-controller.ts'
import {describe, expect, beforeEach, afterEach, test} from 'vitest'

import type {ArtVueInterface} from '@/types/main'

let store: ArtStore
let wrapper: VueWrapper<any>
let empty: ArtVueInterface
let addOnForm: FormController

describe('AcNewLineItem.vue', () => {
  beforeEach(() => {
    store = createStore()
    empty = mount(Empty, vueSetup({store})).vm
    addOnForm = empty.$getForm('addOn', {
      endpoint: '/test/',
      fields: {
        amount: {
          value: 0,
          validators: [{name: 'numeric'}],
        },
        description: {value: ''},
        type: {value: LineType.ADD_ON},
        percentage: {value: 0},
      },
    })
  })
  test('Gives a default label to a discount', async() => {
    wrapper = mount(AcNewLineItem, {
      ...vueSetup({store}),
      attachTo: docTarget(),
      props: {
        form: addOnForm,
        price: -2,
      },
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.html()).toContain('Surcharge/Discount')
  })
  test('Gives a default label to an extra service item', async() => {
    addOnForm.fields.type.update(LineType.EXTRA)
    wrapper = mount(AcNewLineItem, {
      ...vueSetup({store}),
      attachTo: docTarget(),
      props: {
        form: addOnForm,
        price: 10,
      },
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.html()).toContain('Extra item')
  })
  test('Gives a default label to any other type', async() => {
    addOnForm.fields.type.update(123)
    wrapper = mount(AcNewLineItem, {
      ...vueSetup({store}),
      attachTo: docTarget(),
      props: {
        form: addOnForm,
        price: 10,
      },
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.html()).toContain('Other')
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
})
