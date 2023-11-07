<template>
  <v-col no-gutters v-if="device.x">
    <v-row>
      <v-col v-if="device.x.confirmed" cols="12">
        <v-card class="elevation-7">
          <v-card-text>
            <v-row>
              <v-col class="text-center" cols="12" sm="12" order="2" order-sm="1"
                     :class="{'two-factor-label': $vuetify.display.xs}">
                <!--suppress HtmlUnknownTarget -->
                <img :src="telegramLogo" style="height: 10vh" alt="Telegram Logo"/>
              </v-col>
              <v-col cols="12" order="1" order-sm="2" class="two-factor-label text-center">
                <p><strong>You have Telegram Two Factor Authentication enabled!</strong></p>
              </v-col>
              <v-col class="text-center" cols="12" order="2" order-sm="3">
                <p>You will be prompted for a code on each login, keeping your account extra secure.</p>
              </v-col>
              <v-col class="text-center" cols="12" order="3">
                <ac-confirmation :action="() => device.delete().then(() => $emit('removed'))">
                  <template v-slot:default="{on}">
                    <v-btn color="red" class="delete-phone-2fa" v-on="on" variant="elevated">Disable Telegram 2FA
                    </v-btn>
                  </template>
                  <template v-slot:confirmation-text>
                    <div>
                      Are you sure you wish to remove Telegram 2FA? Removing 2FA makes your account less secure.
                      You should only do this if you no longer use the Telegram account on file or believe it
                      has been compromised.
                    </div>
                  </template>
                </ac-confirmation>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
      <v-col v-else cols="12">
        <v-stepper v-model="step" non-linear>
          <v-stepper-header>
            <v-stepper-item :value="1">
              <template v-slot:title>Add Bot</template>
            </v-stepper-item>
            <v-stepper-item :value="2">
              <template v-slot:title>Send Code</template>
            </v-stepper-item>
            <v-stepper-item :value="3">
              <template v-slot:title>Verify Code</template>
            </v-stepper-item>
          </v-stepper-header>
          <v-stepper-window>
            <v-stepper-window-item :value="1">
              <v-card class="lighten-1">
                <v-card-text>
                  <v-row no-gutters>
                    <v-col class="text-center" cols="12">
                      <a :href="subject!.telegram_link" target="_blank" @click="step = 2">
                        <v-avatar
                            size="20vh"
                            color="purple"
                            class="elevation-2"
                        >
                          <!--suppress HtmlUnknownTarget -->
                          <img :src="logo" alt="Bot Avatar">
                        </v-avatar>
                      </a>
                    </v-col>
                    <v-col class="text-center">
                      <a :href="subject!.telegram_link" target="_blank" style="text-decoration: underline;"
                         @click="step = 2">
                        Click to add our Telegram Bot!</a>
                      <p>Press the 'start' button when prompted, then return here.</p>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
              <v-card-actions row wrap>
                <v-spacer />
                <v-btn @click="device.delete" variant="flat">Cancel</v-btn>
                <v-btn color="primary" @click="step = 2" variant="flat">Continue</v-btn>
              </v-card-actions>
            </v-stepper-window-item>
            <v-stepper-window-item :value="2">
              <v-card class="lighten-1">
                <v-card-text>
                  <v-row no-gutters>
                    <v-col class="text-center">
                      <v-btn color="primary" @click="sendTGCode" class="send-tg-code" variant="flat">Send Code</v-btn>
                      <p>Click the button to send a verification code to Telegram!</p>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
              <v-card-actions row wrap>
                <v-spacer />
                <v-btn @click="device.delete" variant="flat">Cancel</v-btn>
                <v-btn @click="step = 1" color="black" variant="flat">Back</v-btn>
                <v-btn color="primary" @click="step = 3" variant="flat">Continue</v-btn>
              </v-card-actions>
            </v-stepper-window-item>
            <v-stepper-window-item :value="3">
              <v-card class="lighten-1">
                <v-card-text>
                  <v-row no-gutters>
                    <v-col class="text-center" cols="12">
                      <p>Finally, enter the code in the field below, and you're all done!</p>
                    </v-col>
                    <v-col class="text-center" cols="12" sm="8" offset-sm="2" md="4" offset-md="4">
                      <ac-form @submit.prevent="form.submitThen(device.setX)">
                        <ac-form-container v-bind="form.bind">
                          <v-text-field v-bind="form.fields.code.bind" v-mask="'### ###'">
                          </v-text-field>
                          <v-btn color="primary" type="submit" class="submit-button" variant="flat">Verify</v-btn>
                        </ac-form-container>
                      </ac-form>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
              <v-card-actions row wrap>
                <v-spacer />
                <v-btn @click="device.delete" variant="flat">Cancel</v-btn>
                <v-btn @click="step = 2" color="black" variant="flat">Back</v-btn>
              </v-card-actions>
            </v-stepper-window-item>
          </v-stepper-window>
        </v-stepper>
      </v-col>
    </v-row>
  </v-col>
</template>

<script lang="ts">
import {Component, mixins, Prop, toNative, Watch} from 'vue-facing-decorator'
import {SingleController} from '@/store/singles/controller'
import {TGDevice} from '@/store/profiles/types/TGDevice'
import {FormController} from '@/store/forms/form-controller'
import {artCall, BASE_URL} from '@/lib/lib'
import Subjective from '@//mixins/subjective'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import AcForm from '@/components/wrappers/AcForm.vue'

@Component({
  components: {
    AcForm,
    AcConfirmation,
    AcFormContainer,
  },
})
class AcTgDevice extends mixins(Subjective) {
  @Prop({required: true})
  public device!: SingleController<TGDevice>

  public form: FormController = null as unknown as FormController
  public step: number = 1

  public telegramLogo = new URL('/static/images/telegram_logo.svg', BASE_URL).href
  public logo = new URL('/static/images/logo.png', BASE_URL).href

  public created() {
    this.form = this.$getForm('telegramOTP', {
      method: 'patch',
      endpoint: this.url,
      fields: {
        code: {
          value: null,
          validators: [{name: 'required'}],
        },
      },
    })
  }

  public sendTGCode() {
    this.step = 3
    artCall({
      url: this.url,
      method: 'post',
    }).then()
  }

  @Watch('url')
  public updateEndpoints(val: string) {
    this.form.endpoint = val
  }

  public get url() {
    return `/api/profiles/account/${this.username}/auth/two-factor/tg/`
  }
}

export default toNative(AcTgDevice)
</script>
