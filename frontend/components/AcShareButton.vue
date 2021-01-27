<template>
  <fragment>
    <v-btn color="primary" @click="showModal = true" :block="block" class="share-button">
      <v-icon left>share</v-icon>
      Share
    </v-btn>
    <ac-expanded-property v-model="showModal">
      <span slot="title">Share this!</span>
      <v-row no-gutters   v-if="social">
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
            <v-spacer />
            <v-col class="shrink">
              <v-btn color="purple" fab small @click="showQr = true" class="qr-button"><v-icon>fa-qrcode</v-icon></v-btn>
            </v-col>
            <v-col class="shrink" v-if="clean">
              <v-btn color="red" fab small :href="`https://www.pinterest.com/pin/create/button/?canonicalUrl=${this.location({mtm_campaign: 'Pinned'})}&description=${this.titleText}&media=${encodeURIComponent(this.mediaUrl)}`"
                     rel="nofollow noopener"
                     target="_blank">
                <v-icon>fa-pinterest</v-icon>
              </v-btn>
            </v-col>
            <v-col class="shrink">
              <v-btn color="red" fab small :href="`https://reddit.com/submit?url=${location()}&title=${titleText}`"
                     rel="nofollow noopener"
                     target="_blank">
                <v-icon>fa-reddit</v-icon>
              </v-btn>
            </v-col>
            <v-col class="shrink">
              <v-btn color="blue" fab small :href="`https://telegram.me/share/url?url=${location()}`"
                     target="_blank"
                     rel="nofollow noopener"
              >
                <v-icon>fa-telegram</v-icon>
              </v-btn>
            </v-col>
            <v-col class="shrink">
              <v-btn color="blue" fab small
                     :href="`https://twitter.com/share?text=${titleText}&url=${location()}&hashtags=Artconomy`"
                     target="_blank"
                     rel="nofollow noopener">
                <v-icon>fa-twitter</v-icon>
              </v-btn>
            </v-col>
            <v-col class="shrink">
              <v-btn color="grey darken-4" fab small :href="`https://www.tumblr.com/share/link?url=${location()}&name=${titleText}`"
                     target="_blank"
                     rel="nofollow noopener">
                <v-icon>fa-tumblr</v-icon>
              </v-btn>
            </v-col>
            <v-spacer />
          </v-row>
        </v-col>
      </v-row>
      <ac-expanded-property v-model="showQr" class="qr-modal">
        <v-row no-gutters  >
          <v-col class="text-center" cols="12">
            <div v-html="image" class="qrcode" v-if="image"></div>
          </v-col>
          <v-col class="text-center" cols="12" >
            Show this QR code to someone and have them scan it with their camera app to quickly link them.
          </v-col>
        </v-row>
      </ac-expanded-property>
      <slot name="footer"></slot>
    </ac-expanded-property>
  </fragment>
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
import Viewer from '../mixins/viewer'
import {Fragment} from 'vue-fragment'
import Component, {mixins} from 'vue-class-component'
import Dialog from '../mixins/dialog'
import {Prop, Watch} from 'vue-property-decorator'
import AcExpandedProperty from '@/components/wrappers/AcExpandedProperty.vue'
import QRCode from 'qrcode'

declare interface ExtraReferred {
  [key: string]: string,
}

@Component({components: {AcExpandedProperty, Fragment}})
export default class AcShareButton extends mixins(Dialog, Viewer) {
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
    QRCode.toString(this.rawLocation(), {}, (err: Error, str: string) => {
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
    const route = {...this.$route, name: this.$route.name || undefined}
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

  public location(extraReferred: ExtraReferred) {
    return encodeURIComponent(
      this.rawLocation(extraReferred),
    )
  }
}
</script>

<style scoped>

</style>
