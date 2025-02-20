<template>
  <ac-form-dialog :model-value="modelValue" @update:model-value="toggle" :large="true"
                  @submit.prevent="newUpload.submitThen(success)"
                  v-bind="newUpload.bind"
                  class="submission-uploader"
                  :fluid="true" v-if="isRegistered" :title="title"
  >
    <template v-slot:top-buttons/>
    <v-stepper v-model="newUpload.step" class="submission-stepper" non-linear>
      <v-stepper-header>
        <v-stepper-item editable :complete="newUpload.steps[1].complete" :value="1" :rules="newUpload.steps[1].rules">
          <template v-slot:title>Content</template>
        </v-stepper-item>
        <v-divider/>
        <v-stepper-item editable :value="2" :rules="newUpload.steps[2].rules" @submit.prevent="false">
          <template v-slot:title>Info</template>
        </v-stepper-item>
      </v-stepper-header>
      <v-stepper-window>
        <v-stepper-window-item :value="1">
          <v-row no-gutters>
            <v-col cols="12">
              <ac-bound-field :field="newUpload.fields.file" field-type="ac-uppy-file" label="Upload your submission"
                              :show-reset="true"
                              uppy-id="new-submission-file"/>
            </v-col>
            <v-col cols="12" v-if="addThumbnail">
              <ac-bound-field :field="newUpload.fields.preview" field-type="ac-uppy-file"
                              label="Upload a preview image (Optional)"
                              :show-reset="true"
                              uppy-id="new-submission-file-preview"/>
            </v-col>
            <v-col cols="12" v-else>
              <v-row no-gutters>
                <v-col cols="12" md="6" lg="4" offset-md="3" offset-lg="4" class="text-center">
                  <v-checkbox label="Upload custom thumbnail?" v-model="addThumbnail" class="d-inline-block"/>
                </v-col>
              </v-row>
            </v-col>
            <v-col cols="12">
              <ac-bound-field :field="newUpload.fields.rating" label="Content Ratings" field-type="ac-rating-field"/>
            </v-col>
            <v-col cols="12">
              <ac-bound-field :field="newUpload.fields.tags" field-type="ac-tag-field" label="Tags"
                              hint="Please add a few tags for this submission."/>
            </v-col>
            <v-col cols="12" md="6">
              <ac-bound-field :field="newUpload.fields.artists"
                              v-if="subject"
                              :init-items="preloadedUser"
                              field-type="ac-user-select" label="Artists"
                              hint="Tag the artist(s) that have worked on this piece. If they don't have an Artconomy account, you can skip this step.">
              </ac-bound-field>
            </v-col>
            <v-col cols="12" md="6">
              <ac-bound-field :field="newUpload.fields.characters"
                              v-if="showCharacters"
                              :init-items="characterInitItems"
                              field-type="ac-character-select" label="Characters"
                              hint="Tag the character(s) featured in this piece. If they're not listed on Artconomy, you can skip this step."/>
            </v-col>
          </v-row>
        </v-stepper-window-item>
        <v-stepper-window-item :value="2">
          <v-row no-gutters>
            <v-col cols="12">
              <ac-bound-field :field="newUpload.fields.title" label="Title"
                              hint="What will you title this submission?"/>
            </v-col>
            <v-col cols="12">
              <ac-bound-field field-type="ac-editor" :field="newUpload.fields.caption" label="Caption"
                              hint="Tell viewers a little about the piece." :save-indicator="false"/>
            </v-col>
            <v-col class="px-2" cols="12" md="4">
              <ac-bound-field field-type="ac-checkbox" :field="newUpload.fields.private" label="Private"
                              hint="If checked, will not show this submission to anyone you've not explicitly shared it with."
                              :persistent-hint="true"
              />
            </v-col>
            <v-col class="px-2" cols="12" md="4">
              <ac-bound-field field-type="ac-checkbox" :field="newUpload.fields.comments_disabled"
                              label="Comments Disabled"
                              hint="If checked, prevents others from commenting on this submission."
                              :persistent-hint="true"
              />
            </v-col>
            <v-col class="px-2" cols="12" md="4">
              <v-checkbox label="I made dis!"
                          hint="If checked, tags you as an artist on this piece. You may still submit if this is not checked, but you won't be credited as the artist."
                          :persistent-hint="true"
                          v-if="subject"
                          v-model="isArtist"
              />
            </v-col>
          </v-row>
        </v-stepper-window-item>
      </v-stepper-window>
      <template v-slot:actions><span/></template>
    </v-stepper>
    <template v-slot:bottom-buttons>
      <v-card-actions row wrap>
        <v-spacer/>
        <div class="d-flex flex-shrink-1 justify-end align-end">
          <v-checkbox v-model="multiple" label="Keep uploading" v-if="allowMultiple" class="px-2 flex-shrink-1"
                      :hide-details="true"/>
        </div>
        <v-btn @click.prevent="toggle(false)" variant="flat">Cancel</v-btn>
        <v-btn @click.prevent="newUpload.step -= 1" v-if="newUpload.step > 1" color="secondary" variant="flat">
          Previous
        </v-btn>
        <v-btn @click.prevent="newUpload.step += 1" v-if="newUpload.step < 2" color="primary" variant="flat">Next
        </v-btn>
        <v-btn type="submit" v-if="newUpload.step === 2" color="primary" class="submit-button" variant="flat">Submit
        </v-btn>
      </v-card-actions>
    </template>
  </ac-form-dialog>
</template>

<style>
.submission-stepper .v_messages__message {
  hyphens: unset
}
</style>

<script setup lang="ts">
import AcFormDialog from './wrappers/AcFormDialog.vue'
import AcBoundField from './fields/AcBoundField.ts'
import {useSubject} from '../mixins/subjective.ts'
import {useUpload} from '@/mixins/upload.ts'
import {newUploadSchema} from '@/lib/lib.ts'
import {computed, nextTick, ref} from 'vue'
import {useForm} from '@/store/forms/hooks.ts'
import {listenForSingle} from '@/store/singles/hooks.ts'
import {useRouter} from 'vue-router'
import {useViewer} from '@/mixins/viewer.ts'
import type {SubjectiveProps, Submission} from '@/types/main'
import {User} from '@/store/profiles/types/main'
import {Character} from '@/store/characters/types/main'

declare interface AcNewSubmissionsProps extends SubjectiveProps {
  showCharacters?: boolean,
  title?: string,
  modelValue: boolean,
  visit?: boolean,
  allowMultiple?: boolean,
  characterInitItems?: Character[],
}

const emit = defineEmits<{'update:modelValue': [boolean], success: [Submission]}>()

const props = withDefaults(defineProps<AcNewSubmissionsProps>(), {
  showCharacters: true,
  title: '',
  visit: true,
  allowMultiple: false,
  characterInitItems: () => [],
})

const {isRegistered} = useViewer()
const {subject, subjectHandler} = useSubject({ props })
const {showUpload} = useUpload()
const router = useRouter()

const addThumbnail = ref(false)
const multiple = ref(false)

const newUpload = useForm('newUpload', newUploadSchema(subjectHandler.user))
nextTick(() => {
  if (props.characterInitItems.length) {
    newUpload.fields.characters.model = props.characterInitItems.map((x) => x.id)
  }
})

const preloadedUser = computed(() => {
  return [subject.value]
})

const isArtist = computed({
  get() {
    /* istanbul ignore if */
    if (!subject.value) {
      return false
    }
    return newUpload.fields.artists.model.indexOf(subject.value.id) !== -1
  },
  set(val: boolean) {
    /* istanbul ignore if */
    if (!subject.value) {
      return
    }
    const artists = newUpload.fields.artists
    if (val && !artists.model.includes(subject.value.id)) {
      artists.model.push(subject.value.id)
    } else if (!val) {
      artists.model = artists.model.filter((artistId: number) => {
        return artistId !== (subject.value as User).id
      })
    }
  }
})

const toggle = (value: boolean) => {
  emit('update:modelValue', value)
}

const success = computed(() => {
  if (props.allowMultiple && multiple.value) {
    return (submission: Submission) => {
      const newValue = isArtist.value
      newUpload.reset()
      emit('success', submission)
      nextTick(() => {
        isArtist.value = newValue
      })
    }
  }
  return (submission: Submission) => {
    emit('success', submission)
    newUpload.reset()
    if (props.visit) {
      goToSubmission(submission)
    }
  }
})

const goToSubmission = (submission: Submission) => {
  showUpload.value = false
  router.push({
    name: 'Submission',
    params: {submissionId: submission.id + ''},
    query: {editing: 'true'},
  })
}

listenForSingle('new-submission-file')
listenForSingle('new-submission-file-preview')

defineExpose({isArtist, newUpload})
</script>
