<template>
  <v-layout row wrap v-if="device.x">
    <v-flex xs12 sm4 offset-sm4 v-if="device.x.confirmed">
      <v-card class="elevation-7">
        <v-card-text>
          <v-layout row wrap>
            <v-flex xs6 sm12 order-xs2 order-sm1 px-2 text-xs-center
                    :class="{'two-factor-label': $vuetify.breakpoint.xsOnly}">
              <!--suppress HtmlUnknownTarget -->
              <img src="/static/images/telegram_logo.svg" style="height: 10vh" alt="Telegram Logo"/>
            </v-flex>
            <v-flex xs6 sm12 order-xs1 order-sm2 text-xs-center class="two-factor-label">
              <p><strong>You have Telegram Two Factor Authentication enabled!</strong></p>
            </v-flex>
            <v-flex xs12 order-xs2 order-sm3 text-xs-center>
              <p>You will be prompted for a code on each login, keeping your account extra secure.</p>
            </v-flex>
            <v-flex xs12 order-xs3 text-xs-center>
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
            </v-flex>
          </v-layout>
        </v-card-text>
      </v-card>
    </v-flex>
    <v-flex v-else xs12>
      <v-stepper v-model="step" vertical non-linear>
        <v-stepper-step step="1" editable>
          Add our Telegram bot
        </v-stepper-step>
        <v-stepper-content step="1">
          <v-card class="lighten-1">
            <v-card-text>
              <v-layout row wrap>
                <v-flex xs12 text-xs-center>
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
                </v-flex>
                <v-flex text-xs-center>
                  <a :href="subject.telegram_link" target="_blank" style="text-decoration: underline;"
                     @click="step = 2">
                    Click to add our Telegram Bot!</a>
                  <p>Press the 'start' button when prompted, then return here.</p>
                </v-flex>
              </v-layout>
            </v-card-text>
          </v-card>
          <v-btn color="primary" @click="step = 2">Continue</v-btn>
          <v-btn flat @click="device.delete">Cancel</v-btn>
        </v-stepper-content>
        <v-stepper-step step="2" editable>
          Send Verification Code
        </v-stepper-step>
        <v-stepper-content step="2">
          <v-card class="lighten-1">
            <v-card-text>
              <v-layout>
                <v-flex text-xs-center>
                  <v-btn color="primary" @click="sendTGCode" class="send-tg-code">Send Code</v-btn>
                  <p>Click the button to send a verification code to Telegram!</p>
                </v-flex>
              </v-layout>
            </v-card-text>
          </v-card>
          <v-btn color="primary" @click="step = 3">Continue</v-btn>
          <v-btn @click="step = 1">Back</v-btn>
          <v-btn flat @click="device.delete">Cancel</v-btn>
        </v-stepper-content>
        <v-stepper-step step="3" editable>
          Verify Code
        </v-stepper-step>
        <v-stepper-content step="3">
          <v-card class="lighten-1">
            <v-card-text>
              <v-layout row wrap>
                <v-flex xs12 text-xs-center>
                  <p>Finally, enter the code in the field below, and you're all done!</p>
                </v-flex>
                <v-flex xs12 sm8 offset-sm2 md4 offset-md4 text-xs-center>
                  <form @submit.prevent="form.submitThen(device.setX)">
                    <ac-form-container v-bind="form.bind">
                      <v-text-field v-bind="form.fields.code.bind" v-on="form.fields.code.on" mask="### ###">
                      </v-text-field>
                      <v-btn color="primary" type="submit" class="submit-button">Verify</v-btn>
                    </ac-form-container>
                  </form>
                </v-flex>
              </v-layout>
            </v-card-text>
          </v-card>
          <v-btn @click="step = 2">Back</v-btn>
          <v-btn flat @click="device.delete">Cancel</v-btn>
        </v-stepper-content>
      </v-stepper>
    </v-flex>
  </v-layout>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import {SingleController} from '@/store/singles/controller'
import {TGDevice} from '@/store/profiles/types/TGDevice'
import {FormController} from '@/store/forms/form-controller'
import {artCall} from '@/lib'
import Subjective from '@//mixins/subjective'
import {Prop, Watch} from 'vue-property-decorator'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import {HttpVerbs} from '@/store/forms/types/HttpVerbs'

  @Component({
    components: {AcConfirmation, AcFormContainer},
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
      return `/api/profiles/v1/account/${this.username}/auth/two-factor/tg/`
    }
}
</script>
