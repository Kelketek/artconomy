<!--suppress JSUnusedLocalSymbols, HtmlUnknownTarget -->
<template>
  <div>
    <v-row>
      <v-col v-if="noDevice">
        <p>Two Factor Authentication (2FA) helps keep your account secure. If someone discovers your password,
          they still will not be able to log in without being able to access a device you own.</p>
        <p><strong>Pick a method below to get started!</strong></p>
      </v-col>
    </v-row>
    <v-row v-if="noDevice">
      <v-col class="text-center" align-self="center" cols="12" sm="4" offset-sm="1" >
        <v-card class="elevation-7 setup-totp" @click="totpDevices.postPush({name: 'Phone'})">
          <v-card-text>
            <v-row no-gutters>
              <v-col class="px-2" cols="6" sm="12" order="2" order-sm="1" >
                <img src="/static/images/iphone.svg" style="height: 10vh" alt="Smartphone"/>
              </v-col>
              <v-col cols="6" sm="12" order="1" order-sm="2" class="two-factor-label">
                <strong>Set up Phone App</strong>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col class="text-center" align-self="center" cols="12" sm="4" offset-sm="2" >
        <v-card class="elevation-7 setup-telegram" @click="tgDevice.put()">
          <v-card-text>
            <v-row no-gutters  >
              <v-col class="px-2" cols="6" sm="12" order="2" order-sm="1" >
                <img src="/static/images/telegram_logo.svg" style="height: 10vh" alt="Telegram logo"/>
              </v-col>
              <v-col cols="6" sm="12" order="1" order-sm="2" class="two-factor-label">
                <div><strong>Set up Telegram</strong></div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <ac-tg-device v-if="tgDevice.x" :username="username" :device="tgDevice" />
    <v-col v-if="totpDevices">
    <ac-totp-device
        v-for="device in totpDevices.list"
        :key="device.x.id" :device="device" :username="username">
    </ac-totp-device>
    </v-col>
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
      this.totpDevices.firstRun().catch(this.$errAlert())
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
