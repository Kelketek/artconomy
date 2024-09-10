<template>
  <div>
    <ac-form-dialog v-model="showDialog" @submit="setCurrent" :large="true" title="Cookie Settings">
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
        :attach="snackbarTarget"
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

<script setup lang="ts">
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import {computed, onMounted, ref} from 'vue'
import {useStore} from 'vuex'
import {ArtState} from '@/store/artState.ts'
import {useTargets} from '@/plugins/targets.ts'
import {getCookie, setCookie} from '@/lib/lib.ts'

const forceRecalculate = ref(0)
const required = ref(true)
const store = useStore<ArtState>()
const {snackbarTarget} = useTargets()


const cookiesUnset = computed({
  get() {
    // Increase the V number when this menu changes so viewers have a chance to reconsider.
    // Also change it in the getter.
    forceRecalculate.value // eslint-disable-line
    return !parseInt(getCookie('cookieOptionsSetV2') || '0', 10)
  },
  set(value: boolean) {
    setCookie('cookieOptionsSetV2', value ? '0' : '1')
  },
})

const showDialog = computed({
  get() {
    return store.state.showCookieDialog
  },
  set(value: boolean) {
    store.commit('setShowCookieDialog', value)
  }
})

const firstParty = computed({
  get() {
    forceRecalculate.value  // eslint-disable-line
    return !!parseInt(getCookie('firstPartyAnalytics') || '1', 10)
  },
  set(value: boolean) {
    forceRecalculate.value += 1
    setCookie('firstPartyAnalytics', value ? '1' : '0')
  }
})

const thirdParty = computed({
  get() {
    forceRecalculate.value  // eslint-disable-line
    return !!parseInt(getCookie('thirdPartyAnalytics') || '1', 10)
  },
  set(value: boolean) {
    forceRecalculate.value += 1
    setCookie('thirdPartyAnalytics', value ? '1' : '0')
  },
})

const performActions = () => {
  if (cookiesUnset.value) {
    return
  }
  if (firstParty.value) {
    window._paq.push(['rememberCookieConsentGiven'])
  } else {
    window._paq.push(['forgetCookieConsentGiven'])
  }
  if (thirdParty.value) {
    window._drip()
    window._fb()
  }
}

const acceptAll = () => {
  firstParty.value = true
  thirdParty.value = true
  cookiesUnset.value = false
  performActions()
}

const onlyEssential = () => {
  firstParty.value = false
  thirdParty.value = false
  cookiesUnset.value = false
  showDialog.value = false
  performActions()
}

const setCurrent = () => {
  firstParty.value = firstParty.value  // eslint-disable-line
  thirdParty.value = thirdParty.value  // eslint-disable-line
  cookiesUnset.value = false
  showDialog.value = false
  performActions()
}

onMounted(performActions)
</script>
