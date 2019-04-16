<template>
  <ac-form-dialog :value="value" @input="toggle" :large="true" @submit.prevent="newUpload.submitThen(success)"
                  v-bind="newUpload.bind"
                  :fluid="true" v-if="isRegistered" :title="title"
  >
    <template slot="top-buttons"></template>
    <v-stepper v-model="newUpload.step" class="submission-stepper" non-linear>
      <v-stepper-header>
        <v-stepper-step editable :complete="newUpload.steps[1].complete" :step="1" :rules="newUpload.steps[1].rules">Basics</v-stepper-step>
        <v-divider />
        <v-stepper-step editable :complete="newUpload.steps[2].complete" :step="2" :rules="newUpload.steps[2].rules">Meta</v-stepper-step>
        <v-divider />
        <v-stepper-step editable :step="3" :rules="newUpload.steps[3].rules">Content</v-stepper-step>
      </v-stepper-header>
      <v-stepper-items>
        <v-stepper-content :step="1">
          <v-layout row wrap>
            <v-flex xs12>
              <ac-bound-field :field="newUpload.fields.title" label="Title" hint="What will you title this submission?" />
            </v-flex>
            <v-flex xs12>
              <ac-bound-field field-type="ac-editor" :field="newUpload.fields.caption" label="Caption" hint="Tell viewers a little about the piece." :save-indicator="false" />
            </v-flex>
            <v-flex xs12 md4 px-2>
              <ac-bound-field field-type="v-checkbox" :field="newUpload.fields.private" label="Private"
                              hint="If checked, will not show this submission to anyone you've not explicitly shared it with."
                              :persistent-hint="true"
              />
            </v-flex>
            <v-flex xs12 md4 px-2>
              <ac-bound-field field-type="v-checkbox" :field="newUpload.fields.comments_disabled" label="Comments Disabled"
                              hint="If checked, prevents others from commenting on this submission."
                              :persistent-hint="true"
              />
            </v-flex>
            <v-flex xs12 md4 px-2>
              <v-checkbox label="I made dis!"
                          hint="If checked, tags you as an artist on this piece. You may still submit if this is not checked, but you won't be credited as the artist."
                          :persistent-hint="true"
                          v-if="subject"
                          v-model="isArtist"
              />
            </v-flex>
          </v-layout>
        </v-stepper-content>
        <v-stepper-content :step="2">
          <v-layout row wrap>
            <v-flex xs12>
              <ac-bound-field :field="newUpload.fields.rating" label="Content Rating" field-type="ac-rating-field"></ac-bound-field>
            </v-flex>
            <v-flex xs12>
              <ac-bound-field :field="newUpload.fields.tags" field-type="ac-tag-field" label="Tags" hint="Please add a few tags for this submission."></ac-bound-field>
            </v-flex>
            <v-flex xs12 md6>
              <ac-bound-field :field="newUpload.fields.artists"
                              v-if="subject"
                              :init-items="preloadedUser"
                              field-type="ac-user-select" label="Artists"
                              hint="Tag the artist(s) that have worked on this piece. If they don't have an Artconomy account, you can skip this step.">
              </ac-bound-field>
            </v-flex>
            <v-flex xs12 md6>
              <ac-bound-field :field="newUpload.fields.characters"
                              v-if="showCharacters"
                              :init-items="characterInitItems"
                              field-type="ac-character-select" label="Characters"
                              hint="Tag the character(s) featured in this piece. If they're not listed on Artconomy, you can skip this step." />
            </v-flex>
          </v-layout>
        </v-stepper-content>
        <v-stepper-content :step="3">
          <v-layout row wrap>
            <v-flex xs12 md6>
              <ac-bound-field :field="newUpload.fields.file" field-type="ac-uppy-file" label="Upload your submission"></ac-bound-field>
            </v-flex>
            <v-flex xs12 md6>
              <ac-bound-field :field="newUpload.fields.preview" field-type="ac-uppy-file" label="Upload a preview image (Optional)"></ac-bound-field>
            </v-flex>
          </v-layout>
        </v-stepper-content>
      </v-stepper-items>
    </v-stepper>
    <template slot="bottom-buttons">
      <v-card-actions row wrap>
        <v-spacer></v-spacer>
        <v-btn @click.prevent="toggle(false)">Cancel</v-btn>
        <v-btn @click.prevent="newUpload.step -= 1" v-if="newUpload.step > 1" color="secondary">Previous</v-btn>
        <v-btn @click.prevent="newUpload.step += 1" v-if="newUpload.step < 3" color="primary">Next</v-btn>
        <v-btn type="submit" v-if="newUpload.step === 3" color="primary" class="submit-button">Submit</v-btn>
      </v-card-actions>
    </template>
  </ac-form-dialog>
</template>

<style>
  .submission-stepper .v_messages__message {
    hyphens: unset
  }
</style>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import AcFormDialog from './wrappers/AcFormDialog.vue'
import AcBoundField from './fields/AcBoundField'
import Subjective from '../mixins/subjective'
import {Prop} from 'vue-property-decorator'
import {Character} from '@/store/characters/types/Character'
import Submission from '@/types/Submission'
import {FormController} from '@/store/forms/form-controller'
import {User} from '@/store/profiles/types/User'
import Upload from '@/mixins/upload'
import {newUploadSchema} from '@/lib'
  @Component({
    components: {AcBoundField, AcFormDialog},
  })
export default class AcNewSubmission extends mixins(Subjective, Upload) {
    // For certain views, we want to control when the characters field is rendered so Vuetify's upstream item cache can
    // be prepopulated. There may be a better way to do this, but it should work for now.
    @Prop({default: true})
    public showCharacters!: boolean
    @Prop({default: () => []})
    public characterInitItems!: Character[]
    @Prop({default: ''})
    public title!: string
    @Prop({required: true})
    public value!: boolean
    public newUpload: FormController = null as unknown as FormController

    public get success() {
      return this.$listeners.success || this.goToSubmission
    }

    public get isArtist() {
      /* istanbul ignore if */
      if (!this.subject) {
        return false
      }
      return this.newUpload.fields.artists.model.indexOf(this.subject.id) !== -1
    }

    public set isArtist(val: boolean) {
      /* istanbul ignore if */
      if (!this.subject) {
        return
      }
      const artists = this.newUpload.fields.artists
      if (val && !artists.model.includes(this.subject.id)) {
        artists.model.push(this.subject.id)
      } else if (!val) {
        artists.model = artists.model.filter((artistId: number) => {
          return artistId !== (this.subject as User).id
        })
      }
    }

    public toggle(value: boolean) {
      this.$emit('input', value)
    }

    public goToSubmission(submission: Submission) {
      this.showUpload = false
      this.$router.push({name: 'Submission', params: {submissionId: submission.id + ''}, query: {editing: 'true'}})
    }

    public get preloadedUser() {
      return [this.subject]
    }

    public created() {
      this.newUpload = this.$getForm('newUpload', newUploadSchema(this.subjectHandler.user))
    }
}
</script>
