import {VueWrapper} from '@vue/test-utils'
import {ArtStore, createStore} from '@/store/index.ts'
import {
  cleanUp, createTestRouter,
  mount,
  rq,
  vueSetup,
  VuetifyWrapped,
} from '@/specs/helpers/index.ts'
import {genUser} from '@/specs/helpers/fixtures.ts'
import {Router} from 'vue-router'
import mockAxios from '@/__mocks__/axios.ts'
import {User} from '@/store/profiles/types/User.ts'
import CharacterDetail from '@/components/views/character/CharacterDetail.vue'
import Empty from '@/specs/helpers/dummy_components/empty.ts'
import {genCharacter} from '@/store/characters/specs/fixtures.ts'
import Submission from '@/types/Submission.ts'
import {genSubmission} from '@/store/submissions/specs/fixtures.ts'
import {searchSchema, setViewer} from '@/lib/lib.ts'
import {describe, expect, beforeEach, afterEach, test} from 'vitest'
import {nextTick} from 'vue'
import AcCharacterToolbar from '@/components/views/character/AcCharacterToolbar.vue'

let store: ArtStore
let wrapper: VueWrapper<any>
let router: Router
let vulpes: User
let empty: VueWrapper<any>['vm']

const WrappedCharacterDetail = VuetifyWrapped(CharacterDetail)

const getCharacter = () => {
  return empty.$getCharacter(`character__Vulpes__Kai`)
}

describe('CharacterDetail.vue', () => {
  beforeEach(() => {
    store = createStore()
    vulpes = genUser()
    vulpes.username = 'Vulpes'
    vulpes.is_staff = false
    vulpes.is_superuser = false
    vulpes.id = 2
    vulpes.artist_mode = false
    router = createTestRouter()
    empty = mount(Empty, vueSetup({store})).vm
    empty.$getForm('search', searchSchema())
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  test('Mounts and fetches a character', async() => {
    setViewer({store, user: vulpes})
    wrapper = mount(WrappedCharacterDetail, {
      ...vueSetup({
        store,
        router,
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
    const character = getCharacter()
    character.profile.makeReady(genCharacter())
    character.attributes.makeReady([])
    character.colors.makeReady([])
    character.submissions.makeReady([])
    await nextTick()
  })
  test('Produces a relevant link to the primary submission', async() => {
    setViewer({ store, user: vulpes })
    wrapper = mount(WrappedCharacterDetail, {
      ...vueSetup({
        store,
router,
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
    const characterDef = genCharacter();
    (characterDef.primary_submission as Submission).id = 100
    const character = getCharacter()
    character.profile.makeReady(characterDef)
    await nextTick()
    expect(wrapper.find('.primary-submission-container a').attributes()['href']).toEqual('/submissions/100/')
    character.profile.updateX({primary_submission: null})
    await nextTick()
    expect(wrapper.find('.primary-submission-container a').exists()).toBe(false)
    const submission = genSubmission()
    submission.id = 101
    character.profile.updateX({primary_submission: submission})
    await nextTick()
    expect(wrapper.find('.primary-submission-container a').attributes()['href']).toEqual('/submissions/101/')
    await router.replace({query: {editing: 'true'}})
    await nextTick()
    expect(wrapper.find('.primary-submission-container a').exists()).toBe(false)
  })
  test('Does not break setting meta information if the primary submission is not set', async() => {
    setViewer({ store, user: vulpes })
    wrapper = mount(WrappedCharacterDetail, {
      ...vueSetup({
        store,
router,
      }),
      props: {
        username: 'Vulpes',
        characterName: 'Kai',
      },
    })
    const characterDef = genCharacter()
    characterDef.primary_submission = null
    const character = getCharacter()
    character.profile.setX(characterDef)
    await wrapper.vm.$nextTick()
  })
  test('Handles a new submission when the primary is being changed', async() => {
    setViewer({ store, user: vulpes })
    wrapper = mount(WrappedCharacterDetail, {
      ...vueSetup({
        store,
router,
      }),
      props: {
        username: 'Vulpes',
        characterName: 'Kai',
      },
    })
    await router.replace({query: {editing: 'true'}})
    const characterDef = genCharacter()
    characterDef.primary_submission = null
    const character = getCharacter()
    character.profile.makeReady(characterDef)
    const submissionList = empty.$getList('characterSubmissions')
    submissionList.makeReady([])
    await nextTick()
    await wrapper.find('.primary-submission .edit-overlay').trigger('click')
    await nextTick()
    expect(character.profile.patchers.primary_submission.model).toBe(null)
    const submission = genSubmission({id: 343})
    await wrapper.findComponent(AcCharacterToolbar).vm.$emit('success', submission)
    expect(character.profile.patchers.primary_submission.model).toBe(submission.id)
    expect(submissionList.list[0].x.id).toBe(submission.id)
    expect(character.submissions.list[0].x.id).toBe(submission.id)
  })
  test('Handles a new submission when the primary is not being changed', async() => {
    setViewer({ store, user: vulpes })
    wrapper = mount(WrappedCharacterDetail, {
      ...vueSetup({
        store,
router,
      }),
      props: {
        username: 'Vulpes',
        characterName: 'Kai',
      },
    })
    await router.replace({query: {editing: 'true'}})
    const characterDef = genCharacter()
    characterDef.primary_submission = null
    const character = getCharacter()
    character.profile.setX(characterDef)
    const submissionList = empty.$getList('characterSubmissions')
    submissionList.makeReady([])
    await wrapper.vm.$nextTick()
    expect(character.profile.patchers.primary_submission.model).toBe(null)
    const submission = genSubmission({id: 343})
    await wrapper.findComponent(AcCharacterToolbar).vm.$emit('success', submission)
    expect(character.profile.patchers.primary_submission.model).toBe(null)
    expect(submissionList.list[0].x).toEqual(submission)
  })
})
