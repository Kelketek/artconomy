<template>
  <v-container>
    <ac-character-toolbar :username="username" :character-name="characterName" :character-avatar="false"
                          :show-edit="true" ref="toolbar" @success="addSubmission" :visit="!showChangePrimary"/>
    <ac-load-section :controller="character.profile" tag="v-layout" class="mt-3">
      <template v-slot:default>
        <v-card class="mb-2" v-if="character.profile.x">
          <v-card-text>
            <v-row no-gutters>
              <v-col cols="12" sm="8" md="7" lg="8" xl="9">
                <v-card-title primary-title>
                  <h1 v-show="!editing">{{character.profile.x.name}}</h1>
                  <ac-patch-field
                      :patcher="character.profile.patchers.name" :persistant-hint="true"
                      v-show="editing"
                      v-if="controls"
                      :auto-save="false"
                      :enter-save="true"
                      label="Name"
                      hint="WARNING: Changing this character's name will change the URL of the
                  character, which can affect SEO."
                  />
                </v-card-title>
                <ac-attributes :username="username" :character-name="characterName"/>
                <ac-tag-display
                    :patcher="character.profile.patchers.tags"
                    :editable="tagControls"
                    :username="username"
                    scope="Characters"
                />
              </v-col>
              <v-col cols="12" sm="4" md="4" lg="3" xl="2" offset-md="1">
                <v-row no-gutters align-content="center" align="center" justify="center">
                  <v-col align-self="center" class="primary-submission-container">
                    <ac-link :to="primarySubmissionLink">
                      <ac-asset :asset="character.profile.x.primary_submission"
                                thumb-name="thumbnail" :terse="true"
                                :aspect-ratio="1"
                                :editing="editing"
                                class="primary-submission"
                                v-model="showChangePrimary"
                                :alt="primarySubmissionText"
                      >
                        <template v-slot:edit-menu>
                          <ac-expanded-property v-model="showChangePrimary" :large="true">
                            <template v-slot:title>Change Showcase Submission</template>
                            <v-row>
                              <v-col cols="12" class="text-center">
                                <!-- @vue-ignore -->
                                <v-btn color="green" variant="flat" class="upload-button" @click="$refs.toolbar.showUpload = true">
                                  <v-icon left :icon="mdiUpload"/>
                                  Upload new Submission
                                </v-btn>
                              </v-col>
                              <v-col cols="12">
                                <ac-patch-field
                                    field-type="ac-submission-select"
                                    :patcher="character.profile.patchers.primary_submission"
                                    :list="submissionList"
                                    v-if="submissionList"
                                    :save-comparison="character.profile.x.primary_submission"
                                    :show-progress="true"
                                />
                              </v-col>
                            </v-row>
                            <template v-slot:actions>
                              <v-spacer/>
                              <v-btn color="danger" v-if="character.profile.x.primary_submission"
                                     variant="flat"
                                     @click="character.profile.patch({primary_submission: null})">Clear Showcased Image
                              </v-btn>
                              <v-btn color="primary" variant="flat" @click="showChangePrimary = false">Cancel</v-btn>
                            </template>
                          </ac-expanded-property>
                        </template>
                      </ac-asset>
                    </ac-link>
                  </v-col>
                </v-row>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
        <v-card v-if="character.profile.x">
          <v-card-text>
            <v-card-title primary-title><h2>About {{character.profile.x.name}}</h2></v-card-title>
            <ac-patch-field
                field-type="ac-editor"
                :auto-save="false"
                :patcher="character.profile.patchers.description"
                v-if="controls"
                v-show="editing"
                :save-comparison="character.profile.patchers.description.rawValue"/>
            <ac-rendered :value="character.profile.patchers.description.rawValue" v-show="!editing"/>
          </v-card-text>
        </v-card>
        <ac-colors :username="username" :character-name="characterName"/>
        <v-card v-if="character.profile.x && (editing || character.profile.x.open_requests)" class="mt-3">
          <v-card-text>
            <v-row no-gutters class="mb-2">
              <ac-patch-field field-type="ac-checkbox"
                              hint="If this is checked, permits others to commission art involving your characters."
                              label="Open Requests"
                              :persistent-hint="true"
                              v-if="controls"
                              v-show="editing"
                              :save-indicator="false"
                              :patcher="character.profile.patchers.open_requests"
              />
              <v-col cols="12" v-if="character.profile.x.open_requests" v-show="!editing">
                <h3>
                  <v-icon left color="green" :icon="mdiCheckCircle"/>
                  Character can be used in other people's commissions
                </h3>
              </v-col>
            </v-row>
            <v-row no-gutters>
              <v-col cols="12" v-show="editing" v-if="controls">
                <ac-patch-field
                    field-type="ac-editor"
                    :auto-save="false"
                    :patcher="character.profile.patchers.open_requests_restrictions"
                    label="Restrictions"
                    hint="Write any restrictions you wish to place on having your character commissioned by others.
                  For instance, if your character would never eat pie, you could write, 'Don't draw them eating pie.'"
                    :disabled="!character.profile.patchers.open_requests.model"
                    :save-comparison="character.profile.x.open_requests_restrictions"/>
              </v-col>
              <v-col cols="12" v-if="character.profile.x.open_requests_restrictions" v-show="!editing">
                <h4 class="mb-2">
                  <v-icon color="yellow" left :icon="mdiAlert"/>
                  With the following restrictions:
                </h4>
                <ac-rendered :value="character.profile.x.open_requests_restrictions"/>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
        <ac-context-gallery
            class="mt-3"
            :username="username" :character-name="characterName"
        />
        <v-row no-gutters>
          <v-col cols="12" class="pt-5">
            <v-toolbar color="secondary" dense>
              <v-toolbar-title>You might also like...</v-toolbar-title>
            </v-toolbar>
            <v-card :color="current.colors['well-darken-4']">
              <v-card-text class="px-0" v-if="character.recommended">
                <ac-load-section :controller="character.recommended">
                  <template v-slot:default>
                    <v-row no-gutters>
                      <v-col cols="6" sm="4" md="3" lg="2" v-for="char in character.recommended.list" :key="char.x!.id"
                             class="pa-1">
                        <ac-character-preview :character="char.x!" :mini="true"/>
                      </v-col>
                    </v-row>
                  </template>
                </ac-load-section>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </template>
    </ac-load-section>
  </v-container>
</template>

<script setup lang="ts">
import AcAsset from '@/components/AcAsset.vue'
import {useSubject} from '@/mixins/subjective.ts'
import {Character} from '@/store/characters/types/Character.ts'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcRendered from '@/components/wrappers/AcRendered.ts'
import {useEditable} from '@/mixins/editable.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcAttributes from '@/components/views/character/AcAttributes.vue'
import AcColors from '@/components/views/character/AcColors.vue'
import AcTagDisplay from '@/components/AcTagDisplay.vue'
import AcContextGallery from '@/components/views/character/AcContextGallery.vue'
import Submission from '@/types/Submission.ts'
import AcLink from '@/components/wrappers/AcLink.vue'
import AcCharacterToolbar from '@/components/views/character/AcCharacterToolbar.vue'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import {setMetaContent, updateTitle} from '@/lib/lib.ts'
import AcCharacterPreview from '@/components/AcCharacterPreview.vue'
import {CharacterProps} from '@/types/CharacterProps.ts'
import {useCharacter} from '@/store/characters/hooks.ts'
import {useErrorHandling} from '@/mixins/ErrorHandling.ts'
import {useList} from '@/store/lists/hooks.ts'
import {computed, ref, watch} from 'vue'
import {useViewer} from '@/mixins/viewer.ts'
import {textualize} from '@/lib/markdown.ts'
import {mdiCheckCircle, mdiAlert, mdiUpload} from '@mdi/js'
import {useTheme} from 'vuetify'

const props = defineProps<CharacterProps>()

const {setError} = useErrorHandling()
const {controls} = useSubject(props)
const {editing} = useEditable(controls)
const {ageCheck, isRegistered} = useViewer()
const toolbar = ref(null)
const {current} = useTheme()

const character = useCharacter(props)
character.profile.get().catch(setError)
character.attributes.firstRun()
character.colors.firstRun()
character.sharedWith.firstRun()
character.recommended.firstRun()
const submissionList = useList('characterSubmissions', {endpoint: character.submissions.endpoint})

const tagControls = computed(() => {
  return (controls.value || character.profile.x?.user.taggable) && isRegistered.value
})

const primarySubmissionLink = computed(() => {
  if (editing.value) {
    return null
  }
  const profile = character.profile.x
  if (!profile) {
    return null
  }
  if (!profile.primary_submission) {
    return null
  }
  return {
    name: 'Submission',
    params: {submissionId: profile.primary_submission.id},
  }
})

const showChangePrimary = ref(false)

watch(() => character.profile.x?.primary_submission?.id, (newValue, oldValue) => {
  showChangePrimary.value = false
})

const addSubmission = (submission: Submission) => {
  if (showChangePrimary.value) {
    if (submissionList.empty) {
      // @ts-expect-error
      character.profile.patchers.primary_submission.model = submission.id
    }
  }
  submissionList.unshift(submission)
  character.submissions.unshift(submission)
}

const primarySubmissionText = computed(() => {
  if (character.profile.x && character.profile.x.primary_submission) {
    const title = character.profile.x.primary_submission.title
    if (!title) {
      return `Untitled Focus Submission for ${character.profile.name}`
    }
    return `Focus Submission for ${character.profile.name} titled: ${title}`
  }
  return ''
})

watch(() => character.profile.x, (character: Character|null) => {
  /* istanbul ignore if */
  if (!character) {
    return
  }
  updateTitle(`${character.name} - ${character.user.username} on Artconomy.com`)
  setMetaContent('description', textualize(character.description).slice(0, 160))
  if (!character.primary_submission) {
    if (character.nsfw) {
      // Adult content rating by default.
      ageCheck({value: 2})
    }
    return
  }
  ageCheck({value: character.primary_submission.rating})
}, {deep: true, immediate: true})
</script>
