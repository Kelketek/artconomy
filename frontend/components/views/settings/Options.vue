<template>
  <v-card>
    <v-card-text>
      <v-list-subheader>Community</v-list-subheader>
      <v-container fluid class="py-0">
        <v-row no-gutters class="pb-4">
          <v-col cols="12" sm="6" md="4">
            <ac-patch-field
                field-type="v-switch"
                label="Favorites Hidden"
                hint="When on, prevents others from seeing what pieces you've added to your favorites."
                :persistent-hint="true"
                color="primary"
                :patcher="patchers.favorites_hidden"
            />
          </v-col>
          <v-col cols="12" sm="6" md="4">
            <ac-patch-field label="Taggable"
                            field-type="v-switch"
                            hint="When off, prevents others from tagging you or your characters in submissions."
                            :patcher="patchers.taggable"
                            :persistent-hint="true"
                            color="primary"
            />
          </v-col>
          <v-col cols="12" sm="6" md="4">
            <ac-patch-field
                field-type="v-switch" label="Artist Mode"
                hint="When on, enables options and functionality for selling commissions."
                :patcher="patchers.artist_mode"
                :persistent-hint="true"
                color="primary"
            />
          </v-col>
        </v-row>
      </v-container>
      <v-divider></v-divider>
      <v-row no-gutters>
        <v-col>
          <v-list-subheader>Content/Browsing</v-list-subheader>
          <v-card-text>
            <v-row>
              <v-col cols="12" offset-md="3" md="6" :class="{disabled: patchers.sfw_mode.model}">
                <ac-patch-field
                    field-type="ac-birthday-field"
                    label="Birthday"
                    :patcher="patchers.birthday"
                    :persistent-hint="true"
                    hint="You must be at least 18 years old to view adult content."
                />
              </v-col>
              <v-col cols="12" md="6">
                <ac-patch-field field-type="ac-tag-field"
                                label="Blocked tags"
                                hint="All submissions and characters that have these tags will be hidden from view, regardless of rating."
                                persistent-hint
                                :patcher="patchers.blacklist"
                />
              </v-col>
              <v-col cols="12" md="6" class="text-center" :class="{disabled: patchers.sfw_mode.model}">
                <ac-patch-field field-type="ac-tag-field"
                                label="NSFW Blocked tags"
                                hint="Submissions and characters that have these tags and have a rating higher than clean/safe will be hidden from view."
                                persistent-hint
                                :patcher="patchers.nsfw_blacklist"
                />
              </v-col>
              <v-col cols="12" class="pt-5" :class="{disabled: patchers.sfw_mode.model}"><strong>Select the maximum content rating
                you'd like to see when browsing.</strong></v-col>
              <v-col cols="12">
                <ac-patch-field
                    field-type="ac-rating-field"
                    :patcher="patchers.rating"
                    :max="3"
                    step="1"
                    show-ticks="always"
                    tick-size="2"
                    :show-warning="true"
                />
              </v-col>
            </v-row>
          </v-card-text>
        </v-col>
      </v-row>
      <v-container class="py-0" fluid>
        <v-row justify="center" align="center">
          <v-col class="text-center" cols="12" sm="6">
            <ac-patch-field field-type="v-switch" label="SFW Mode"
                            :patcher="patchers.sfw_mode"
                            hint="Overrides your content preferences to only allow clean content. Useful if viewing the site
                      from a work machine."
                            :save-indicator="false"
                            :instant="true"
                            color="primary"
                            persistent-hint
            />
          </v-col>
          <v-col order="1" cols="12" sm="6" class="text-center">
            <v-btn color="secondary" variant="elevated" @click="updateCookieSettings" class="cookie-settings-button">Update Cookie
              Settings
            </v-btn>
          </v-col>
        </v-row>
      </v-container>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import {Component, mixins, toNative} from 'vue-facing-decorator'
import Viewer from '@/mixins/viewer.ts'
import Subjective from '@/mixins/subjective.ts'
import {RATING_COLOR, RATING_LONG_DESC, RATINGS_SHORT} from '@/lib/lib.ts'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import Alerts from '@/mixins/alerts.ts'
import AcTagField from '@/components/fields/AcTagField.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import {Patch} from '@/store/singles/patcher.ts'
import {differenceInYears} from 'date-fns'
import {ContentRating} from '@/types/ContentRating.ts'
import {SingleController} from '@/store/singles/controller.ts'
import {User} from '@/store/profiles/types/User.ts'
import {parseISO} from '@/lib/formattingTools.ts'

@Component({
  components: {
    AcTagField,
    AcLoadingSpinner,
    AcPatchField,
  },
})
class Options extends mixins(Viewer, Subjective, Alerts) {
  public ratingOptions = RATINGS_SHORT

  public EXTREME = 3
  public ratingLongDesc = RATING_LONG_DESC
  public ratingColor = RATING_COLOR

  public get adultAllowed() {
    if (this.patchers.sfw_mode.model) {
      return false
    }
    // @ts-ignore
    const birthday = this.patchers.birthday.model
    if (birthday === null) {
      return false
    }
    return differenceInYears(new Date(), parseISO(birthday)) >= 18
  }

  public get patchers() {
    return (this.subjectHandler.user as SingleController<User>).patchers
  }

  public updateCookieSettings() {
    this.$store.commit('setShowCookieDialog', true)
  }
}

export default toNative(Options)
</script>

<!--suppress CssUnusedSymbol -->
<style scoped>
.disabled {
  opacity: .5;
}
</style>
