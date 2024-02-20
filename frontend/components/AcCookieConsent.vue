<template>
  <div>
    <ac-form-dialog v-model="showDialog" @submit="setCurrent" title="Cookie Settings">
      <template v-slot:default>
        <v-card-text>
          Cookies are special pieces of data that help websites keep track of information about a visitor. They can help
          with authentication,
          site improvement, and other functions. Artconomy uses the following kinds of cookies:
        </v-card-text>
        <v-row>
          <v-col cols="6">
            <v-checkbox checked disabled v-model="required" label="Required Cookies"/>
          </v-col>
          <v-col cols="6">
            Artconomy has a handful of cookies that are required for basic function, including those that handle
            authentication and your content settings.
          </v-col>
          <v-col cols="6">
            <v-checkbox v-model="firstParty" label="First Party Analytics" class="first-party-analytics"/>
          </v-col>
          <v-col cols="6">
            Artconomy uses <a href="https://matomo.org/" rel="noopener nofollow" target="_blank">Matomo Analytics</a>,
            an open source privacy-centric analytics service which does not share its data with third party entities. We
            use this to tell which
            parts of our site people use the most and where we might make improvements.
          </v-col>
          <v-col cols="6">
            <v-checkbox v-model="thirdParty" label="Third Party Analytics" class="third-party-analytics"/>
          </v-col>
          <v-col cols="6">
            <p>
              Artconomy may partner with third party networks in order to verify if integrations with those partners is
              working correctly, or to gain more
              insight into our customer base. For example, if we ran an ad on Pinterest, these cookies would help us know
              that these ads were
              actually being seen and followed. This helps us build a website more tailored to customer needs, but is the
              least private cookie we use.
            </p>
            <p>
              For the moment, we have also introduced Google Analytics on advice of a marketing advisor. We are
              evaluating the possibility of removal pending determination of how our advisor uses the service.
            </p>
          </v-col>
        </v-row>
      </template>
      <template v-slot:bottom-buttons>
        <v-card-actions row wrap class="hidden-sm-and-down">
          <v-spacer></v-spacer>
          <v-btn @click="onlyEssential" class="essential-cookies-button" variant="flat">Only Required Cookies</v-btn>
          <v-btn color="primary" type="submit" class="dialog-submit" variant="flat">Save Settings
          </v-btn>
        </v-card-actions>
      </template>
    </ac-form-dialog>
    <v-snackbar
        :timeout="-1"
        :model-value="true"
        v-if="cookiesUnset && !showDialog"
        :vertical="true"
        :attach="$snackbarTarget"
    >
      Artconomy uses cookies to help improve our service.
      <template v-slot:actions>
        <v-row>
          <v-col class="text-center">
            <v-btn
                variant="text"
                @click="onlyEssential"
                color="red"
                class="essential-cookies-button"
            >
              Decline Non-essential
            </v-btn>
            <v-btn
                variant="text"
                @click="showDialog = true"
                class="customize-cookies-button"
            >
              Customize
            </v-btn>
            <v-btn
                variant="text"
                @click="acceptAll"
                color="primary"
                class="accept-cookies-button"
            >
              Accept All
            </v-btn>
          </v-col>
        </v-row>
      </template>
    </v-snackbar>
  </div>
</template>

<script lang="ts">
import {Component, toNative} from 'vue-facing-decorator'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import {ArtVue} from '@/lib/lib.ts'

@Component({
  components: {AcFormDialog},
})
class AcCookieConsent extends ArtVue {
  required = true
  forceRecalculate = 0

  public acceptAll() {
    this.firstParty = true
    this.thirdParty = true
    this.cookiesUnset = false
    this.performActions()
  }

  public onlyEssential() {
    this.firstParty = false
    this.thirdParty = false
    this.cookiesUnset = false
    this.showDialog = false
    this.performActions()
  }

  public setCurrent() {
    this.firstParty = this.firstParty  // eslint-disable-line
    this.thirdParty = this.thirdParty  // eslint-disable-line
    this.cookiesUnset = false
    this.showDialog = false
    this.performActions()
  }

  public get cookiesUnset() {
    // Increase the V number when this menu changes so viewers have a chance to reconsider.
    // Also change it in the getter.
    this.forceRecalculate // eslint-disable-line
    return !parseInt(localStorage.getItem('cookieOptionsSetV1') || '0', 10)
  }

  public set cookiesUnset(value: boolean) {
    /* istanbul ignore next */
    localStorage.setItem('cookieOptionsSetV1', value ? '0' : '1')
  }

  public get showDialog() {
    return this.$store.state.showCookieDialog
  }

  public set showDialog(value: boolean) {
    this.$store.commit('setShowCookieDialog', value)
  }

  public get firstParty() {
    this.forceRecalculate  // eslint-disable-line
    return !!parseInt(localStorage.getItem('firstPartyAnalytics') || '1', 10)
  }

  public set firstParty(value: boolean) {
    this.forceRecalculate += 1
    localStorage.setItem('firstPartyAnalytics', value ? '1' : '0')
  }

  public get thirdParty() {
    this.forceRecalculate  // eslint-disable-line
    return !!parseInt(localStorage.getItem('thirdPartyAnalytics') || '1', 10)
  }

  public set thirdParty(value: boolean) {
    this.forceRecalculate += 1
    localStorage.setItem('thirdPartyAnalytics', value ? '1' : '0')
  }

  public performActions() {
    if (this.cookiesUnset) {
      return
    }
    if (this.firstParty) {
      window._paq.push(['rememberCookieConsentGiven'])
    } else {
      window._paq.push(['forgetCookieConsentGiven'])
    }
    // If and when we add Pinterest ads back in, we'll need to do something with the third party consent cookies.
    if (this.thirdParty) {
      window._drip()
      window._ga()
    }
  }

  public created() {
    this.performActions()
  }
}

export default toNative(AcCookieConsent)
</script>
