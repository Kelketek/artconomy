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
                    <img :src="iphone" style="height: 10vh" alt="Smartphone"/>
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
      <v-col cols="12">
        <ac-load-section :controller="totpDevices">
          <template v-slot:default>
            <ac-totp-device
                v-for="device in totpDevices.list"
                :key="device.x!.id" :device="device" :username="username" />
          </template>
        </ac-load-section>
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

<script setup lang="ts">
import AcTotpDevice from './AcTotpDevice.vue'
import AcTgDevice from './AcTgDevice.vue'
import {BASE_URL} from '@/lib/lib.ts'
import {useList} from '@/store/lists/hooks.ts'
import {computed, watch} from 'vue'
import {useSingle} from '@/store/singles/hooks.ts'
import AcLoadSection from '@/components/wrappers/AcLoadSection.vue'
import type {SubjectiveProps, TGDevice, TOTPDevice} from '@/types/main'


const props = defineProps<SubjectiveProps>()

const url = computed(() => {
  return `/api/profiles/account/${props.username}/auth/two-factor/`
})

const iphone = new URL('/static/images/iphone.svg', BASE_URL).href
const telegramLogo = new URL('/static/images/telegram_logo.svg', BASE_URL).href

const totpDevices = useList<TOTPDevice>('totpDevices', {endpoint: `${url.value}totp/`})
totpDevices.firstRun()

const tgDevice = useSingle<TGDevice>('tgDevice', {endpoint: `${url.value}tg/`})
tgDevice.get().catch(() => {
  tgDevice.ready = true
})

const noDevice = computed(() => (
  tgDevice.x === null
  && (tgDevice.ready || tgDevice.deleted)
  && totpDevices.ready
  && totpDevices.list.length === 0
))

watch(url, (val: string) => {
  tgDevice.endpoint = val + 'tg/'
  totpDevices.endpoint = val + 'totp/'
})
</script>
