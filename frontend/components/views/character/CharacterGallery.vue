<template>
  <v-container>
    <ac-load-section :controller="character.profile">
      <ac-character-toolbar :username="username" :character-name="characterName" :post-add="character.submissions.unshift" />
      <ac-paginated :list="character.submissions" :track-pages="true" class="pt-3">
        <v-col cols="4" sm="3" lg="2" v-for="submission in this.character.submissions.list" :key="submission.x.id">
          <ac-gallery-preview class="pa-1" :submission="submission.x" />
        </v-col>
      </ac-paginated>
    </ac-load-section>
  </v-container>
</template>

<script lang="ts">
import CharacterCentric from './mixins/CharacterCentric'
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import AcPaginated from '@/components/wrappers/AcPaginated.vue'
import AcCharacterToolbar from '@/components/views/character/AcCharacterToolbar.vue'
import AcGalleryPreview from '@/components/AcGalleryPreview.vue'
import RatingRefresh from '@/mixins/RatingRefresh'
  @Component({
    components: {AcGalleryPreview, AcCharacterToolbar, AcPaginated, AcLoadSection},
  })
export default class CharacterGallery extends mixins(Subjective, CharacterCentric, RatingRefresh) {
  public refreshLists = ['character.submissions']
  public created() {
    this.character.profile.get().catch(this.setError)
    this.character.submissions.firstRun().catch(this.setError)
  }
}
</script>
