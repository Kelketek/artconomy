<template>
  <fragment>
    <v-btn color="primary" @click="showModal = true" :block="block">
      <v-icon left>share</v-icon>
      Share
    </v-btn>
    <ac-expanded-property v-model="showModal">
      <span slot="title">Share this!</span>
      <v-layout row wrap v-if="social">
        <v-flex text-xs-center xs12>
          <v-checkbox
              label="Include referral information"
              hint="Includes your username in URL to credit for rewards."
              :persistent-hint="true"
              v-model="referral"
              v-if="isRegistered"
              class="referral-check"
          />
        </v-flex>
        <v-flex text-xs-center xs12>
          <v-btn color="purple" icon large @click="showQr = true"><v-icon>fa-qrcode</v-icon></v-btn>
          <v-btn color="red" icon large :href="`https://reddit.com/submit?url=${location}&title=${titleText}`"
                 rel="nofollow"
                 target="_blank">
            <v-icon large>fa-reddit</v-icon>
          </v-btn>
          <v-btn color="blue" icon large :href="`https://telegram.me/share/url?url=${location}`"
                 target="_blank"
                 rel="nofollow"
          >
            <v-icon large>fa-telegram</v-icon>
          </v-btn>
          <v-btn color="blue" icon large
                 :href="`https://twitter.com/share?text=${titleText}&url=${location}&hashtags=Artconomy`"
                 target="_blank"
                 rel="nofollow">
            <v-icon>fa-twitter</v-icon>
          </v-btn>
          <v-btn color="grey darken-4" icon large :href="`https://www.tumblr.com/share/link?url=${location}&name=${titleText}`"
                 target="_blank"
                 rel="nofollow">
            <v-icon>fa-tumblr</v-icon>
          </v-btn>
        </v-flex>
      </v-layout>
      <ac-expanded-property v-model="showQr">
        <v-layout row wrap>
          <v-flex class="text-xs-center" xs12>
            <div v-html="image" class="qrcode" v-if="image"></div>
          </v-flex>
          <v-flex xs12 text-xs-center>
            Show this QR code to someone and have them scan it with their camera app to quickly link them.
          </v-flex>
        </v-layout>
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

  @Watch('showQr')
  public syncClose(newVal: boolean, oldVal: boolean) {
    if (oldVal && !newVal) {
      this.showModal = false
    }
  }

  @Watch('location', {immediate: true})
  public renderCode() {
    QRCode.toString(this.rawLocation, {}, (err: Error, str: string) => {
      if (err) {
        console.error(err)
      }
      this.image = str
    })
  }
  public get titleText() {
    return encodeURIComponent(this.title)
  }
  public get rawLocation() {
    const route = {...this.$route}
    const query = {...this.$route.query}
    if (this.referral && this.isRegistered) {
      query.referred_by = this.rawViewerName
    } else {
      delete query.referred_by
    }
    route.query = query
    return window.location.protocol + '//' + window.location.host + this.$router.resolve(route).href
  }
  public get location() {
    return encodeURIComponent(
      this.rawLocation
    )
  }
}
</script>

<style scoped>

</style>
