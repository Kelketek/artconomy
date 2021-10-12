<template>
  <v-card>
    <v-card-text>
      <v-subheader>Community</v-subheader>
      <v-container fluid class="py-0">
        <v-row no-gutters class="pb-4"   >

          <v-col cols="12" sm="6" md="4">
            <ac-patch-field
                field-type="v-switch"
                label="Favorites Hidden"
                hint="When on, prevents others from seeing what pieces you've added to your favorites."
                :persistent-hint="true"
                :save-indicator="false"
                :patcher="favoritesHidden"
            ></ac-patch-field>
          </v-col>
          <v-col cols="12" sm="6" md="4">
            <ac-patch-field label="Taggable"
                field-type="v-switch"
                hint="When off, prevents others from tagging you or your characters in submissions."
                :patcher="taggable"
                :save-indicator="false"
                :persistent-hint="true"></ac-patch-field>
          </v-col>
          <v-col cols="12" sm="6" md="4">
            <ac-patch-field
                field-type="v-switch" label="Artist Mode"
                hint="When on, enables options and functionality for selling commissions."
                :patcher="artistMode"
                :save-indicator="false"
                :persistent-hint="true"></ac-patch-field>
          </v-col>
        </v-row>
      </v-container>
      <v-divider></v-divider>
      <v-row no-gutters>
        <v-col>
          <v-subheader>Content/Browsing</v-subheader>
          <v-card-text :class="{disabled: sfwMode.model}">
            <v-row no-gutters>
              <v-col cols="12" md="6" lg="4">
                <ac-patch-field
                  field-type="ac-birthday-field"
                  label="Birthday"
                  :patcher="subjectHandler.user.patchers.birthday"
                  :persistent-hint="true"
                  hint="You must be at least 18 years old to view adult content."
                ></ac-patch-field>
              </v-col>
              <v-col cols="12" class="pt-5"><strong>Select the maximum content rating you'd like to see when browsing.</strong></v-col>
            </v-row>
            <ac-patch-field
                field-type="v-slider"
                :patcher="maxRating"
                :always-dirty="true"
                :max="3"
                step="1"
                ticks="always"
                tick-size="2"
                :color="ratingColor[maxRating.model]"
            >
            </ac-patch-field>
            <v-row no-gutters  >
              <v-col class="text-center" cols="12" ><h2>{{ratingOptions[maxRating.model]}}</h2></v-col>
              <v-col cols="12">
                <span v-text="ratingLongDesc[maxRating.model]">
                </span>
              </v-col>
            </v-row>
          </v-card-text>
        </v-col>
      </v-row>
      <v-container class="py-0" fluid>
        <v-row no-gutters   justify="center" align="center">
          <v-col class="text-center" cols="12" sm="6" md="4" >
            <ac-patch-field field-type="v-switch" label="SFW Mode"
                :patcher="sfwMode"
                hint="Overrides your content preferences to only allow clean content. Useful if viewing the site
                      from a work machine."
                :save-indicator="false"
                persistent-hint></ac-patch-field>
          </v-col>
          <v-col cols="12" sm="6">
            <ac-patch-field field-type="ac-tag-field"
                label="Blacklist"
                hint="Submissions that have tags in your blacklist will be hidden from view."
                persistent-hint
                :patcher="blacklist"
            ></ac-patch-field>
          </v-col>
        </v-row>
      </v-container>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import Subjective from '@/mixins/subjective'
import {RATING_COLOR, RATING_LONG_DESC, RATINGS_SHORT, parseISO} from '@/lib/lib'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import Alerts from '@/mixins/alerts'
import AcTagField from '@/components/fields/AcTagField.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import {Patch} from '@/store/singles/patcher'
import {differenceInYears} from 'date-fns'

@Component({
  components: {AcTagField, AcLoadingSpinner, AcPatchField},
})
export default class Options extends mixins(Viewer, Subjective, Alerts) {
  private ratingOptions = RATINGS_SHORT
  private maxRating: Patch = null as unknown as Patch
  private sfwMode: Patch = null as unknown as Patch
  private artistMode: Patch = null as unknown as Patch
  private favoritesHidden: Patch = null as unknown as Patch
  private taggable: Patch = null as unknown as Patch
  private blacklist: Patch = null as unknown as Patch

  private ratingLongDesc = RATING_LONG_DESC
  private ratingColor = RATING_COLOR

  public get adultAllowed() {
    if (this.sfwMode.model) {
      return false
    }
    // @ts-ignore
    // @ts-ignore
    const birthday = this.subjectHandler.user.patchers.birthday.model
    if (birthday === null) {
      return false
    }
    return differenceInYears(new Date(), parseISO(birthday)) >= 18
  }

  public created() {
    this.maxRating = this.$makePatcher({modelProp: 'subjectHandler.user', attrName: 'rating'})
    this.sfwMode = this.$makePatcher({modelProp: 'subjectHandler.user', attrName: 'sfw_mode'})
    this.artistMode = this.$makePatcher({modelProp: 'subjectHandler.user', attrName: 'artist_mode'})
    this.favoritesHidden = this.$makePatcher({modelProp: 'subjectHandler.user', attrName: 'favorites_hidden'})
    this.taggable = this.$makePatcher({modelProp: 'subjectHandler.user', attrName: 'taggable'})
    this.blacklist = this.$makePatcher({modelProp: 'subjectHandler.user', attrName: 'blacklist'})
  }
}
</script>

<!--suppress CssUnusedSymbol -->
<style scoped>
  .disabled {
    opacity: .5;
  }
</style>
