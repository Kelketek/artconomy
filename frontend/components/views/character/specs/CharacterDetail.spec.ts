import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store'
import {
  cleanUp,
  createVuetify,
  docTarget,
  flushPromises,
  mount,
  rq,
  setViewer,
  vueSetup,
  VuetifyWrapped,
} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import {Router, createRouter, createWebHistory} from 'vue-router'
import mockAxios from '@/__mocks__/axios'
import {User} from '@/store/profiles/types/User'
import CharacterDetail from '@/components/views/character/CharacterDetail.vue'
import Empty from '@/specs/helpers/dummy_components/empty'
import {genCharacter} from '@/store/characters/specs/fixtures'
import Submission from '@/types/Submission'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import {searchSchema} from '@/lib/lib'
import {describe, expect, beforeEach, afterEach, test, vi} from 'vitest'

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router
let vulpes: User

const WrappedCharacterDetail = VuetifyWrapped(CharacterDetail)

describe('CharacterDetail.vue', () => {
  beforeEach(() => {
    store = createStore()
    vulpes = genUser()
    vulpes.username = 'Vulpes'
    vulpes.is_staff = false
    vulpes.is_superuser = false
    vulpes.id = 2
    vulpes.artist_mode = false
    router = createRouter({
      history: createWebHistory(),
      routes: [
        {
          path: '/',
          component: Empty,
          name: 'Home',
        },
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
        {
          path: '/profile/:username/characters/:characterName',
          name: 'Character',
          component: Empty,
          props: true,
        },
      ],
    })
    mount(Empty, vueSetup({store})).vm.$getForm('search', searchSchema())
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Mounts and fetches a character', async() => {
    setViewer(store, vulpes)
    wrapper = mount(WrappedCharacterDetail, {
      ...vueSetup({
        store,
        extraPlugins: [router],
      }),
      props: {
        username: 'Vulpes',
        characterName: 'Kai',
      },
    })
    await wrapper.vm.$nextTick()
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/api/profiles/account/Vulpes/characters/Kai/', 'get'),
    )
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/api/profiles/account/Vulpes/characters/Kai/attributes/', 'get',
        undefined, {signal: expect.any(Object)}))
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/api/profiles/account/Vulpes/characters/Kai/colors/', 'get',
        undefined, {signal: expect.any(Object)}))
    expect(mockAxios.request).toHaveBeenCalledWith(
      rq('/api/profiles/account/Vulpes/characters/Kai/share/', 'get',
        undefined, {signal: expect.any(Object)}))
    const vm = wrapper.vm.$refs.vm as any
    vm.character.profile.makeReady(genCharacter())
    vm.character.attributes.makeReady([])
    vm.character.colors.makeReady([])
    vm.character.submissions.makeReady([])
    await wrapper.vm.$nextTick()
  })
  test('Produces a relevant link to the primary submission', async() => {
    setViewer(store, vulpes)
    wrapper = mount(WrappedCharacterDetail, {
      ...vueSetup({
        store,
        extraPlugins: [router],
      }),
      props: {
        username: 'Vulpes',
        characterName: 'Kai',
      },
    })
    await router.replace({
      name: 'Character',
      params: {
        username: 'Fox',
        characterName: 'Kai',
      },
    })
    const character = genCharacter();
    (character.primary_submission as Submission).id = 100
    const vm = wrapper.vm.$refs.vm as any
    vm.character.profile.setX(character)
    await vm.$nextTick()
    expect(vm.primarySubmissionLink).toEqual({
      name: 'Submission',
      params: {submissionId: 100},
    })
    vm.character.profile.updateX({primary_submission: null})
    expect(vm.primarySubmissionLink).toBe(null)
    const submission = genSubmission()
    submission.id = 101
    vm.character.profile.updateX({primary_submission: submission})
    await vm.$nextTick()
    expect(vm.primarySubmissionLink).toEqual({
      name: 'Submission',
      params: {submissionId: 101},
    })
    await router.replace({query: {editing: 'true'}})
    await vm.$nextTick()
    expect(vm.primarySubmissionLink).toBe(null)
  })
  test('Does not break setting meta information if the primary submission is not set', async() => {
    setViewer(store, vulpes)
    wrapper = mount(WrappedCharacterDetail, {
      ...vueSetup({
        store,
        extraPlugins: [router],
      }),
      props: {
        username: 'Vulpes',
        characterName: 'Kai',
      },
    })
    const character = genCharacter()
    character.primary_submission = null
    const vm = wrapper.vm.$refs.vm as any
    vm.character.profile.setX(character)
    await wrapper.vm.$nextTick()
  })
  test('Handles a new submission when the primary is being changed', async() => {
    setViewer(store, vulpes)
    wrapper = mount(WrappedCharacterDetail, {
      ...vueSetup({
        store,
        extraPlugins: [router],
      }),
      props: {
        username: 'Vulpes',
        characterName: 'Kai',
      },
    })
    const character = genCharacter()
    character.primary_submission = null
    const vm = wrapper.vm.$refs.vm as any
    vm.character.profile.setX(character)
    vm.submissionList.makeReady([])
    vm.showChangePrimary = true
    await wrapper.vm.$nextTick()
    expect(vm.character.profile.patchers.primary_submission.model).toBe(null)
    const submission = genSubmission({id: 343})
    vm.addSubmission(submission)
    expect(vm.character.profile.patchers.primary_submission.model).toBe(submission.id)
    expect(vm.submissionList.list[0].x.id).toBe(submission.id)
    expect(vm.character.submissions.list[0].x.id).toBe(submission.id)
  })
  test('Handles a new submission when the primary is not being changed', async() => {
    setViewer(store, vulpes)
    wrapper = mount(WrappedCharacterDetail, {
      ...vueSetup({
        store,
        extraPlugins: [router],
      }),
      props: {
        username: 'Vulpes',
        characterName: 'Kai',
      },
    })
    const character = genCharacter()
    character.primary_submission = null
    const vm = wrapper.vm.$refs.vm as any
    vm.character.profile.setX(character)
    vm.submissionList.makeReady([])
    await wrapper.vm.$nextTick()
    expect(vm.character.profile.patchers.primary_submission.model).toBe(null)
    const submission = genSubmission({id: 343})
    vm.addSubmission(submission)
    expect(vm.character.profile.patchers.primary_submission.model).toBe(null)
  })
})
