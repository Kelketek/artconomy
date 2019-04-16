<!--suppress JSUnusedLocalSymbols, HtmlUnknownTarget -->
<template>
  <div>
    <v-layout row wrap>
      <v-flex v-if="noDevice">
        <p>Two Factor Authentication (2FA) helps keep your account secure. If someone discovers your password,
          they still will not be able to log in without being able to access a device you own.</p>
        <p><strong>Pick a method below to get started!</strong></p>
      </v-flex>
    </v-layout>
    <v-layout row wrap v-if="noDevice">
      <v-flex text-xs-center xs12 sm4 offset-sm1 d-flex>
        <v-card class="elevation-7 setup-totp" @click="totpDevices.postPush({name: 'Phone'})">
          <v-card-text>
            <v-layout row wrap>
              <v-flex xs6 sm12 order-xs2 order-sm1 px-2>
                <img src="/static/images/iphone.svg" style="height: 10vh" alt="Smartphone"/>
              </v-flex>
              <v-flex xs6 sm12 order-xs1 order-sm2 class="two-factor-label">
                <strong>Set up Phone App</strong>
              </v-flex>
            </v-layout>
          </v-card-text>
        </v-card>
      </v-flex>
      <v-flex text-xs-center xs12 sm4 offset-sm1 d-flex>
        <v-card class="elevation-7 setup-telegram" @click="tgDevice.put()">
          <v-card-text>
            <v-layout row wrap>
              <v-flex xs6 sm12 order-xs2 order-sm1 px-2>
                <img src="/static/images/telegram_logo.svg" style="height: 10vh" alt="Telegram logo"/>
              </v-flex>
              <v-flex xs6 sm12 order-xs1 order-sm2 class="two-factor-label">
                <div><strong>Set up Telegram</strong></div>
              </v-flex>
            </v-layout>
          </v-card-text>
        </v-card>
      </v-flex>
    </v-layout>
    <ac-tg-device v-if="tgDevice.x" :username="username" :device="tgDevice"></ac-tg-device>
    <v-flex v-if="totpDevices">
    <ac-totp-device
        v-for="device in totpDevices.list"
        :key="device.x.id" :device="device" :username="username">
    </ac-totp-device>
    </v-flex>
  </div>
</template>

<style>
  .two-factor-label {
    justify-content: center;
    flex-direction: column;
    display: flex;
  }
</style>

<script lang="ts">
import Viewer from '@/mixins/viewer'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import AcTotpDevice from './AcTotpDevice.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import Component, {mixins} from 'vue-class-component'
import Subjective from '@/mixins/subjective'
import {TGDevice} from '@/store/profiles/types/TGDevice'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import Alerts from '@/mixins/alerts'
import {TOTPDevice} from '@/store/profiles/types/TOTPDevice'
import {ListController} from '@/store/lists/controller'
import {SingleController} from '@/store/singles/controller'
import {Watch} from 'vue-property-decorator'
import AcTgDevice from './AcTgDevice.vue'

  @Component({components: {AcTgDevice, AcConfirmation, AcFormContainer, AcTotpDevice}})
export default class AcSetupTwoFactor extends mixins(Viewer, Subjective, Alerts) {
    public totpDevices: ListController<TOTPDevice> = null as unknown as ListController<TOTPDevice>
    private showNewDevice: boolean = false
    private tgDevice: SingleController<TGDevice> = null as unknown as SingleController<TGDevice>
    private showTOTPAdd: boolean = false
    private tgStep: number = 1

    public created() {
      this.totpDevices = this.$getList('totpDevices', {endpoint: `${this.url}totp/`})
      this.totpDevices.get().catch(this.$errAlert())
      this.tgDevice = this.$getSingle('tgDevice', {endpoint: `${this.url}tg/`})
      this.tgDevice.get().catch(() => {
        this.tgDevice.x = false
      })
    }

    @Watch('url')
    private updateEndpoints(val: string) {
      this.tgDevice.endpoint = val + 'tg/'
      this.totpDevices.endpoint = val + 'totp/'
    }

    private get url() {
      return `/api/profiles/v1/account/${this.username}/auth/two-factor/`
    }

    private get noDevice() {
      return this.tgDevice.x === false && this.totpDevices.ready && this.totpDevices.list.length === 0
    }
}
</script>
