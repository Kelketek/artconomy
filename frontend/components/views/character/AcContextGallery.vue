<template>
  <ac-load-section :controller="character.submissions" v-show="character.profile.ready">
    <v-card color="grey darken-4">
      <v-card-title><h2>Uploads</h2></v-card-title>
      <v-card-text>
        <v-row no-gutters v-if="character.submissions.list.length && character.profile.ready"
        >
          <div :class="featuredClasses">
            <v-col cols="12">
              <v-col class="grow">
                <ac-gallery-preview
                  :submission="featured"
                  thumb-name="gallery"
                  :contain="true"
                  :compact="true"
                  :aspect-ratio="null"
                  :show-footer="$vuetify.breakpoint.lgAndUp"
                />
              </v-col>
              <v-col class="shrink text-center pt-2" v-if="more && $vuetify.breakpoint.mdAndUp" >
                <v-btn color="primary" :to="{name: 'CharacterGallery', params: {username, characterName}}">See all Uploads</v-btn>
              </v-col>
            </v-col>
          </div>
          <v-col cols="12" md="4" lg="2" offset-md="1" align-self="center">
            <v-row>
              <v-col cols="6" lg="12" v-for="submission in prunedSubmissions" :key="submission.x.id">
                <ac-gallery-preview
                  :submission="submission.x"
                  thumb-name="thumbnail"
                  :contain="true"
                  :show-footer="false"
                />
              </v-col>
              <v-col cols="12" class="text-center pt-2" v-if="more && $vuetify.breakpoint.smAndDown" >
                <v-btn color="primary" :to="{name: 'CharacterGallery', params: {username, characterName}}">See all Uploads</v-btn>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
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
    const single = this.prunedSubmissions.length === 0
    return {
      'pb-2': this.$vuetify.breakpoint.smAndDown,
      'col-12': true,
      'col-md-7': !single,
      'col-lg-9': !single,
      'align-self-center': true,
    }
  }
  public get more() {
    return (this.prunedSubmissions.length < (this.character.submissions.list.length - 1))
  }
}
</script>
