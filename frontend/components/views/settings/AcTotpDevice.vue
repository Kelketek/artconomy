<template>
  <v-col v-if="device.x">
    <v-row>
      <v-col v-if="device.x.confirmed" cols="12">
        <v-col cols="12" sm="4" offset-sm="4">
          <v-card class="elevation-7">
            <v-card-text>
              <v-row no-gutters>
                <v-col
                  class="px-2 text-center"
                  cols="4"
                  sm="12"
                  order="2"
                  order-sm="1"
                >
                  <img :src="iphone" style="height: 10vh" alt="Smartphone" />
                </v-col>
                <v-col
                  cols="8"
                  sm="12"
                  order="1"
                  order-sm="2"
                  class="two-factor-label text-center"
                >
                  <p>
                    <strong
                      >You have Two Factor authentication enabled on your
                      phone!</strong
                    >
                  </p>
                </v-col>
                <v-col class="text-center" cols="12" order="2" order-sm="3">
                  <p>
                    You will be prompted for a code on each login, keeping your
                    account extra secure.
                  </p>
                  <p v-if="device.x.name !== 'Phone'">
                    <strong>Device Name: {{ device.x.name }}</strong>
                  </p>
                </v-col>
                <v-col class="text-center" cols="12" order="3">
                  <ac-confirmation
                    :action="() => device.delete().then(() => emit('removed'))"
                  >
                    <template #default="{ on }">
                      <v-btn
                        color="red"
                        class="delete-phone-2fa"
                        variant="elevated"
                        v-on="on"
                      >
                        Disable Phone 2FA
                      </v-btn>
                    </template>
                    <template #confirmation-text>
                      <div>
                        Are you sure you wish to remove 2FA? Removing 2FA makes
                        your account less secure. You should only do this if you
                        no longer have this phone, or are expecting to get a new
                        one.
                      </div>
                    </template>
                  </ac-confirmation>
                </v-col>
              </v-row>
            </v-card-text>
          </v-card>
        </v-col>
      </v-col>
      <v-col v-else cols="12">
        <v-stepper v-model="step" non-linear>
          <v-stepper-header>
            <v-stepper-item :value="1">
              <template #title> Install App </template>
            </v-stepper-item>
            <v-stepper-item :value="2">
              <template #title> Add Artconomy </template>
            </v-stepper-item>
            <v-stepper-item :value="3">
              <template #title> Verify Code </template>
            </v-stepper-item>
          </v-stepper-header>
          <v-stepper-window v-model="step">
            <v-stepper-window-item :value="1">
              <v-row no-gutters class="pb-2">
                <v-col class="text-center" cols="12" sm="4" offset-sm="1">
                  <v-card class="elevation-7">
                    <v-card-text>
                      <v-row no-gutters>
                        <v-col cols="12" class="text-center">
                          <h3>Authy</h3>
                        </v-col>
                        <v-col cols="12">
                          <img
                            :src="authy"
                            style="min-width: 60%; max-width: 75%"
                            alt="Authy"
                          />
                        </v-col>
                        <v-col cols="12">
                          <a
                            href="https://play.google.com/store/apps/details?id=com.authy.authy"
                            target="_blank"
                            @click="step = 2"
                          >
                            <img
                              :src="playStore"
                              alt="Download Authy on the Google Play Store"
                            />
                          </a>
                        </v-col>
                        <v-col cols="12">
                          <a
                            target="_blank"
                            href="https://itunes.apple.com/us/app/authy/id494168017"
                            @click="step = 2"
                          >
                            <img
                              :src="appStore"
                              alt="Download Authy on Apple's App Store"
                            />
                          </a>
                        </v-col>
                      </v-row>
                    </v-card-text>
                  </v-card>
                </v-col>
                <v-col class="text-center" cols="12" sm="4" offset-sm="1">
                  <v-card class="elevation-7">
                    <v-card-text class="text-center">
                      <v-row no-gutters>
                        <v-col cols="12" class="text-center">
                          <h3>Google Authenticator</h3>
                        </v-col>
                        <v-col cols="12">
                          <img
                            :src="authenticator"
                            style="min-width: 60%; max-width: 75%"
                            alt="Google Authenticator"
                          />
                        </v-col>
                        <v-col cols="12">
                          <a
                            href="https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2"
                            target="_blank"
                            @click="step = 2"
                          >
                            <img
                              :src="playStore"
                              alt="Download Google Authenticator on the Play Store"
                            />
                          </a>
                        </v-col>
                        <v-col cols="12">
                          <a
                            target="_blank"
                            href="https://itunes.apple.com/us/app/google-authenticator/id388497605"
                            @click="step = 2"
                          >
                            <img
                              :src="appStore"
                              alt="Download Google Authenticator on Apple's App Store"
                            />
                          </a>
                        </v-col>
                      </v-row>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
              <v-card-actions row wrap>
                <v-spacer />
                <v-btn variant="flat" @click="device.delete"> Cancel </v-btn>
                <v-btn color="primary" variant="flat" @click="step = 2">
                  Continue
                </v-btn>
              </v-card-actions>
            </v-stepper-window-item>
            <v-stepper-window-item :value="2">
              <v-card class="lighten-1">
                <v-card-text>
                  <v-row no-gutters>
                    <v-col class="text-center" cols="12">
                      <qr-code
                        v-if="device.x && !device.x.confirmed"
                        :data="device.x.config_url"
                      />
                    </v-col>
                    <v-col class="text-center" cols="12">
                      Scan the barcode above with your phone or other device. If
                      you are on the device, you can also
                      <a :href="device.x!.config_url">click this link.</a>
                    </v-col>
                  </v-row>
                </v-card-text>
              </v-card>
              <v-card-actions row wrap>
                <v-spacer />
                <v-btn variant="flat" @click="device.delete"> Cancel </v-btn>
                <v-btn color="black" variant="flat" @click="step = 1">
                  Back
                </v-btn>
                <v-btn color="primary" variant="flat" @click="step = 3">
                  Continue
                </v-btn>
              </v-card-actions>
            </v-stepper-window-item>
            <v-stepper-window-item :value="3">
              <v-card class="lighten-1">
                <v-card-text>
                  <v-row no-gutters>
                    <v-col class="text-center" cols="12">
                      <p>
                        Finally, enter the code in the field below, and you're
                        all done!
                      </p>
                    </v-col>
                    <v-col
                      class="text-center"
                      cols="12"
                      sm="8"
                      offset-sm="2"
                      md="4"
                      offset-md="4"
                    >
                      <ac-form
                        @submit.prevent="totpForm.submitThen(device.setX)"
                      >
                        <ac-form-container v-bind="totpForm.bind">
                          <v-text-field
                            v-mask-token
                            v-bind="totpForm.fields.code.bind"
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
              <v-card-actions row wrap>
                <v-spacer />
                <v-btn variant="flat" @click="device.delete"> Cancel </v-btn>
                <v-btn color="black" variant="flat" @click="step = 2">
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
import AcFormContainer from "@/components/wrappers/AcFormContainer.vue"
import AcConfirmation from "@/components/wrappers/AcConfirmation.vue"
import { SingleController } from "@/store/singles/controller.ts"
import AcForm from "@/components/wrappers/AcForm.vue"
import { BASE_URL } from "@/lib/lib.ts"
import { vMaskToken } from "@/lib/vMask.ts"
import { ref, watch } from "vue"
import { useForm } from "@/store/forms/hooks.ts"
import type { SubjectiveProps, TOTPDevice } from "@/types/main"
import QrCode from "@/components/wrappers/QrCode.ts"

const props = defineProps<
  { device: SingleController<TOTPDevice> } & SubjectiveProps
>()

const step = ref(1)

const appStore = new URL("/static/images/Appstore.svg", BASE_URL).href
const playStore = new URL("/static/images/Playstore.svg", BASE_URL).href
const authenticator = new URL("/static/images/authenticator.png", BASE_URL).href
const authy = new URL("/static/images/authy.png", BASE_URL).href
const iphone = new URL("/static/images/iphone.svg", BASE_URL).href

const emit = defineEmits<{ removed: [] }>()

const totpForm = useForm(props.device.x!.id + "_totpForm", {
  method: "patch",
  endpoint: props.device.endpoint,
  fields: {
    code: {
      validators: [{ name: "required" }],
      value: null,
    },
  },
})

watch(
  () => props.device.endpoint,
  (val: string) => {
    totpForm.endpoint = val
  },
)
</script>
