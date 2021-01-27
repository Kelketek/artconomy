import {Wrapper} from '@vue/test-utils'
import Vuetify from 'vuetify/lib'
import Vue from 'vue'
import {cleanUp, createVuetify, docTarget, vueSetup, mount} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import Editor from '@/specs/helpers/dummy_components/editor.vue'

const localVue = vueSetup()
let store: ArtStore
let wrapper: Wrapper<Vue>
let vuetify: Vuetify

const mockError = jest.spyOn(console, 'error')

describe('ac-editor', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    mockError.mockImplementationOnce(() => undefined)
  })
  afterEach(() => {
    mockError.mockClear()
    cleanUp(wrapper)
  })
  it('Mounts the editor', async() => {
    wrapper = mount(Editor, {
      localVue,
      store,
      vuetify,

      attachTo: docTarget(),
    })
  })
  it('Auto saves changes', async() => {
    wrapper = mount(Editor, {
      localVue,
      store,
      vuetify,

      attachTo: docTarget(),
    })
    const mockEmit = jest.spyOn(wrapper.vm.$refs.auto as any, '$emit')
    wrapper.find('#editor textarea').setValue('Hello there!')
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).stuff).toBe('Hello there!')
    expect(mockEmit).toHaveBeenCalledWith('input', 'Hello there!')
  })
  it('Saves changes manually', async() => {
    wrapper = mount(Editor, {
      localVue,
      store,
      vuetify,
    })
    wrapper.find('#editor-manual textarea').setValue('Hello there!')
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).things).toBe('')
  })
  it('Does not propagate the changes down when manually controlled', async() => {
    wrapper = mount(Editor, {
      localVue,
      store,
      vuetify,

      attachTo: docTarget(),
    })
    const mockEmit = jest.spyOn(wrapper.vm.$refs.auto as any, '$emit');
    (wrapper.vm as any).things = 'Hello there!'
    await wrapper.vm.$nextTick()
    expect((wrapper.vm.$refs.manual as any).scratch).toBe('')
    expect(mockEmit).not.toHaveBeenCalled()
  })
  it('Previews the result', async() => {
    wrapper = mount(Editor, {
      localVue,
      store,
      vuetify,

      attachTo: docTarget(),
    })
    wrapper.find('#editor-manual textarea').setValue('# Hello there!')
    await wrapper.vm.$nextTick()
    wrapper.find('#editor-manual .preview-mode-toggle').trigger('click')
    await wrapper.vm.$nextTick()
    expect((wrapper.vm.$refs.manual as any).previewMode).toBe(true)
    expect(wrapper.find('.editor-preview h1').text()).toBe('Hello there!')
  })
})
