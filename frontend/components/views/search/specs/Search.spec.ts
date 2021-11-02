import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import Router from 'vue-router'
import {cleanUp, createVuetify, docTarget, genAnon, mount, setViewer, vueSetup} from '@/specs/helpers'
import {ArtStore, createStore} from '@/store'
import {Wrapper} from '@vue/test-utils'
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
import {genUser} from '@/specs/helpers/fixtures'
import {Ratings} from '@/store/profiles/types/Ratings'
import SubmissionExtra from '@/components/views/search/extra/SubmissionExtra.vue'

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
            extra: SubmissionExtra,
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
      }, {
        name: 'SessionSettings',
        path: '/settings/',
        component: Empty,
        props: true,
      }, {
        name: 'Options',
        path: '/profile/:username/settings/options',
        component: Empty,
        props: true,
      }],
    })
    searchForm = mount(Empty, {
      localVue,
      store,
      vuetify,
    }).vm.$getForm('search', searchSchema())
    store.commit('setSearchInitialized', true)
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts', () => {
    wrapper = mount(Search, {localVue, store, vuetify, router, attachTo: docTarget()})
  })
  it('Tabs through each search option', async() => {
    setViewer(store, genUser())
    wrapper = mount(Search, {localVue, store, vuetify, router, attachTo: docTarget()})
    const routes = ['SearchProducts', 'SearchSubmissions', 'SearchCharacters', 'SearchProfiles']
    for (const [index, el] of wrapper.findAll('.v-item-group .v-btn').wrappers.entries()) {
      el.trigger('click')
      await wrapper.vm.$nextTick()
      expect(wrapper.vm.$route.name).toBe(routes[index])
    }
  })
  it('Opens the default view', async() => {
    setViewer(store, genUser())
    router.push({name: 'Search'})
    searchForm.fields.featured.update(true)
    wrapper = mount(Search, {localVue, store, vuetify, router, attachTo: docTarget()})
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.$route.name).toBe('SearchProducts')
  })
  it('Updates the route when the values change', async() => {
    setViewer(store, genUser())
    router.push({name: 'SearchProducts'})
    wrapper = mount(SearchProducts, {localVue, store, vuetify, router, attachTo: docTarget()})
    const vm = wrapper.vm as any
    const mockUpdate = jest.spyOn(vm, 'debouncedUpdate')
    mockUpdate.mockImplementation(vm.rawUpdate)
    await wrapper.vm.$nextTick()
    searchForm.fields.featured.update(true)
    await wrapper.vm.$nextTick()
    expect(wrapper.vm.$route.query).toEqual({featured: 'true', page: '1', size: '24'})
  })
  it('Shows an alert when an anonymous user has a max rating under the current search', async() => {
    router.push({name: 'SearchProducts'})
    setViewer(store, genAnon())
    wrapper = mount(Search, {localVue, store, vuetify, router, attachTo: docTarget(), stubs: ['v-badge']})
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(wrapper.find('.v-alert').exists()).toBe(false)
    searchForm.fields.minimum_content_rating.update('3')
    await vm.$nextTick()
    expect(wrapper.find('.v-alert').exists()).toBe(true)
    expect(wrapper.find('.v-alert .rating-button').exists()).toBe(true)
  })
  it('Shows an alert when a registered user has a max rating under the current search', async() => {
    router.push({name: 'SearchSubmissions'})
    searchForm.fields.content_ratings.update('2,3')
    setViewer(store, genUser({username: 'Fox', rating: Ratings.GENERAL}))
    wrapper = mount(Search, {localVue, store, vuetify, router, attachTo: docTarget(), stubs: ['v-badge']})
    const vm = wrapper.vm as any
    await vm.$nextTick()
    expect(wrapper.find('.v-alert').exists()).toBe(true)
    expect(wrapper.find('.v-alert .rating-button').exists()).toBe(true)
  })
  it('Properly handles setting and getting the allowed content ratings', async() => {
    setViewer(store, genUser())
    wrapper = mount(SubmissionExtra, {localVue, store, vuetify, router, attachTo: docTarget(), stubs: ['v-badge']})
    const vm = wrapper.vm as any
    vm.contentRatings = ['1', '3', '0']
    expect(vm.contentRatings).toEqual(['0', '1', '3'])
    expect(searchForm.fields.content_ratings.value).toBe('0,1,3')
  })
  it('Synchronizes the value of the form page value and the list page value', async() => {
    wrapper = mount(SearchProducts, {localVue, store, vuetify, router, attachTo: docTarget()})
    const vm = wrapper.vm as any
    vm.list.currentPage = 3
    await vm.$nextTick()
    expect(vm.searchForm.fields.page.value).toEqual(3)
  })
})
