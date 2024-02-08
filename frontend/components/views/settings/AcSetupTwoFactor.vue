<!--suppress JSUnusedLocalSymbols, HtmlUnknownTarget -->
<template>
  <v-col>
    <v-row>
      <v-col v-if="noDevice" cols="12">
        <p>Two Factor Authentication (2FA) helps keep your account secure. If someone discovers your password,
          they still will not be able to log in without being able to access a device you own.</p>
        <p><strong>Pick a method below to get started!</strong></p>
      </v-col>
      <v-col cols="12" v-if="noDevice">
        <v-row>
          <v-col class="text-center" align-self="center" cols="12" sm="4" offset-sm="1">
            <v-card class="elevation-7 setup-totp" @click="totpDevices.postPush({name: 'Phone'})">
              <v-card-text>
                <v-row no-gutters>
                  <v-col class="px-2" cols="6" sm="12" order="2" order-sm="1">
                    <img :src="iphone.href" style="height: 10vh" alt="Smartphone"/>
                  </v-col>
                  <v-col cols="6" sm="12" order="1" order-sm="2" class="two-factor-label">
                    <strong>Set up Phone App</strong>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>
          <v-col class="text-center" align-self="center" cols="12" sm="4" offset-sm="2">
            <v-card class="elevation-7 setup-telegram" @click="tgDevice.put()">
              <v-card-text>
                <v-row no-gutters>
                  <v-col class="px-2" cols="6" sm="12" order="2" order-sm="1">
                    <img :src="telegramLogo" style="height: 10vh" alt="Telegram logo"/>
                  </v-col>
                  <v-col cols="6" sm="12" order="1" order-sm="2" class="two-factor-label">
                    <div><strong>Set up Telegram</strong></div>
                  </v-col>
                </v-row>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-col>
      <v-col cols="12">
        <ac-tg-device v-if="tgDevice.x" :username="username" :device="tgDevice"/>
      </v-col>
      <v-col v-if="totpDevices" cols="12">
        <ac-totp-device
            v-for="device in totpDevices.list"
            :key="device.x!.id" :device="device" :username="username" />
      </v-col>
    </v-row>
  </v-col>
</template>

<style>
.two-factor-label {
  justify-content: center;
  flex-direction: column;
  display: flex;
}
</style>

<script lang="ts">
import Viewer from '@/mixins/viewer.ts'
import AcTotpDevice from './AcTotpDevice.vue'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import {Component, mixins, toNative, Watch} from 'vue-facing-decorator'
import Subjective from '@/mixins/subjective.ts'
import {TGDevice} from '@/store/profiles/types/TGDevice.ts'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import Alerts from '@/mixins/alerts.ts'
import {TOTPDevice} from '@/store/profiles/types/TOTPDevice.ts'
import {ListController} from '@/store/lists/controller.ts'
import {SingleController} from '@/store/singles/controller.ts'
import AcTgDevice from './AcTgDevice.vue'
import {BASE_URL} from '@/lib/lib.ts'

@Component({
  components: {
    AcTgDevice,
    AcConfirmation,
    AcFormContainer,
    AcTotpDevice,
  },
})
class AcSetupTwoFactor extends mixins(Viewer, Subjective, Alerts) {
  public totpDevices: ListController<TOTPDevice> = null as unknown as ListController<TOTPDevice>
  public showNewDevice: boolean = false
  public tgDevice: SingleController<TGDevice> = null as unknown as SingleController<TGDevice>
  public showTOTPAdd: boolean = false
  public tgStep: number = 1
  public iphone = new URL('/static/images/iphone.svg', BASE_URL)
  public telegramLogo = new URL('/static/images/telegram_logo.svg', BASE_URL).href

  public created() {
    this.totpDevices = this.$getList('totpDevices', {endpoint: `${this.url}totp/`})
    this.totpDevices.firstRun().catch(this.$errAlert())
    this.tgDevice = this.$getSingle('tgDevice', {endpoint: `${this.url}tg/`})
    this.tgDevice.get().catch(() => {
      this.tgDevice.ready = true
    })
  }

  @Watch('url')
  public updateEndpoints(val: string) {
    this.tgDevice.endpoint = val + 'tg/'
    this.totpDevices.endpoint = val + 'totp/'
  }

  public get url() {
    return `/api/profiles/account/${this.username}/auth/two-factor/`
  }

  public get noDevice() {
    return (
        this.tgDevice.x === null
        && (this.tgDevice.ready || this.tgDevice.deleted)
        && this.totpDevices.ready
        && this.totpDevices.list.length === 0
    )
  }
}

export default toNative(AcSetupTwoFactor)
</script>
