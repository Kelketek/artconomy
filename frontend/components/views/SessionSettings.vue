<template>
  <ac-load-section :controller="viewerHandler.user">
    <template v-slot:default>
      <v-container>
        <v-card>
          <v-card-text>
            <v-layout row wrap>
              <v-flex xs12>
                <v-card-text :class="{disabled: patchers.sfw_mode.model}">
                  <ac-patch-field
                      field-type="ac-rating-field"
                      label="Select the maximum content rating you'd like to see when browsing."
                      :patcher="patchers.rating"
                      :disabled="patchers.sfw_mode.model"
                      :max="2"
                  >
                  </ac-patch-field>
                </v-card-text>
              </v-flex>
              <v-flex xs12 sm6>
                <ac-patch-field field-type="v-switch" label="SFW Mode"
                                :patcher="patchers.sfw_mode"
                                hint="Overrides your content preferences to only allow clean content. Useful if viewing the site
                      from a work machine."
                                :save-indicator="false"
                                persistent-hint></ac-patch-field>
              </v-flex>
              <v-flex xs12 sm6 pa-2 text-xs-center>
                <p class="title">Register, and get access to more cool features like:</p>
              </v-flex>
              <v-flex xs12 sm6 d-flex>
                <v-layout row justify-content align-center d-flex>
                  <v-flex>
                    <v-img src="/static/images/laptop.png" max-height="30vh" :contain="true"></v-img>
                  </v-flex>
                </v-layout>
              </v-flex>
              <v-flex xs12 sm6 d-flex>
                <v-layout row justify-content align-center>
                  <v-spacer />
                  <v-flex>
                    <ul>
                      <li>
                        <strong>Character listings</strong>
                      </li>
                      <li>
                        <strong>Saved Payment information for quick checkout</strong>
                      </li>
                      <li>
                        <strong>Galleries</strong>
                      </li>
                      <li>
                        <strong>Blacklist settings</strong>
                      </li>
                      <li>
                        <strong>...And much more!</strong>
                      </li>
                    </ul>
                  </v-flex>
                  <v-spacer />
                </v-layout>
              </v-flex>
              <v-flex xs12 text-xs-center pt-2>
                <v-btn color="primary" :to="{name: 'Login', params: {tabName: 'register'}}">Sign up for FREE!</v-btn>
              </v-flex>
            </v-layout>
          </v-card-text>
        </v-card>
      </v-container>
    </template>
  </ac-load-section>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Viewer from '@/mixins/viewer'
import AcPatchField from '@/components/fields/AcPatchField.vue'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
  @Component({
    components: {AcLoadSection, AcPatchField},
  })
export default class SessionSettings extends mixins(Viewer) {
  public get patchers() {
    return this.viewerHandler.user.patchers
  }
  public created() {
    if (this.isRegistered) {
      this.$router.replace({name: 'Settings', params: {username: this.rawViewerName}})
    }
  }
}
</script>
