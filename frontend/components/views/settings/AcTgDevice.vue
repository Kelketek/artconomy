<template>
  <v-row no-gutters   v-if="device.x">
    <v-col cols="12" sm="4" offset-sm="4" v-if="device.x.confirmed">
      <v-card class="elevation-7">
        <v-card-text>
          <v-row>
            <v-col class="text-center" cols="6" sm="12" order="2" order-sm="1"  :class="{'two-factor-label': $vuetify.breakpoint.xsOnly}">
              <!--suppress HtmlUnknownTarget -->
              <img src="/static/images/telegram_logo.svg" style="height: 10vh" alt="Telegram Logo"/>
            </v-col>
            <v-col cols="6" sm="12" order="1" order-sm="2" class="two-factor-label text-center">
              <p><strong>You have Telegram Two Factor Authentication enabled!</strong></p>
            </v-col>
            <v-col class="text-center" cols="12" order="2" order-sm="3" >
              <p>You will be prompted for a code on each login, keeping your account extra secure.</p>
            </v-col>
            <v-col class="text-center" cols="12" order="3" >
              <ac-confirmation :action="device.delete">
                <template v-slot:default="{on}">
                  <v-btn color="red" class="delete-phone-2fa" v-on="on">Disable Telegram 2FA</v-btn>
                </template>
                <div slot="confirmation-text">
                  Are you sure you wish to remove Telegram 2FA? Removing 2FA makes your account less secure.
                  You should only do this if you no longer use the Telegram account on file or believe it
                  has been compromised.
                </div>
              </ac-confirmation>
            </v-col>
          </v-row>
        </v-card-text>
      </v-card>
    </v-col>
    <v-col v-else cols="12">
      <v-stepper v-model="step" vertical non-linear>
        <v-stepper-step step="1" editable>
          Add our Telegram bot
        </v-stepper-step>
        <v-stepper-content step="1">
          <v-card class="lighten-1">
            <v-card-text>
              <v-row no-gutters  >
                <v-col class="text-center" cols="12" >
                  <a :href="subject.telegram_link" target="_blank" @click="step = 2">
                    <v-avatar
                        size="20vh"
                        color="purple"
                        class="elevation-2"
                    >
                      <!--suppress HtmlUnknownTarget -->
                      <img src="/static/images/logo.png" alt="Bot Avatar">
                    </v-avatar>
                  </a>
                </v-col>
                <v-col class="text-center" >
                  <a :href="subject.telegram_link" target="_blank" style="text-decoration: underline;"
                     @click="step = 2">
                    Click to add our Telegram Bot!</a>
                  <p>Press the 'start' button when prompted, then return here.</p>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
          <v-row>
            <v-col class="shrink">
              <v-btn color="primary" @click="step = 2">Continue</v-btn>
            </v-col>
            <v-col class="shrink">
              <v-btn @click="device.delete">Cancel</v-btn>
            </v-col>
          </v-row>
        </v-stepper-content>
        <v-stepper-step step="2" editable>
          Send Verification Code
        </v-stepper-step>
        <v-stepper-content step="2">
          <v-card class="lighten-1">
            <v-card-text>
              <v-row no-gutters>
                <v-col class="text-center" >
                  <v-btn color="primary" @click="sendTGCode" class="send-tg-code">Send Code</v-btn>
                  <p>Click the button to send a verification code to Telegram!</p>
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
        <v-stepper-step step="3" editable>
          Verify Code
        </v-stepper-step>
        <v-stepper-content step="3">
          <v-card class="lighten-1">
            <v-card-text>
              <v-row no-gutters  >
                <v-col class="text-center" cols="12" >
                  <p>Finally, enter the code in the field below, and you're all done!</p>
                </v-col>
                <v-col class="text-center" cols="12" sm="8" offset-sm="2" md="4" offset-md="4" >
                  <ac-form @submit.prevent="form.submitThen(device.setX)">
                    <ac-form-container v-bind="form.bind">
                      <v-text-field v-bind="form.fields.code.bind" v-on="form.fields.code.on" v-mask="'### ###'">
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
import Component, {mixins} from 'vue-class-component'
import {SingleController} from '@/store/singles/controller'
import {TGDevice} from '@/store/profiles/types/TGDevice'
import {FormController} from '@/store/forms/form-controller'
import {artCall} from '@/lib/lib'
import Subjective from '@//mixins/subjective'
import {Prop, Watch} from 'vue-property-decorator'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import {HttpVerbs} from '@/store/forms/types/HttpVerbs'
import AcForm from '@/components/wrappers/AcForm.vue'
import {mask} from 'vue-the-mask'

  @Component({
    components: {AcForm, AcConfirmation, AcFormContainer},
    directives: {mask},
  })
export default class AcTgDevice extends mixins(Subjective) {
    @Prop({required: true})
    private device!: SingleController<TGDevice>

    private form: FormController = null as unknown as FormController
    private step: number = 1

    public created() {
      this.form = this.$getForm('telegramOTP', {
        method: 'patch',
        endpoint: this.url,
        fields: {code: {value: null, validators: [{name: 'required'}]}},
      })
    }

    private sendTGCode() {
      this.step = 3
      artCall({url: this.url, method: 'post'}).then()
    }

    @Watch('url')
    private updateEndpoints(val: string) {
      this.form.endpoint = val
    }

    private get url() {
      return `/api/profiles/account/${this.username}/auth/two-factor/tg/`
    }
}
</script>
