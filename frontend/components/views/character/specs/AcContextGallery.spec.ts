import Vue from 'vue'
import {ArtStore, createStore} from '@/store'
import {mount, Wrapper} from '@vue/test-utils'
import AcContextGallery from '@/components/views/character/AcContextGallery.vue'
import {genCharacter} from '@/store/characters/specs/fixtures'
import {genSubmission} from '@/store/submissions/specs/fixtures'
import Submission from '@/types/Submission'
import {cleanUp, createVuetify, setViewer, vueSetup} from '@/specs/helpers'
import {genUser} from '@/specs/helpers/fixtures'
import {SingleController} from '@/store/singles/controller'
import {Vuetify} from 'vuetify'

const localVue = vueSetup()
let vuetify: Vuetify

describe('AcContextGallery.vue', () => {
  let store: ArtStore
  let wrapper: Wrapper<Vue>
  beforeEach(() => {
    store = createStore()
    vuetify = createVuetify()
  })
  afterEach(() => {
    cleanUp(wrapper)
  })
  it('Determines the featured submission', async() => {
    setViewer(store, genUser())
    wrapper = mount(
      AcContextGallery, {
        localVue,
        vuetify,
        store,
        propsData: {username: 'Fox', characterName: 'Kai'},
        mocks: {$route: {name: 'Character', params: {username: 'Fox', characterName: 'Kai'}, query: {}}},
        stubs: ['router-link'],
        sync: false,
      }
    )
    const vm = wrapper.vm as any
    const character = genCharacter()
    const primary = character.primary_submission as Submission
    const submissions = []
    for (let index = 0; index < 7; index++) {
      const submission = genSubmission()
      submission.id = submission.id + index + 1
      submissions.push(submission)
    }
    submissions.splice(2, 0, primary)
    vm.character.profile.setX(genCharacter())
    store.commit('characterModules/character__Fox__Kai/profile/setReady', true)
    vm.character.submissions.setList(submissions)
    store.commit('characterModules/character__Fox__Kai/submissions/setReady', true)
    await vm.$nextTick()
    expect(vm.featured.id).toBe(primary.id)
    let pruned = vm.prunedSubmissions.map(
      (submission: SingleController<Submission>) => (submission.x as Submission).id)
    expect(pruned.indexOf(primary.id + 1)).not.toBe(-1)
    expect(pruned.indexOf(primary.id)).toBe(-1)
    expect(pruned.length).toBe(4)
    const updatedCharacter = {...character}
    updatedCharacter.primary_submission = null
    vm.character.profile.setX(updatedCharacter)
    await vm.$nextTick()
    pruned = vm.prunedSubmissions.map(
      (submission: SingleController<Submission>) => (submission.x as Submission).id)
    expect(pruned.indexOf(primary.id + 1)).toBe(-1)
    expect(pruned.indexOf(primary.id)).not.toBe(-1)
    expect(pruned.length).toBe(4)
    expect(vm.featured.id).toBe(primary.id + 1)
  })
})
