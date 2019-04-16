<template>
  <v-card>
    <v-card-text>
      <v-subheader>Community</v-subheader>
      <v-container fluid class="py-0" grid-list-lg>
        <v-layout row wrap pb-4>

          <v-flex xs12 sm6 md4>
            <ac-patch-field
                field-type="v-switch"
                label="Favorites Hidden"
                hint="When off, prevents others from seeing what pieces you've added to your favorites."
                :persistent-hint="true"
                :save-indicator="false"
                :patcher="favoritesHidden"
            ></ac-patch-field>
          </v-flex>
          <v-flex xs12 sm6 md4>
            <ac-patch-field label="Taggable"
                field-type="v-switch"
                hint="When off, prevents others from tagging you or your characters in submissions."
                :patcher="taggable"
                :save-indicator="false"
                :persistent-hint="true"></ac-patch-field>
          </v-flex>
          <v-flex xs12 sm6 md4>
            <ac-patch-field
                field-type="v-switch" label="Artist Mode"
                hint="When on, enables options and functionality for selling commissions."
                :patcher="artistMode"
                :save-indicator="false"
                :persistent-hint="true"></ac-patch-field>
          </v-flex>
        </v-layout>
      </v-container>
      <v-divider></v-divider>
      <v-layout>
        <v-flex>
          <v-subheader>Content/Browsing</v-subheader>
          <v-card-text :class="{disabled: sfwMode.model}">
            <v-layout>
              <v-flex>Select the maximum content rating you'd like to see when browsing.</v-flex>
            </v-layout>
            <ac-patch-field
                field-type="v-slider"
                :patcher="maxRating"
                :always-dirty="true"
                :max="3"
                step="1"
                ticks="always"
                tick-size="2"
                :color="ratingColor[maxRating.model]"
                :disabled="sfwMode.model"
            >
            </ac-patch-field>
            <v-layout row wrap>
              <v-flex xs12 text-xs-center><h2>{{ratingOptions[maxRating.model]}}</h2></v-flex>
              <v-flex xs12>
                <span v-text="ratingLongDesc[maxRating.model]">
                </span>
              </v-flex>
            </v-layout>
          </v-card-text>
        </v-flex>
      </v-layout>
      <v-container fluid py-0 grid-list-lg>
        <v-layout row wrap justify-center align-center>
          <v-flex xs12 sm6 md4 text-xs-center>
            <ac-patch-field field-type="v-switch" label="SFW Mode"
                :patcher="sfwMode"
                hint="Overrides your content preferences to only allow clean content. Useful if viewing the site
                      from a work machine."
                :save-indicator="false"
                persistent-hint></ac-patch-field>
          </v-flex>
          <v-flex xs12 sm6>
            <ac-patch-field field-type="ac-tag-field"
                label="Blacklist"
                hint="Submissions that have tags in your blacklist will be hidden from view."
                persistent-hint
                :patcher="blacklist"
            ></ac-patch-field>
          </v-flex>
        </v-layout>
      </v-container>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import Subjective from '@/mixins/subjective'
import {RATING_COLOR, RATING_LONG_DESC, RATINGS_SHORT} from '@/lib'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import Alerts from '@/mixins/alerts'
import AcTagField from '@/components/fields/AcTagField.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import {Patch} from '@/store/singles/patcher'

  @Component({
    components: {AcTagField, AcLoadingSpinner, AcPatchField},
  })
export default class Options extends mixins(Viewer, Subjective, Alerts) {
    private ratingLabels = Object.values(RATINGS_SHORT)
    private ratingOptions = RATINGS_SHORT
    private maxRating: Patch = null as unknown as Patch
    private sfwMode: Patch = null as unknown as Patch
    private artistMode: Patch = null as unknown as Patch
    private favoritesHidden: Patch = null as unknown as Patch
    private taggable: Patch = null as unknown as Patch
    private blacklist: Patch = null as unknown as Patch

    private ratingLongDesc = RATING_LONG_DESC
    private ratingColor = RATING_COLOR

    public created() {
      this.maxRating = this.$makePatcher({modelProp: 'subjectHandler.user', attrName: 'rating'})
      this.sfwMode = this.$makePatcher({modelProp: 'subjectHandler.user', attrName: 'sfw_mode'})
      this.artistMode = this.$makePatcher({modelProp: 'subjectHandler.user', attrName: 'artist_mode'})
      this.favoritesHidden = this.$makePatcher({modelProp: 'subjectHandler.user', attrName: 'favorites_hidden'})
      this.taggable = this.$makePatcher({modelProp: 'subjectHandler.user', attrName: 'taggable'})
      this.blacklist = this.$makePatcher({modelProp: 'subjectHandler.user', attrName: 'blacklist'})
    }

    private get settingsUrl() {
      return `/api/profiles/v1/account/${this.username}/`
    }
}
</script>

<!--suppress CssUnusedSymbol -->
<style scoped>
  .disabled {
    opacity: .5;
  }
</style>
