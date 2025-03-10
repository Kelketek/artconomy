<template>
  <v-col
    v-if="device.x"
    no-gutters
  >
    <v-row>
      <v-col
        v-if="device.x.confirmed"
        cols="12"
      >
        <v-card class="elevation-7">
          <v-card-text>
            <v-row>
              <v-col
                class="text-center"
                cols="12"
                sm="12"
                order="2"
                order-sm="1"
                :class="{'two-factor-label': xs}"
              >
                <!--suppress HtmlUnknownTarget -->
                <img
                  :src="telegramLogo"
                  style="height: 10vh"
                  alt="Telegram Logo"
                >
              </v-col>
              <v-col
                cols="12"
                order="1"
                order-sm="2"
                class="two-factor-label text-center"
              >
                <p><strong>You have Telegram Two Factor Authentication enabled!</strong></p>
              </v-col>
              <v-col
                class="text-center"
                cols="12"
                order="2"
                order-sm="3"
              >
                <p>You will be prompted for a code on each login, keeping your account extra secure.</p>
              </v-col>
              <v-col
                class="text-center"
                cols="12"
                order="3"
              >
                <ac-confirmation :action="() => device.delete().then(() => $emit('removed'))">
                  <template #default="{on}">
                    <v-btn
                      color="red"
                      class="delete-phone-2fa"
                      variant="elevated"
                      v-on="on"
                    >
                      Disable Telegram 2FA
                    </v-btn>
                  </template>
                  <template #confirmation-text>
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
      <v-col
        v-else
        cols="12"
      >
        <v-stepper
          v-model="step"
          non-linear
        >
          <v-stepper-header>
            <v-stepper-item :value="1">
              <template #title>
                Add Bot
              </template>
            </v-stepper-item>
            <v-stepper-item :value="2">
              <template #title>
                Send Code
              </template>
            </v-stepper-item>
            <v-stepper-item :value="3">
              <template #title>
                Verify Code
              </template>
            </v-stepper-item>
          </v-stepper-header>
          <v-stepper-window>
            <v-stepper-window-item :value="1">
              <v-card class="lighten-1">
                <v-card-text>
                  <v-row no-gutters>
                    <v-col
                      class="text-center"
                      cols="12"
                    >
                      <a
                        :href="subject!.telegram_link"
                        target="_blank"
                        @click="step = 2"
                      >
                        <v-avatar
                          size="20vh"
                          color="purple"
                          class="elevation-2"
                        >
                          <!--suppress HtmlUnknownTarget -->
                          <img
                            :src="logo"
                            alt="Bot Avatar"
                          >
                        </v-avatar>
                      </a>
                    </v-col>
                    <v-col class="text-center">
                      <a
                        :href="subject!.telegram_link"
                        target="_blank"
                        style="text-decoration: underline;"
                        @click="step = 2"
                      >
                        Click to add our Telegram Bot!</a>
                      <p>Press the 'start' button when prompted, then return here.</p>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
              <v-card-actions
                row
                wrap
              >
                <v-spacer />
                <v-btn
                  variant="flat"
                  @click="device.delete"
                >
                  Cancel
                </v-btn>
                <v-btn
                  color="primary"
                  variant="flat"
                  @click="step = 2"
                >
                  Continue
                </v-btn>
              </v-card-actions>
            </v-stepper-window-item>
            <v-stepper-window-item :value="2">
              <v-card class="lighten-1">
                <v-card-text>
                  <v-row no-gutters>
                    <v-col class="text-center">
                      <v-btn
                        color="primary"
                        class="send-tg-code"
                        variant="flat"
                        @click="sendTGCode"
                      >
                        Send Code
                      </v-btn>
                      <p>Click the button to send a verification code to Telegram!</p>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
              <v-card-actions
                row
                wrap
              >
                <v-spacer />
                <v-btn
                  variant="flat"
                  @click="device.delete"
                >
                  Cancel
                </v-btn>
                <v-btn
                  color="black"
                  variant="flat"
                  @click="step = 1"
                >
                  Back
                </v-btn>
                <v-btn
                  color="primary"
                  variant="flat"
                  @click="step = 3"
                >
                  Continue
                </v-btn>
              </v-card-actions>
            </v-stepper-window-item>
            <v-stepper-window-item :value="3">
              <v-card class="lighten-1">
                <v-card-text>
                  <v-row no-gutters>
                    <v-col
                      class="text-center"
                      cols="12"
                    >
                      <p>Finally, enter the code in the field below, and you're all done!</p>
                    </v-col>
                    <v-col
                      class="text-center"
                      cols="12"
                      sm="8"
                      offset-sm="2"
                      md="4"
                      offset-md="4"
                    >
                      <ac-form @submit.prevent="form.submitThen(device.setX)">
                        <ac-form-container v-bind="form.bind">
                          <v-text-field
                            v-mask-token
                            v-bind="form.fields.code.bind"
                          />
                          <v-btn
                            color="primary"
                            type="submit"
                            class="submit-button"
                            variant="flat"
                          >
                            Verify
                          </v-btn>
                        </ac-form-container>
                      </ac-form>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
              <v-card-actions
                row
                wrap
              >
                <v-spacer />
                <v-btn
                  variant="flat"
                  @click="device.delete"
                >
                  Cancel
                </v-btn>
                <v-btn
                  color="black"
                  variant="flat"
                  @click="step = 2"
                >
                  Back
                </v-btn>
              </v-card-actions>
            </v-stepper-window-item>
          </v-stepper-window>
        </v-stepper>
      </v-col>
    </v-row>
  </v-col>
</template>

<script setup lang="ts">
import {SingleController} from '@/store/singles/controller.ts'
import {useDisplay} from 'vuetify'
import {artCall, BASE_URL} from '@/lib/lib.ts'
import {useSubject} from '@//mixins/subjective.ts'
import AcFormContainer from '@/components/wrappers/AcFormContainer.vue'
import AcConfirmation from '@/components/wrappers/AcConfirmation.vue'
import AcForm from '@/components/wrappers/AcForm.vue'
import {vMaskToken} from '@/lib/vMask.ts'
import {useForm} from '@/store/forms/hooks.ts'
import {computed, ComputedRef, ref, watch} from 'vue'
import type {SubjectiveProps, TGDevice} from '@/types/main'
import {User} from '@/store/profiles/types/main'

const telegramLogo = new URL('/static/images/telegram_logo.svg', BASE_URL).href
const logo = new URL('/static/images/logo.png', BASE_URL).href
const {xs} = useDisplay()

declare interface AcTgDeviceProps {
  device: SingleController<TGDevice>
}

const props = defineProps<AcTgDeviceProps & SubjectiveProps>()
const subjectTraits = useSubject({ props })
const subject = subjectTraits.subject as ComputedRef<User>
const step = ref(1)

const url = computed(() => `/api/profiles/account/${props.username}/auth/two-factor/tg/`)

const form = useForm('telegramOTP', {
  method: 'patch',
  endpoint: url.value,
  fields: {
    code: {
      value: null,
      validators: [{name: 'required'}],
    },
  },
})

const sendTGCode = () => {
  step.value = 3
  artCall({
    url: url.value,
    method: 'post',
  }).then()
}

watch(url, (val: string) => form.endpoint = val)
</script>
