<template>
  <div>
    <v-layout row wrap>
      <v-flex>
        <p>Two Factor Authentication (2FA) helps keep your account secure. If someone discovers your password,
          they still will not be able to log in without being able to access a device you own.</p>
        <p>You can set up more than one device and more than one form of two factor authentication.</p>
      </v-flex>
    </v-layout>
    <v-layout v-if="canCreate">
      <v-flex>
        <h2>Set up a device (such as your Phone)</h2>
        <p>Your phone can be used to help you log in using a special app. Click the button below to get started.</p>
      </v-flex>
    </v-layout>
    <v-container fluid grid-list-md>
      <v-layout row wrap>
        <ac-totp-device
            v-for="device in ttopDevices"
            :key="device.id"
            :totp-device="device"
            :username="username"></ac-totp-device>
      </v-layout>
    </v-container>
    <v-layout row wrap>
      <v-flex xs12 v-if="canCreate" text-xs-center>
        <v-btn color="primary" @click="showNewDevice=true">Add new Device</v-btn>
      </v-flex>
    </v-layout>
    <ac-form-dialog v-model="showNewDevice" :model="newDeviceModel" :options="newDeviceOptions" :schema="newDeviceSchema" :success="loadDevices" :url="`${url}totp/`" />
    <v-card class="mt-2">
      <v-card-text>
        <v-layout row wrap>
          <v-flex xs12 v-if="tgDevice === false" text-xs-center>
            <h2>Set up 2FA with Telegram</h2>
            <p>You may also set up 2FA with <a href="https://telegram.org/">Telegram</a>. Telegram is a popular messenger, especially in artistic communities.</p>
            <v-btn color="primary" @click="createTG">Enable Telegram</v-btn>
          </v-flex>
          <v-flex xs12 v-if="tgDevice && !tgDevice.confirmed" text-xs-center>
            <h2><a :href="user.telegram_link" target="_blank" style="text-decoration: underline;">First: Click this link to connect Telegram to Artconomy!</a></h2>
            <p>Once you're connected, press this button to send a code! You can press it again if the code doesn't arrive after a while.</p>
            <p><v-btn color="primary" @click="sendTGCode">Send Code</v-btn></p>
            <p>Finally, enter the code in the field below, and you're all done!</p>
            <form @submit.prevent="$refs.verifyForm.submit">
              <ac-form-container :model="verifyModel" :schema="verifySchema" ref="verifyForm" :url="`${url}tg/`" method="PATCH" :success="loadTGDevice" />
              <v-btn color="primary" type="submit">Verify</v-btn>
            </form>
          </v-flex>
          <v-flex xs12 v-if="tgDevice && tgDevice.confirmed" text-xs-center>
            You are set up with Telegram for Two Factor Authentication.
          </v-flex>
          <v-flex xs12 text-xs-center v-if="tgDevice">
            <ac-action color="red" :url="`${this.url}tg/`" method="DELETE" :confirm="true" :success="noTGDevice">
              <div class="text-xs-left" slot="confirmation-text">Are you sure you wish to remove Telegram 2FA? Removing 2FA makes your account less secure. You should only do this if you no longer use the Telegram account on file or believe it has been compromised.</div>
              Remove Telegram 2FA
            </ac-action>
          </v-flex>
        </v-layout>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import {artCall, EventBus} from '../lib'
  import AcFormDialog from './ac-form-dialog'
  import AcTotpDevice from './ac-totp-device'
  import AcFormContainer from './ac-form-container'
  import AcAction from './ac-action'
  export default {
    components: {AcAction, AcFormContainer, AcTotpDevice, AcFormDialog},
    mixins: [Viewer, Perms],
    name: 'ac-setup-two-factor',
    data () {
      return {
        ttopDevices: null,
        showNewDevice: false,
        tgDevice: null,
        newDeviceModel: {
          name: ''
        },
        verifyModel: {
          code: ''
        },
        verifySchema: {
          fields: [{
            type: 'v-text',
            inputType: 'number',
            model: 'code',
            name: 'code',
            label: 'Verification Code'
          }]
        },
        newDeviceSchema: {
          fields: [
            {
              name: 'name',
              type: 'v-text',
              label: 'Device Name',
              model: 'name',
              required: true,
              hint: "Name of the device you're setting up. For instance, you could name it 'iPhone' or 'Android Phone'."
            }
          ]
        },
        newDeviceOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        }
      }
    },
    methods: {
      loadTTOP (response) {
        this.ttopDevices = response.results
      },
      deleteTG () {
        artCall(`${this.url}tg/`, 'DELETE', undefined, this.noTGDevice)
      },
      loadTGDevice (response) {
        this.tgDevice = response
      },
      noTGDevice () {
        this.tgDevice = false
      },
      sendTGCode () {
        artCall(`${this.url}tg/`, 'POST', undefined)
      },
      createTG () {
        artCall(`${this.url}tg/`, 'CREATE', undefined, this.loadTGDevice, this.noTGDevice)
      },
      loadDevices () {
        this.showNewDevice = false
        artCall(`${this.url}totp/`, 'GET', undefined, this.loadTTOP)
        artCall(`${this.url}tg/`, 'GET', undefined, this.loadTGDevice, this.noTGDevice)
      }
    },
    computed: {
      canCreate () {
        return this.ttopDevices && this.ttopDevices.length < 5
      },
      url () {
        return `/api/profiles/v1/account/${this.username}/settings/two-factor/`
      }
    },
    created () {
      this.loadDevices()
      EventBus.$on('refresh-totp', this.loadDevices)
    },
    destroyed () {
      EventBus.$off('refresh-totp', this.loadDevices)
    }
  }
</script>