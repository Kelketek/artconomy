<template>
  <v-card>
    <v-card-text v-if="artistProfile.x">
      <v-container fluid class="py-0" grid-list-lg>
        <v-subheader>Workload</v-subheader>
        <v-layout row wrap pb-4>
          <v-flex xs12 sm6 md4>
            <ac-patch-field
                label="Commissions Closed"
                field-type="v-switch"
                hint="When on, delists all of your products, and only allows orders you've specifically
                      invoiced or granted a token for."
                :persistent-hint="true"
                :save-indicator="false"
                :patcher="commissionsClosed"
            ></ac-patch-field>
          </v-flex>
          <v-flex xs12 sm6 md4>
            <ac-patch-field
                label="Auto Withdraw"
                field-type="v-switch"
                hint="Automatically withdraws all funds you receive from commissions. You might turn this off if
                      you're switching banks."
                :patcher="autoWithdraw"
                :save-indicator="false"
                :persistent-hint="true"></ac-patch-field>
          </v-flex>
          <v-flex xs12 sm6 md4>
            <v-layout row wrap>
              <v-flex xs12>
                <ac-patch-field
                    field-type="v-slider"
                    label="Slots"
                    :patcher="maxLoad"
                    hint="Commissions are automatically closed when you've filled up your slots.
                    You can customize an order to take multiple slots if it is especially big."
                    :persistent-hint="true"
                    :min="1"
                    :max="100"
                >
                </ac-patch-field>
              </v-flex>
            </v-layout>
            <v-layout row wrap>
              <v-flex xs12>
                <ac-patch-field
                    :patcher="maxLoad"
                    class="mt-0"
                    hide-details
                    single-line
                    type="number"
                    :save-indicator="false"
                    step="1"
                ></ac-patch-field>
              </v-flex>
            </v-layout>
          </v-flex>
          <v-flex></v-flex>
        </v-layout>
      </v-container>
      <v-layout>
        <v-flex>
          <v-subheader>Content</v-subheader>
          <v-card-text>
            <v-layout>
              <v-flex>Select the maximum rating of content you're willing to create.</v-flex>
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
      <v-layout row wrap>
        <v-flex xs12 py-4>
          <v-divider></v-divider>
        </v-flex>
        <v-flex xs12>
          <ac-patch-field
              field-type="ac-editor"
              :patcher="commissionInfo"
              label="Commission Info"
              :persistent-hint="true"
              :counter="5000"
              :auto-save="false"
              hint="This information will be shown on all of your product pages. It could contain terms of service or
              other information used to set expectations with your clients."
          >

          </ac-patch-field>
        </v-flex>
      </v-layout>
    </v-card-text>
    <v-card-text v-else>
      <ac-loading-spinner></ac-loading-spinner>
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
import {SingleController} from '@/store/singles/controller'
import {ArtistProfile} from '@/store/profiles/types/ArtistProfile'
import AcEditor from '@/components/fields/AcEditor.vue'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import {Patch} from '@/store/singles/patcher'

  @Component({
    components: {AcPatchField, AcEditor, AcLoadingSpinner},
  })
export default class Options extends mixins(Viewer, Subjective, Alerts) {
    private ratingLabels = Object.values(RATINGS_SHORT)
    private ratingOptions = RATINGS_SHORT
    private artistProfile: SingleController<ArtistProfile> = null as unknown as SingleController<ArtistProfile>
    private maxLoad: Patch = null as unknown as Patch
    private autoWithdraw: Patch = null as unknown as Patch
    private commissionsClosed: Patch = null as unknown as Patch
    private maxRating: Patch = null as unknown as Patch
    private commissionInfo: Patch = null as unknown as Patch

    private ratingLongDesc = RATING_LONG_DESC
    private ratingColor = RATING_COLOR

    public created() {
      this.artistProfile = this.$getSingle('artistProfile', {endpoint: this.url})
      this.artistProfile.get().then()
      this.maxLoad = this.$makePatcher({modelProp: 'artistProfile', debounceRate: 200, attrName: 'max_load'})
      this.autoWithdraw = this.$makePatcher({modelProp: 'artistProfile', attrName: 'auto_withdraw'})
      this.commissionsClosed = this.$makePatcher({modelProp: 'artistProfile', attrName: 'max_rating'})
      this.maxRating = this.$makePatcher({modelProp: 'artistProfile', attrName: 'max_rating'})
      this.commissionInfo = this.$makePatcher(
        {modelProp: 'artistProfile', attrName: 'commission_info', debounceRate: 1000}
      )
    }

    private get url() {
      return `/api/profiles/v1/account/${this.username}/artist-profile/`
    }
}
</script>
