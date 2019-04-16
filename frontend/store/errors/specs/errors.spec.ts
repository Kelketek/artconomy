import Vue from 'vue'
import Vuex from 'vuex'
import mockAxios from '@/specs/helpers/mock-axios'
import {ArtStore, createStore} from '../../index'
import {createLocalVue} from '@vue/test-utils'

const localVue = createLocalVue()
localVue.use(Vuex)

describe('Errors store', () => {
  let store: ArtStore
  beforeEach(() => {
    mockAxios.reset()
    store = createStore()
  })
  it('Commits an error code', () => {
    store.commit('errors/setError', {response: {status: 500}})
    expect((store.state as any).errors.code).toBe(500)
  })
  it('Resolves to common error images', () => {
    for (const code of [500, 503, 400, 404, 403]) {
      store.commit('errors/setError', {response: {status: code}})
      expect((store.getters as any)['errors/logo']).toBe(`/static/images/${code}.png`)
    }
  })
  it('Resolves to a generic image if the code is unknown', () => {
    store.commit('errors/setError', {response: {status: 600}})
    expect((store.getters as any)['errors/logo']).toBe(`/static/images/generic-error.png`)
  })
  it('Resolves to 503 if no response was received', () => {
    store.commit('errors/setError', {})
    expect((store.getters as any)['errors/logo']).toBe(`/static/images/503.png`)
  })
  it('Clears the error', () => {
    store.commit('errors/setError', {response: {status: 500}})
    store.commit('errors/clearError')
    expect((store.state as any).errors.code).toBe(0)
  })
})
