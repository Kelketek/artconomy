import Vue from 'vue'
import Vuex from 'vuex'
import mockAxios from '@/specs/helpers/mock-axios'
import {ArtStore, createStore} from '../../index'
import {createLocalVue} from '@vue/test-utils'
import {fieldFromSchema} from '../index'
import {formRegistry} from '../registry'
import {rs} from '@/specs/helpers'
import flushPromises from 'flush-promises'
import {HttpVerbs} from '@/store/forms/types/HttpVerbs'
import {RootFormState} from '@/store/forms/types/RootFormState'

Vue.use(Vuex)
const localVue = createLocalVue()

describe('Forms store', () => {
  let store: ArtStore
  let state: RootFormState
  beforeEach(() => {
    formRegistry.reset()
    formRegistry.resetValidators()
    mockAxios.reset()
    store = createStore()
    state = (store.state as any).forms as RootFormState
  })
  it('Creates a form', () => {
    store.commit('forms/initForm', {name: 'example', fields: {name: {value: 'Fox'}, age: {value: 30}}})
    expect(state.example.fields.name.initialData).toBe('Fox')
    expect(state.example.method).toBe('post')
    expect(state.example.fields.age.initialData).toBe(30)
    expect(state.example.fields.name.value).toBe('Fox')
    expect(state.example.fields.age.value).toBe(30)
    expect(state.example.errors).toEqual([])
    expect(state.example.fields.name.errors).toEqual([])
    expect(state.example.fields.age.errors).toEqual([])
  })
  it('Deletes a form', () => {
    store.commit('forms/initForm', {name: 'example', fields: {name: {value: 'Fox'}, age: {value: 30}}})
    expect(state.example).toBeTruthy()
    store.commit('forms/delForm', {name: 'example'})
    expect(state.example).toBe(undefined)
  })
  it('Creates a form with a different method', () => {
    store.commit(
      'forms/initForm',
      {name: 'example', method: 'get', fields: {name: {value: 'Fox'}, age: {value: 30}}}
    )
    expect(state.example.method).toBe('get')
  })
  it('Creates a form with errors', () => {
    store.commit(
      'forms/initForm',
      {name: 'example', fields: {name: {value: 'Fox', errors: ['Too cool.']}, age: {value: 30}}}
    )
    expect(state.example.fields.name.value).toBe('Fox')
    expect(state.example.fields.age.value).toBe(30)
    expect(state.example.fields.name.errors).toEqual(['Too cool.'])
    expect(state.example.fields.age.errors).toEqual([])
  })
  it('Updates form data', () => {
    store.commit(
      'forms/initForm',
      {name: 'example', fields: {name: {value: 'Fox', errors: ['Too cool.']}, age: {value: 30}}}
    )
    expect(state.example.fields.name.errors).toEqual(['Too cool.'])
    store.commit('forms/updateValues', {name: 'example', data: {name: 'Wolf'}})
    // Should not affect error status at this point.
    expect(state.example.fields.name.errors).toEqual(['Too cool.'])
    expect(state.example.fields.name.value).toBe('Wolf')
    expect(state.example.fields.age.value).toBe(30)
    expect(state.example.fields.name.initialData).toBe('Fox')
    expect(state.example.fields.age.initialData).toBe(30)
  })
  it('Updates errors', () => {
    store.commit(
      'forms/initForm',
      {name: 'example', fields: {name: {value: 'Fox'}, age: {value: 30}}})
    store.commit('forms/setErrors', {
      name: 'example', errors: {fields: {name: ['Too cool.']}, errors: ['Borked.']},
    })
    expect(state.example.fields.name.errors).toEqual(['Too cool.'])
    expect(state.example.errors).toEqual(['Borked.'])
  })
  it('Updates meta errors', () => {
    store.commit(
      'forms/initForm',
      {name: 'example', fields: {name: {value: 'Fox', errors: ['Too cool.']}, age: {value: 30}}}
    )
    store.commit('forms/setMetaErrors', {name: 'example', errors: ['Borked.']})
    expect(state.example.errors).toEqual(['Borked.'])
  })
  it('Updates field errors', () => {
    store.commit(
      'forms/initForm',
      {name: 'example', fields: {name: {value: 'Fox', errors: ['Too cool.']}}}
    )
    store.commit('forms/setFieldErrors', {name: 'example', fields: {name: ['Way too cool!']}})
    expect(state.example.fields.name.errors).toEqual(['Way too cool!'])
  })
  it('Clears all errors', () => {
    store.commit(
      'forms/initForm',
      {
        name: 'example',
        fields: {name: {value: 'Fox', errors: ['Too cool.']}, age: {value: 30}},
        errors: ['Borked.'],
      }
    )
    expect(state.example.fields.name.errors).toEqual(['Too cool.'])
    expect(state.example.errors).toEqual(['Borked.'])
    store.commit('forms/clearErrors', {name: 'example'})
    expect(state.example.fields.name.errors).toEqual([])
    expect(state.example.errors).toEqual([])
  })
  it('Handles missing data in set errors sanely', () => {
    store.commit(
      'forms/initForm',
      {
        name: 'example',
        fields: {name: {value: 'Fox', errors: ['Too cool.']}, age: {value: 30}},
        errors: ['Borked.'],
      }
    )
    expect(state.example.fields.name.errors).toEqual(['Too cool.'])
    expect(state.example.errors).toEqual(['Borked.'])
    store.commit('forms/setErrors', {name: 'example', errors: {}})
    expect(state.example.fields.name.errors).toEqual([])
    expect(state.example.errors).toEqual([])
  })
  it('Adds a field', () => {
    store.commit('forms/initForm', {name: 'example', fields: {name: {value: 'Fox'}, age: {value: 30}}})
    store.commit('forms/addField', {name: 'example', field: {name: 'sex', schema: {value: 'Male'}}})
    expect(state.example.fields.name.value).toBe('Fox')
    expect(state.example.fields.sex.value).toBe('Male')
    expect(state.example.fields.sex.initialData).toBe('Male')
    expect(state.example.fields.sex.errors).toEqual([])
  })
  it('Adds a field with errors', () => {
    store.commit('forms/initForm', {name: 'example', fields: {name: {value: 'Fox'}, age: {value: 30}}})
    store.commit(
      'forms/addField',
      {name: 'example', field: {name: 'sex', schema: {value: 'Male', errors: ['So much dick!']}}}
    )
    expect(state.example.fields.name.value).toBe('Fox')
    expect(state.example.fields.sex.value).toBe('Male')
    expect(state.example.fields.sex.initialData).toBe('Male')
    expect(state.example.fields.sex.errors).toEqual(['So much dick!'])
  })
  it('Removes a field', () => {
    store.commit('forms/initForm', {name: 'example', fields: {name: {value: 'Fox'}, age: {value: 30}}})
    expect(state.example.fields.age).toBeTruthy()
    store.commit('forms/delField', {name: 'example', field: 'age'})
    expect(state.example.fields.age).toBe(undefined)
  })
  it('Submits a form', async() => {
    store.commit('forms/initForm', {
      name: 'example', fields: {name: {value: 'Fox'}, age: {value: 30}}, endpoint: '/test/endpoint/',
    })
    store.dispatch('forms/submit', {name: 'example'}).then()
    expect(mockAxios.post).toHaveBeenCalledWith(
      '/test/endpoint/',
      {name: 'Fox', age: 30},
      {headers: {'Content-Type': 'application/json; charset=utf-8'}}
    )
  })
  it('Resets after submission', async() => {
    store.commit('forms/initForm', {
      name: 'example', fields: {name: {value: 'Fox'}, age: {value: 30}}, endpoint: '/test/endpoint/',
    })
    store.commit('forms/updateValues', {name: 'example', data: {name: 'Amber', age: 20}})
    store.dispatch('forms/submit', {name: 'example'}).then()
    mockAxios.mockResponse(rs({}))
    await flushPromises()
    expect(state.example.fields.name.value).toBe('Fox')
    expect(state.example.fields.age.value).toBe(30)
  })
  it('Does not reset after submitting if reset is disabled', async() => {
    store.commit('forms/initForm', {
      name: 'example',
      fields: {name: {value: 'Fox'}, age: {value: 30}},
      endpoint: '/test/endpoint/',
      reset: false,
    })
    store.commit('forms/updateValues', {name: 'example', data: {name: 'Amber', age: 20}})
    store.dispatch('forms/submit', {name: 'example'}).then()
    mockAxios.mockResponse(rs({}))
    await flushPromises()
    expect(state.example.fields.name.value).toBe('Amber')
    expect(state.example.fields.age.value).toBe(20)
  })
  it('Submits a form with ommissions', async() => {
    store.commit('forms/initForm', {
      name: 'example',
      fields: {name: {value: 'Fox', omitIf: ''}, age: {value: 0, omitIf: 0}},
      endpoint: '/test/endpoint/',
    })
    store.dispatch('forms/submit', {name: 'example'}).then()
    expect(mockAxios.post).toHaveBeenCalledWith(
      '/test/endpoint/',
      {name: 'Fox'},
      {headers: {'Content-Type': 'application/json; charset=utf-8'}}
    )
  })
  it('Merges defaults for field Schemas', () => {
    let field = fieldFromSchema({value: 'Derp'})
    expect(field).toEqual({
      disabled: false,
      validators: [],
      errors: [],
      hidden: false,
      initialData: 'Derp',
      extra: {},
      value: 'Derp',
      debounce: null,
      step: 1,
    }
    )
    field = fieldFromSchema({value: 'Derp', debounce: 200, validators: [{name: 'Herp', args: ['wat']}]})
    expect(field).toEqual({
      disabled: false,
      validators: [{name: 'Herp', args: ['wat']}],
      errors: [],
      hidden: false,
      initialData: 'Derp',
      extra: {},
      value: 'Derp',
      debounce: 200,
      step: 1,
    }
    )
  })
})
