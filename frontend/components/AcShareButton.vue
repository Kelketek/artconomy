<template>
  <v-btn color="primary" @click="showModal = true" :block="block" variant="flat" class="share-button">
    <v-icon left icon="mdi-share"/>
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
              <v-icon icon="mdi-qrcode" size="large" />
            </v-btn>
          </v-col>
          <v-col class="shrink" v-if="clean">
            <v-btn color="red" icon small
                   :href="`https://www.pinterest.com/pin/create/button/?canonicalUrl=${location({mtm_campaign: 'Pinned'})}&description=${titleText}&media=${encodeURIComponent(mediaUrl)}`"
                   rel="nofollow noopener"
                   target="_blank">
              <ac-icon :icon="siPinterest" size="large" />
            </v-btn>
          </v-col>
          <v-col class="shrink">
            <v-btn color="red" icon small :href="`https://reddit.com/submit?url=${location()}&title=${titleText}`"
                   rel="nofollow noopener"
                   target="_blank">
              <ac-icon :icon="siReddit" size="large" />
            </v-btn>
          </v-col>
          <v-col class="shrink">
            <v-btn color="blue" icon small :href="`https://telegram.me/share/url?url=${location()}`"
                   target="_blank"
                   rel="nofollow noopener"
            >
              <ac-icon :icon="siTelegram" size="large" />
            </v-btn>
          </v-col>
          <v-col class="shrink">
            <v-btn color="blue" icon small
                   :href="`https://twitter.com/share?text=${titleText}&url=${location()}&hashtags=Artconomy`"
                   target="_blank"
                   rel="nofollow noopener">
              <ac-icon :icon="siX" size="large" />
            </v-btn>
          </v-col>
          <v-col class="shrink">
            <v-btn color="grey darken-4" icon small
                   :href="`http://tumblr.com/widgets/share/tool?canonicalUrl=${location()}&title=${titleText}`"
                   target="_blank"
                   rel="nofollow noopener">
              <ac-icon :icon="siTumblr" size="large" />
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
    <slot name="footer" />
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

<script lang="ts">
import Viewer from '../mixins/viewer.ts'
import {Component, mixins, Prop, toNative, Watch} from 'vue-facing-decorator'
import Dialog from '../mixins/dialog.ts'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import QRCode from 'qrcode'
import {siPinterest, siReddit, siX, siTumblr, siTelegram} from 'simple-icons'
import AcIcon from '@/components/AcIcon.vue'

declare interface ExtraReferred {
  [key: string]: string,
}

@Component({components: {AcExpandedProperty, AcIcon}})
class AcShareButton extends mixins(Dialog, Viewer) {
  @Prop({default: true})
  public social!: boolean

  @Prop({required: true})
  public title!: string

  public showModal = false
  public referral = true
  public showQr = false
  public image = ''
  @Prop()
  public block!: boolean

  public siPinterest = siPinterest
  public siTumblr = siTumblr
  public siReddit = siReddit
  public siX = siX
  public siTelegram = siTelegram

  // "Clean" art suitable for general audiences. Useful for social networks with restrictions.
  @Prop({required: true})
  public clean!: boolean

  @Prop({required: true})
  public mediaUrl!: string

  @Watch('showQr')
  public syncClose(newVal: boolean, oldVal: boolean) {
    if (oldVal && !newVal) {
      this.showModal = false
    }
  }

  @Watch('location', {immediate: true})
  public renderCode() {
    QRCode.toString(this.rawLocation(), {}, (err: Error | null | undefined, str: string) => {
      /* istanbul ignore if */
      if (err) {
        console.error(err)
      }
      this.image = str
    })
  }

  public get titleText() {
    return encodeURIComponent(this.title)
  }

  public rawLocation(extraReferred?: ExtraReferred) {
    /* istanbul ignore next */
    const route = {
      ...this.$route,
      name: this.$route.name || undefined,
    }
    route.name = route.name || undefined
    const query = {...this.$route.query}
    if (this.referral && this.isRegistered) {
      query.referred_by = this.rawViewerName
      Object.assign(query, extraReferred || {})
    } else {
      delete query.referred_by
    }
    route.query = query
    return window.location.protocol + '//' + window.location.host + this.$router.resolve(route).href
  }

  public location(extraReferred?: ExtraReferred) {
    return encodeURIComponent(
        this.rawLocation(extraReferred),
    )
  }
}

export default toNative(AcShareButton)
</script>

<style scoped>

</style>
