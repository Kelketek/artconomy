<template>
  <v-btn color="primary" @click="showModal = true" :block="block" variant="flat" class="share-button">
    <v-icon left :icon="mdiShare"/>
    Share
  </v-btn>
  <ac-expanded-property v-model="showModal" aria-label="Sharing dialog">
    <template v-slot:title>
      <span>Share this!</span>
    </template>
    <v-row v-if="social">
      <v-col class="text-center" cols="12">
        <v-checkbox
            label="Include referral information"
            hint="Includes your username in URL to credit for rewards."
            :persistent-hint="true"
            v-model="referral"
            v-if="isRegistered"
            class="referral-check"
        />
      </v-col>
      <v-col class="text-center" cols="12">
        <v-row>
          <v-spacer/>
          <v-col class="shrink">
            <v-btn color="purple" icon small @click="showQr = true" class="qr-button">
              <v-icon :icon="mdiQrcode" size="large"/>
            </v-btn>
          </v-col>
          <v-col class="shrink" v-if="clean">
            <v-btn color="red" icon small
                   :href="`https://www.pinterest.com/pin/create/button/?canonicalUrl=${location({mtm_campaign: 'Pinned'})}&description=${titleText}&media=${encodeURIComponent(mediaUrl)}`"
                   rel="nofollow noopener"
                   target="_blank">
              <v-icon :icon="siPinterest.path" size="large"/>
            </v-btn>
          </v-col>
          <v-col class="shrink">
            <v-btn color="red" icon small :href="`https://reddit.com/submit?url=${location()}&title=${titleText}`"
                   rel="nofollow noopener"
                   target="_blank">
              <v-icon :icon="siReddit.path" size="large"/>
            </v-btn>
          </v-col>
          <v-col class="shrink">
            <v-btn color="blue" icon small :href="`https://telegram.me/share/url?url=${location()}`"
                   target="_blank"
                   rel="nofollow noopener"
            >
              <v-icon :icon="siTelegram.path" size="large"/>
            </v-btn>
          </v-col>
          <v-col class="shrink">
            <v-btn color="blue" icon small
                   :href="`https://twitter.com/share?text=${titleText}&url=${location()}&hashtags=Artconomy`"
                   target="_blank"
                   rel="nofollow noopener">
              <v-icon :icon="siX.path" size="large"/>
            </v-btn>
          </v-col>
          <v-col class="shrink">
            <v-btn color="grey darken-4" icon small
                   :href="`http://tumblr.com/widgets/share/tool?canonicalUrl=${location()}&title=${titleText}`"
                   target="_blank"
                   rel="nofollow noopener">
              <v-icon :icon="siTumblr.path" size="large"/>
            </v-btn>
          </v-col>
          <v-spacer/>
        </v-row>
      </v-col>
    </v-row>
    <ac-expanded-property v-model="showQr" class="qr-modal" aria-label="QR Code display modal">
      <v-row>
        <v-col class="text-center" cols="12">
          <div v-html="image" class="qrcode" v-if="image"></div>
        </v-col>
        <v-col class="text-center" cols="12">
          Show this QR code to someone and have them scan it with their camera app to quickly link them.
        </v-col>
      </v-row>
    </ac-expanded-property>
    <slot name="footer"/>
  </ac-expanded-property>
</template>

<style>
.qrcode {
  width: 160px;
  height: 160px;
  margin-top: 15px;
  display: inline-block;
}
</style>

<script setup lang="ts">
import {useViewer} from '../mixins/viewer.ts'
import {defaultDialogProps, DialogProps} from '../mixins/dialog.ts'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import QRCode from 'qrcode'
import {siPinterest, siReddit, siX, siTumblr, siTelegram} from 'simple-icons'
import {mdiShare, mdiQrcode} from '@mdi/js'
import {computed, ref, watch} from 'vue'
import {useRoute, useRouter} from 'vue-router'

declare interface ExtraReferred {
  [key: string]: string,
}

declare interface AcShareButtonProps extends DialogProps {
  social?: boolean,
  title: string,
  block?: boolean,
  mediaUrl: string,
  clean: boolean|null,
}

const props = withDefaults(
  defineProps<AcShareButtonProps>(),
  {...defaultDialogProps(), block: false, social: true},
)

const showModal = ref(false)
const referral = ref(true)
const showQr = ref(false)
const image = ref('')

const {isRegistered, rawViewerName} = useViewer()
const router = useRouter()
const route = useRoute()

watch(showQr, (newVal, oldVal) => {
  if (oldVal && !newVal) {
    showModal.value = false
  }
})

const titleText = computed(() => encodeURIComponent(props.title))

const rawLocation = (extraReferred?: ExtraReferred) => {
  /* istanbul ignore next */
  const newRoute = {
    ...route,
    name: route.name || undefined,
  }
  newRoute.name = newRoute.name || undefined
  const query = {...route.query}
  if (referral.value && isRegistered.value) {
    query.referred_by = rawViewerName.value
    Object.assign(query, extraReferred || {})
  } else {
    delete query.referred_by
  }
  newRoute.query = query
  return window.location.protocol + '//' + window.location.host + router.resolve(newRoute).href
}

const location = (extraReferred?: ExtraReferred) => encodeURIComponent(rawLocation(extraReferred))

const baseRawLocation = computed(() => rawLocation())

const renderCode = () => {
  QRCode.toString(rawLocation(), {}, (err: Error | null | undefined, str: string) => {
    /* istanbul ignore if */
    if (err) {
      console.error(err)
    }
    image.value = str
  })
}
watch(baseRawLocation, renderCode, {immediate: true})

// Used in tests.
defineExpose({referral, showModal, baseRawLocation, showQr})
</script>
