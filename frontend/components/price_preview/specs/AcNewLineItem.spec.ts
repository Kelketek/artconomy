import {Wrapper} from '@vue/test-utils'
import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import {ArtStore, createStore} from '@/store'
import {cleanUp, createVuetify, docTarget, vueSetup, mount} from '@/specs/helpers'
import Router from 'vue-router'
import {LineTypes} from '@/types/LineTypes'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import AcNewLineItem from '@/components/price_preview/AcNewLineItem.vue'
import {FormController} from '@/store/forms/form-controller'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let vuetify: Vuetify
let empty: Vue
let addOnForm: FormController

describe('AcNewLineItem.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    empty = mount(Empty, {localVue, store, vuetify}).vm
    addOnForm = empty.$getForm('addOn', {
      endpoint: '/test/',
      fields: {
        amount: {value: 0, validators: [{name: 'numeric'}]},
        description: {value: ''},
        type: {value: LineTypes.ADD_ON},
        percentage: {value: 0},
      },
    })
  })
  it('Gives a default label to a discount', async() => {
    wrapper = mount(AcNewLineItem, {
      localVue,
      store,

      attachTo: docTarget(),
      propsData: {form: addOnForm, price: -2},
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.html()).toContain('Surcharge/Discount')
  })
  it('Gives a default label to an extra service item', async() => {
    addOnForm.fields.type.update(LineTypes.EXTRA)
    wrapper = mount(AcNewLineItem, {
      localVue,
      store,

      attachTo: docTarget(),
      propsData: {form: addOnForm, price: 10},
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.html()).toContain('Extra item')
  })
  it('Gives a default label to any other type', async() => {
    addOnForm.fields.type.update(123)
    wrapper = mount(AcNewLineItem, {
      localVue,
      store,

      attachTo: docTarget(),
      propsData: {form: addOnForm, price: 10},
    })
    await wrapper.vm.$nextTick()
    expect(wrapper.html()).toContain('Other')
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
})
