<!--suppress JSMethodCanBeStatic, JSUnusedLocalSymbols, HtmlUnknownTarget -->
<template>
  <v-row no-gutters v-if="device.x">
    <v-col v-if="device.x.confirmed">
      <v-col cols="12" sm="4" offset-sm="4">
        <v-card class="elevation-7">
          <v-card-text>
            <v-row no-gutters  >
              <v-col class="px-2 text-center" cols="4" sm="12" order="2" order-sm="1" >
                <img src="/static/images/iphone.svg" style="height: 10vh" alt="Smartphone"/>
              </v-col>
              <v-col cols="8" sm="12" order="1" order-sm="2" class="two-factor-label text-center">
                <p><strong>You have Two Factor authentication enabled on your phone!</strong></p>
              </v-col>
              <v-col class="text-center" cols="12" order="2" order-sm="3" >
                <p>You will be prompted for a code on each login, keeping your account extra secure.</p>
                <p v-if="device.x.name !== 'Phone'"><strong>Device Name: {{device.x.name}}</strong></p>
              </v-col>
              <v-col class="text-center" cols="12" order="3" >
                <ac-confirmation :action="device.delete">
                  <template v-slot:default="{on}">
                    <v-btn v-on="on" color="red" class="delete-phone-2fa">Disable Phone 2FA</v-btn>
                  </template>
                  <div slot="confirmation-text">
                    Are you sure you wish to remove 2FA? Removing 2FA makes your account less secure.
                    You should only do this if you no longer have this phone, or are expecting to get a new one.
                  </div>
                </ac-confirmation>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-col>
    <v-col v-else>
      <v-stepper v-model="step" vertical non-linear="">
        <v-stepper-step step="1" editable>Install a Compatible App</v-stepper-step>
        <v-stepper-content step="1">
          <v-row no-gutters   class="pb-2">
            <v-col class="text-center" cols="12" sm="4" offset-sm="1">
              <v-card class="elevation-7">
                <v-card-text>
                  <v-row no-gutters  >
                    <v-col cols="12" class="text-center">
                      <h3>Authy</h3>
                    </v-col>
                    <v-col cols="12">
                      <img src="/static/images/authy.png" style="min-width: 60%; max-width: 75%" alt="Authy"/>
                    </v-col>
                    <v-col cols="12">
                      <a href="https://play.google.com/store/apps/details?id=com.authy.authy" target="_blank"
                         @click="step = 2"
                      >
                        <img src="/static/images/Playstore.svg" alt="Download Authy on the Google Play Store">
                      </a>
                    </v-col>
                    <v-col cols="12">
                      <a target="_blank" href="https://itunes.apple.com/us/app/authy/id494168017" @click="step = 2">
                        <img src="/static/images/Appstore.svg" alt="Download Authy on Apple's App Store">
                      </a>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </v-col>
            <v-col class="text-center" cols="12" sm="4" offset-sm="1">
              <v-card class="elevation-7">
                <v-card-text class="text-center">
                  <v-row no-gutters  >
                    <v-col cols="12" class="text-center">
                      <h3>Google Authenticator</h3>
                    </v-col>
                    <v-col cols="12">
                      <img src="/static/images/authenticator.png" style="min-width: 60%; max-width: 75%"
                           alt="Google Authenticator"/>
                    </v-col>
                    <v-col cols="12">
                      <a href="https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2"
                         target="_blank"
                         @click="step = 2"
                      >
                        <img src="/static/images/Playstore.svg" alt="Download Google Authenticator on the Play Store">
                      </a>
                    </v-col>
                    <v-col cols="12">
                      <a target="_blank" href="https://itunes.apple.com/us/app/google-authenticator/id388497605"
                         @click="step = 2"
                      >
                        <img src="/static/images/Appstore.svg" alt="Download Google Authenticator on Apple's App Store">
                      </a>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
          <v-row>
            <v-col class="shrink">
              <v-btn color="primary" @click="step = 2">Continue</v-btn>
            </v-col>
            <v-col class="shrink">
              <v-btn @click="device.delete">Cancel</v-btn>
            </v-col>
          </v-row>
        </v-stepper-content>
        <v-stepper-step step="2" editable>Add Artconomy to App</v-stepper-step>
        <v-stepper-content step="2">
          <v-card class="lighten-1">
            <v-card-text>
              <v-row no-gutters  >
                <v-col class="text-center" cols="12">
                  <div v-html="image" class="qrcode" v-if="image"></div>
                </v-col>
                <v-col class="text-center" cols="12" >
                  Scan the barcode above with your phone or other device.
                  If you are on the device, you can also <a :href="device.config_url">click this link.</a>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
          <v-row>
            <v-col class="shrink">
              <v-btn color="primary" @click="step = 3">Continue</v-btn>
            </v-col>
            <v-col class="shrink">
              <v-btn @click="step = 1" color="black">Back</v-btn>
            </v-col>
            <v-col class="shrink">
              <v-btn @click="device.delete">Cancel</v-btn>
            </v-col>
          </v-row>
        </v-stepper-content>
        <v-stepper-step step="3" editable>Verify</v-stepper-step>
        <v-stepper-content step="3">
          <v-card class="lighten-1">
            <v-card-text>
              <v-row no-gutters  >
                <v-col class="text-center" cols="12" >
                  <p>Finally, enter the code in the field below, and you're all done!</p>
                </v-col>
                <v-col class="text-center" cols="12" sm="8" offset-sm="2" md="4" offset-md="4" >
                  <ac-form @submit.prevent="totpForm.submitThen(device.setX)">
                    <ac-form-container v-bind="totpForm.bind">
                      <v-text-field v-bind="totpForm.fields.code.bind" v-on="totpForm.fields.code.on" v-mask="'### ###'">
                      </v-text-field>
                      <v-btn color="primary" type="submit" class="submit-button">Verify</v-btn>
                    </ac-form-container>
                  </ac-form>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
          <v-row>
            <v-col class="shrink">
              <v-btn @click="step = 2" color="black">Back</v-btn>
            </v-col>
            <v-col class="shrink">
              <v-btn @click="device.delete">Cancel</v-btn>
            </v-col>
          </v-row>
        </v-stepper-content>
      </v-stepper>
    </v-col>
  </v-row>
</template>

<script lang="ts">
import QRCode from 'qrcode'
import Component, {mixins} from 'vue-class-component'
import Subjective from '@//mixins/subjective'
import {Prop, Watch} from 'vue-property-decorator'
import {FormController} from '@/store/forms/form-controller'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import {TOTPDevice} from '@/store/profiles/types/TOTPDevice'
import {SingleController} from '@/store/singles/controller'
import AcForm from '@/components/wrappers/AcForm.vue'
import {mask} from 'vue-the-mask'

@Component({
  components: {AcForm, AcConfirmation, AcFormContainer},
  directives: {mask},
})
export default class AcTotpDevice extends mixins(Subjective) {
  @Prop({required: true})
  private device!: SingleController<TOTPDevice>

  private QRCode = QRCode
  private image: string = ''
  private totpForm: FormController = null as unknown as FormController
  private step: number = 1

  public created() {
    const device = this.device.x as TOTPDevice
    this.totpForm = this.$getForm(device.id + '_totpForm', {
      method: 'patch',
      endpoint: this.url,
      fields: {code: {validators: [{name: 'required'}], value: null}},
    })
    this.renderCode()
  }

  private renderCode() {
    const device = this.device.x as TOTPDevice
    if (device.confirmed) {
      this.image = ''
      return
    }
    QRCode.toString(device.config_url, {}, (err: Error, str: string) => {
      if (err) {
        console.error(err)
      }
      this.image = str
    })
  }

  @Watch('url')
  private updateEndpoints(val: string) {
    this.totpForm.endpoint = val
  }

  private get url() {
    if (!this.device.x) {
      return '#'
    }
    return `/api/profiles/account/${this.username}/auth/two-factor/totp/${this.device.x.id}/`
  }
}
</script>

<style scoped>
  .qrcode {
    width: 160px;
    height: 160px;
    margin-top: 15px;
    display: inline-block;
  }
</style>
