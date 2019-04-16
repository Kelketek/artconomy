import {createLocalVue, mount, Wrapper} from '@vue/test-utils'
import Vuetify from 'vuetify'
import Vue from 'vue'
import {vuetifySetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import Vuex from 'vuex'
import Editor from '@/specs/helpers/dummy_components/editor.vue'

Vue.use(Vuetify)
Vue.use(Vuex)
const localVue = createLocalVue()
let store: ArtStore
let wrapper: Wrapper<Vue>

const mockError = jest.spyOn(console, 'error')

describe('ac-editor', () => {
  beforeEach(() => {
    vuetifySetup()
    store = createStore()
    mockError.mockImplementationOnce(() => undefined)
  })
  afterEach(() => {
    mockError.mockClear()
    if (wrapper) {
      wrapper.destroy()
    }
  })
  it('Mounts the editor', async() => {
    wrapper = mount(Editor, {localVue, store, sync: false, attachToDocument: true})
  })
  it('Auto saves changes', async() => {
    wrapper = mount(Editor, {
      localVue, store, sync: false, attachToDocument: true,
    })
    const mockEmit = jest.spyOn(wrapper.vm.$refs.auto as any, '$emit')
    wrapper.find('#editor textarea').setValue('Hello there!')
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).stuff).toBe('Hello there!')
    expect(mockEmit).toHaveBeenCalledWith('input', 'Hello there!')
  })
  it('Saves changes manually', async() => {
    wrapper = mount(Editor, {localVue, store})
    wrapper.find('#editor-manual textarea').setValue('Hello there!')
    await wrapper.vm.$nextTick()
    expect((wrapper.vm as any).things).toBe('')
  })
  it('Does not propagate the changes down when manually controlled', async() => {
    wrapper = mount(Editor, {
      localVue, store, sync: false, attachToDocument: true,
    })
    const mockEmit = jest.spyOn(wrapper.vm.$refs.auto as any, '$emit');
    (wrapper.vm as any).things = 'Hello there!'
    await wrapper.vm.$nextTick()
    expect((wrapper.vm.$refs.manual as any).scratch).toBe('')
    expect(mockEmit).not.toHaveBeenCalled()
  })
  it('Previews the result', async() => {
    wrapper = mount(Editor, {localVue, store, sync: false, attachToDocument: true})
    wrapper.find('#editor-manual textarea').setValue('# Hello there!')
    await wrapper.vm.$nextTick()
    wrapper.find('#editor-manual .preview-mode-toggle').trigger('click')
    await wrapper.vm.$nextTick()
    expect((wrapper.vm.$refs.manual as any).previewMode).toBe(true)
    expect(wrapper.find('.editor-preview h1').text()).toBe('Hello there!')
  })
})
