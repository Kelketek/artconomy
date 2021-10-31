<template>
  <ac-load-section :controller="viewerHandler.user">
    <template v-slot:default>
      <v-container>
        <v-card>
          <v-card-text>
            <v-row no-gutters  >
              <v-col cols="12" md="6" lg="4" order="2" order-md="1">
                <ac-patch-field
                  field-type="ac-birthday-field"
                  label="Birthday"
                  :patcher="patchers.birthday"
                  :persistent-hint="true"
                  hint="You must be at least 18 years old to view adult content."
                ></ac-patch-field>
              </v-col>
              <v-col cols="12" md="6" lg="8" class="text-center mt-5" order="1" order-md="2">
                <v-btn @click="updateCookieSettings" color="secondary" class="cookie-settings-button">Update Cookie Settings</v-btn>
              </v-col>
              <v-col cols="12" order="3">
                <v-card-text :class="{disabled: patchers.sfw_mode.model}">
                  <ac-patch-field
                      field-type="ac-rating-field"
                      label="Select the maximum content rating you'd like to see when browsing."
                      :patcher="patchers.rating"
                      :disabled="!adultAllowed"
                      :max="2"
                      :persistent-hint="true"
                      hint="You must be at least 18 years old to view adult content."
                  >
                  </ac-patch-field>
                </v-card-text>
              </v-col>
              <v-col cols="12" sm="6" order="4">
                <ac-patch-field field-type="v-switch" label="SFW Mode"
                                :patcher="patchers.sfw_mode"
                                :instant="true"
                                hint="Overrides your content preferences to only allow clean content. Useful if viewing the site
                      from a work machine."
                                :save-indicator="false"
                                persistent-hint></ac-patch-field>
              </v-col>
              <v-col class="pa-2 text-center" cols="12" sm="6" order="5">
                <p class="title">Register, and get access to more cool features like:</p>
              </v-col>
              <v-col class="d-flex" cols="12" sm="6" order="6">
                <v-row no-gutters class="justify-content d-flex"  align="center" >
                  <v-col>
                    <v-img src="/static/images/laptop.png" max-height="30vh" :contain="true"></v-img>
                  </v-col>
                </v-row>
              </v-col>
              <v-col class="d-flex" cols="12" sm="6" order="7">
                <v-row no-gutters class="justify-content"  align="center">
                  <v-spacer />
                  <v-col>
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
                  </v-col>
                  <v-spacer />
                </v-row>
              </v-col>
              <v-col class="text-center pt-2" cols="12" order="8">
                <v-btn color="primary" :to="{name: 'Login', params: {tabName: 'register'}}">Sign up for FREE!</v-btn>
              </v-col>
            </v-row>
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
import {differenceInYears} from 'date-fns'
import {parseISO} from '@/lib/lib'

@Component({
  components: {AcLoadSection, AcPatchField},
})
export default class SessionSettings extends mixins(Viewer) {
  public get patchers() {
    return this.viewerHandler.user.patchers
  }

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

  public updateCookieSettings() {
    this.$store.commit('setShowCookieDialog', true)
  }

  public created() {
    if (this.isRegistered) {
      this.$router.replace({name: 'Settings', params: {username: this.rawViewerName}})
    }
  }
}
</script>
