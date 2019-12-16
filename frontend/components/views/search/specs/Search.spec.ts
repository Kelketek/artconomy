import Vue from 'vue'
import {Vuetify} from 'vuetify/types'
import Router from 'vue-router'
import {cleanUp, createVuetify, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import Search from '@/components/views/search/Search.vue'
import SearchProducts from '@/components/views/search/SearchProducts.vue'
import SearchCharacters from '@/components/views/search/SearchCharacters.vue'
import SearchProfiles from '@/components/views/search/SearchProfiles.vue'
import SearchSubmissions from '@/components/views/search/SearchSubmissions.vue'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import ProductExtra from '@/components/views/search/extra/ProductExtra.vue'
import ProductHints from '@/components/views/search/hints/ProductHints.vue'
import SubmissionHints from '@/components/views/search/hints/SubmissionHints.vue'
import CharacterHints from '@/components/views/search/hints/CharacterHints.vue'
import ProfileHints from '@/components/views/search/hints/ProfileHints.vue'
import searchSchema from '@/components/views/search/specs/fixtures'
import {FormController} from '@/store/forms/form-controller'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let router: Router
let searchForm: FormController
let vuetify: Vuetify

describe('Search.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    router = new Router({
      mode: 'history',
      routes: [{
        path: '/search/:tabName?/',
        name: 'Search',
        component: Search,
        props: true,
        children: [{
          path: 'products',
          name: 'SearchProducts',
          components: {
            default: SearchProducts,
            hints: ProductHints,
            extra: ProductExtra,
          },
          props: true,
        }, {
          path: 'submissions',
          name: 'SearchSubmissions',
          components: {
            default: SearchSubmissions,
            hints: SubmissionHints,
          },
          props: true,
        }, {
          path: 'characters',
          name: 'SearchCharacters',
          components: {
            default: SearchCharacters,
            hints: CharacterHints,
          },
          props: true,
        }, {
          path: 'profiles',
          name: 'SearchProfiles',
          components: {
            default: SearchProfiles,
            hints: ProfileHints,
          },
          props: true,
        }],
      }],
    })
    searchForm = mount(Empty, {localVue, store, sync: false}).vm.$getForm('search', searchSchema())
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts', () => {
    wrapper = mount(Search, {localVue, store, vuetify, router, sync: false, attachToDocument: true})
  })
  it('Tabs through each search option', async() => {
    wrapper = mount(Search, {localVue, store, vuetify, router, sync: false, attachToDocument: true})
    const routes = ['SearchProducts', 'SearchSubmissions', 'SearchCharacters', 'SearchProfiles']
    for (const [index, el] of wrapper.findAll('.v-item-group .v-btn').wrappers.entries()) {
      el.trigger('click')
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.$route.name).toBe(routes[index])
    }
  })
  it('Opens the default view', async() => {
    router.push({name: 'Search'})
    searchForm.fields.featured.update(true)
    wrapper = mount(Search, {localVue, store, vuetify, router, sync: false, attachToDocument: true})
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.$route.name).toBe('SearchProducts')
  })
  it('Updates the route when the values change', async() => {
    // Need to start the fake timers here or else things get weird during the test.
    jest.useFakeTimers()
    router.push({name: 'SearchProducts'})
    wrapper = mount(Search, {localVue, store, router, sync: false, attachToDocument: true})
    await wrapper.vm.$nextTick()
    searchForm.fields.featured.update(true)
    await wrapper.vm.$nextTick()
    await jest.runAllTimers()
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.$route.query).toEqual({featured: 'true'})
    // Should trigger the debounced function once and not change anything.
    searchForm.fields.featured.update(false)
    searchForm.fields.featured.update(true)
    await wrapper.vm.$nextTick()
    await jest.runAllTimers()
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.$route.query).toEqual({featured: 'true'})
  })
})
