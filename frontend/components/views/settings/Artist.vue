<template>
  <ac-load-section :controller="artistProfile">
    <template v-slot:default>
      <v-card>
        <v-card-text>
          <v-container fluid class="py-0">
            <v-subheader>
              <strong>
                Workload
              </strong>
            </v-subheader>
            <v-row no-gutters class="pb-4"   >
              <v-col cols="12" sm="6" md="4">
                <ac-patch-field
                    label="Commissions Closed"
                    field-type="v-switch"
                    hint="When on, delists all of your products, and only allows orders you've specifically
                          invoiced or granted a token for."
                    :persistent-hint="true"
                    :save-indicator="false"
                    :patcher="artistProfile.patchers.commissions_closed"
                ></ac-patch-field>
              </v-col>
              <v-col cols="12" sm="6" md="4">
                <ac-patch-field
                    label="Auto Withdraw"
                    field-type="v-switch"
                    hint="Automatically withdraws all funds you receive from commissions. You might turn this off if
                          you're switching banks."
                    :patcher="artistProfile.patchers.auto_withdraw"
                    :save-indicator="false"
                    :persistent-hint="true"></ac-patch-field>
              </v-col>
              <v-col cols="12" sm="6" md="4">
                <v-row no-gutters  >
                  <v-col cols="12">
                    <ac-patch-field
                        field-type="v-slider"
                        label="Slots"
                        :patcher="artistProfile.patchers.max_load"
                        hint="Commissions are automatically closed when you've filled up your slots.
                        You can customize an order to take multiple slots if it is especially big."
                        :persistent-hint="true"
                        :min="1"
                        :max="100"
                    >
                    </ac-patch-field>
                  </v-col>
                </v-row>
                <v-row no-gutters  >
                  <v-col cols="12">
                    <ac-patch-field
                        :patcher="artistProfile.patchers.max_load"
                        class="mt-0"
                        hide-details
                        single-line
                        type="number"
                        :save-indicator="false"
                        step="1"
                    ></ac-patch-field>
                  </v-col>
                </v-row>
              </v-col>
              <v-col></v-col>
            </v-row>
          </v-container>
          <v-row no-gutters>
            <v-col>
              <v-subheader>
                <strong>Content</strong>
              </v-subheader>
              <v-card-text>
                <v-row no-gutters>
                  <v-col>Select the maximum rating of content you're willing to create.</v-col>
                </v-row>
                <ac-patch-field
                    field-type="v-slider"
                    :patcher="artistProfile.patchers.max_rating"
                    :always-dirty="true"
                    :max="3"
                    step="1"
                    ticks="always"
                    tick-size="2"
                    :color="ratingColor[artistProfile.patchers.max_rating.model]"
                >
                </ac-patch-field>
                <v-row no-gutters  >
                  <v-col class="text-center" cols="12" ><h2>{{ratingOptions[artistProfile.patchers.max_rating.model]}}</h2></v-col>
                  <v-col cols="12">
                    <span v-text="ratingLongDesc[artistProfile.patchers.max_rating.model]">
                    </span>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-col>
          </v-row>
          <v-row no-gutters  >
            <v-col class="py-4" cols="12" >
              <v-divider></v-divider>
            </v-col>
            <v-col cols="12">
              <ac-patch-field
                  field-type="ac-editor"
                  :patcher="artistProfile.patchers.commission_info"
                  label="Commission Info"
                  :persistent-hint="true"
                  :counter="5000"
                  :auto-save="false"
                  hint="This information will be shown on all of your product pages. It could contain terms of service or
                  other information used to set expectations with your clients."
              >
              </ac-patch-field>
            </v-col>
          </v-row>
          <v-container>
            <v-row no-gutters>
              <v-col class="py-4" cols="12" >
                <v-divider></v-divider>
              </v-col>
              <v-col cols="12">
                <v-subheader>
                  <strong>I am/identify as...</strong>
                </v-subheader>
              </v-col>
              <v-col cols="12" sm="6">
                <ac-patch-field
                  :patcher="artistProfile.patchers.artist_of_color"
                  field-type="v-checkbox"
                  :save-indicator="false"
                  label="An Artist of Color"
                 />
              </v-col>
              <v-col cols="12" sm="6">
                <ac-patch-field
                  :patcher="artistProfile.patchers.lgbt"
                  field-type="v-checkbox"
                  :save-indicator="false"
                  label="A member of the LGBTQ+ community"
                />
              </v-col>
              <v-col cols="12">
                <strong>...and would like to be featured in the relevant community sections.</strong>
              </v-col>
            </v-row>
          </v-container>
        </v-card-text>
      </v-card>
    </template>
  </ac-load-section>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import Subjective from '@/mixins/subjective'
import {RATING_COLOR, RATING_LONG_DESC, RATINGS_SHORT} from '@/lib/lib'
import AcLoadingSpinner from '@/components/wrappers/AcLoadingSpinner.vue'
import Alerts from '@/mixins/alerts'
import {SingleController} from '@/store/singles/controller'
import {ArtistProfile} from '@/store/profiles/types/ArtistProfile'
import AcEditor from '@/components/fields/AcEditor.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import {Patch} from '@/store/singles/patcher'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'

  @Component({
    components: {AcLoadSection, AcPatchField, AcEditor, AcLoadingSpinner},
  })
export default class Options extends mixins(Viewer, Subjective, Alerts) {
    private ratingOptions = RATINGS_SHORT
    private artistProfile: SingleController<ArtistProfile> = null as unknown as SingleController<ArtistProfile>

    private ratingLongDesc = RATING_LONG_DESC
    private ratingColor = RATING_COLOR

    public created() {
      this.artistProfile = this.subjectHandler.artistProfile
      this.artistProfile.get().then()
    }
}
</script>
