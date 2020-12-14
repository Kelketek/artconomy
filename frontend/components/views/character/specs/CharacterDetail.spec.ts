import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import {mount, Wrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import {cleanUp, createVuetify, docTarget, rq, rs, setViewer, vueSetup} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import Router from 'vue-router'
import mockAxios from '@/__mocks__/axios'
import {User} from '@/store/profiles/types/User'
import CharacterDetail from '@/components/views/character/CharacterDetail.vue'
import Empty from '@/specs/helpers/dummy_components/empty.vue'
import {genCharacter} from '@/store/characters/specs/fixtures'
import Submission from '@/types/Submission'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import {searchSchema} from '@/lib/lib'

const localVue = vueSetup()
localVue.use(Router)
let store: ArtStore
let wrapper: Wrapper<Vue>
let router: Router
let vulpes: User
let vuetify: Vuetify

describe('CharacterDetail.vue', () => {
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
    vulpes = genUser()
    vulpes.username = 'Vulpes'
    vulpes.is_staff = false
    vulpes.is_superuser = false
    vulpes.id = 2
    vulpes.artist_mode = false
    router = new Router({
      mode: 'history',
      routes: [
        {
          path: '/profile/:username',
          component: Empty,
          props: true,
          children: [{
            path: 'about',
            name: 'AboutUser',
            component: Empty,
            props: true,
          }],
        }, {
          path: '/submissions/:submissionId',
          name: 'Submission',
          component: Empty,
          props: true,
        }, {
          path: '/search/characters/',
          name: 'SearchCharacters',
          component: Empty,
          props: true,
        },
      ],
    })
    mount(Empty, {localVue, store}).vm.$getForm('search', searchSchema())
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Mounts and fetches a character', async() => {
    setViewer(store, vulpes)
    wrapper = mount(CharacterDetail, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {username: 'Vulpes', characterName: 'Kai'},

      attachTo: docTarget(),
    },
    )
    await wrapper.vm.$nextTick()
    expect(mockAxios.get).toHaveBeenCalledWith(
      ...rq('/api/profiles/v1/account/Vulpes/characters/Kai/', 'get'),
    )
    expect(mockAxios.get).toHaveBeenCalledWith(
      ...rq('/api/profiles/v1/account/Vulpes/characters/Kai/attributes/', 'get',
        undefined, {cancelToken: expect.any(Object)}))
    expect(mockAxios.get).toHaveBeenCalledWith(
      ...rq('/api/profiles/v1/account/Vulpes/characters/Kai/colors/', 'get',
        undefined, {cancelToken: expect.any(Object)}))
    expect(mockAxios.get).toHaveBeenCalledWith(
      ...rq('/api/profiles/v1/account/Vulpes/characters/Kai/share/', 'get',
        undefined, {cancelToken: expect.any(Object)}))
    mockAxios.mockResponse(rs(genCharacter()))
    mockAxios.mockResponse(rs([]))
    mockAxios.mockResponse(rs([]))
    mockAxios.mockResponse(rs([]))
    await wrapper.vm.$nextTick()
  })
  it('Produces a relevant link to the primary submission', async() => {
    setViewer(store, vulpes)
    wrapper = mount(CharacterDetail, {
      localVue,
      store,
      router,
      vuetify,
      propsData: {username: 'Vulpes', characterName: 'Kai'},

      attachTo: docTarget(),
    },
    )
    const character = genCharacter();
    (character.primary_submission as Submission).id = 100
    const vm = wrapper.vm as any
    vm.character.profile.setX(character)
    await vm.$nextTick()
    expect(vm.primarySubmissionLink).toEqual({name: 'Submission', params: {submissionId: 100}})
    vm.character.profile.updateX({primary_submission: null})
    expect(vm.primarySubmissionLink).toBe(null)
    const submission = genSubmission()
    submission.id = 101
    vm.character.profile.updateX({primary_submission: submission})
    await vm.$nextTick()
    expect(vm.primarySubmissionLink).toEqual({name: 'Submission', params: {submissionId: 101}})
    router.replace({query: {editing: 'true'}})
    await vm.$nextTick()
    expect(vm.primarySubmissionLink).toBe(null)
  })
})
