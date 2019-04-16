<template>
  <ac-load-section :controller="character.submissions" v-show="character.profile.ready">
    <v-card color="grey darken-4">
      <v-card-title><h2>Uploads</h2></v-card-title>
      <v-card-text>
        <v-layout row wrap v-if="character.submissions.list.length && character.profile.ready"
                  justify-content
                  align-center
        >
          <v-flex :class="featuredClasses">
            <v-layout column>
              <v-flex grow>
                <ac-gallery-preview
                  :submission="featured"
                  thumb-name="gallery"
                  :contain="true"
                  :compact="true"
                  :aspect-ratio="null"
              />
              </v-flex>
              <v-flex shrink v-if="more" text-xs-center pt-2>
                <v-btn color="primary" :to="{name: 'CharacterGallery', params: {username, characterName}}">See all Uploads</v-btn>
              </v-flex>
            </v-layout>
          </v-flex>
          <v-flex xs12 md3 lg2 offset-md1>
            <v-layout column d-flex>
              <v-flex v-for="(submission, index) in prunedSubmissions"
                      shrink
                      :class="{'pb-2': index !== prunedSubmissions.length}" :key="submission.x.id">
                <ac-gallery-preview
                  :submission="submission.x"
                  thumb-name="thumbnail"
                  :contain="true"
                  :show-footer="false"
                />
              </v-flex>
              <v-spacer></v-spacer>
              <v-flex></v-flex>
            </v-layout>
          </v-flex>
        </v-layout>
      </v-card-text>
    </v-card>
  </ac-load-section>
</template>

<script lang="ts">
import AcGalleryPreview from '../../AcGalleryPreview.vue'
import Component, {mixins} from 'vue-class-component'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import {Character} from '@/store/characters/types/Character'
import CharacterCentric from '@/components/views/character/mixins/CharacterCentric'
import Submission from '@/types/Submission'
import {SingleController} from '@/store/singles/controller'

  @Component({components: {AcLoadSection, AcGalleryPreview}})
export default class AcContextGallery extends mixins(CharacterCentric) {
  public get featured() {
    const character = this.character.profile.x as Character
    return character.primary_submission || this.character.submissions.list[0].x
  }
  public created() {
    this.character.submissions.firstRun().then()
  }

  public get prunedSubmissions() {
    let submissions = [...this.character.submissions.list]
    submissions = submissions.filter(
      (submission: SingleController<Submission>) =>
        (submission.x as Submission).id !== (this.featured as Submission).id
    )
    return submissions.slice(0, 4)
  }
  public get featuredClasses() {
    const single = this.character.submissions.list.length === 1
    return {
      'pb-2': this.$vuetify.breakpoint.smAndDown,
      xs12: true,
      md3: !single,
      lg9: !single,
    }
  }
  public get more() {
    return (this.prunedSubmissions.length < (this.character.submissions.list.length - 1))
  }
}
</script>
