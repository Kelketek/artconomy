<template>
  <v-flex class="xs12" :class="{md4: device.confirmed}">
    <v-card>
      <v-card-text>
        <v-layout row wrap>
          <v-flex xs12 text-xs-center>
            <h3>{{device.name}}</h3>
          </v-flex>
          <v-flex class="text-xs-center" xs12>
            <div v-html="image" class="qrcode" v-if="image"></div>
          </v-flex>
          <v-flex xs12 v-if="!device.confirmed" text-xs-center>
            Scan the above barcode with your phone or other device.
            If you are on the device, install one of the following apps:
            <ul>
              <li>Authy: <a href="https://itunes.apple.com/us/app/authy/id494168017">iPhone</a> or <a href="https://play.google.com/store/apps/details?id=com.authy.authy">Android</a></li>
              <li>Google Authenticator: <a href="https://itunes.apple.com/us/app/google-authenticator/id388497605">iPhone</a> or <a href="https://play.google.com/store/apps/details?id=com.google.android.apps.authenticator2">Android</a></li>
            </ul>
            ...then, <a :href="device.config_url">try clicking this link.</a>
            <p>Finally, enter the verification code generated below and hit 'Verify'.</p>
            <form @submit.prevent="$refs.verifyForm.submit">
              <ac-form-container :model="verifyModel" :schema="verifySchema" ref="verifyForm" :url="url" method="PATCH" :success="loadDevice" />
              <v-btn color="primary" type="submit">Verify</v-btn>
            </form>
          </v-flex>
          <v-flex xs12 v-else text-xs-center>
            <p>This device is set up for 2FA.</p>
            <ac-action :success="refreshDevices" color="red" :url="url" method="DELETE" :confirm="true">
              <div class="text-xs-left" slot="confirmation-text">Are you sure you wish to remove this 2FA device? Removing 2FA makes your account less secure. You should only do this if you've lost your device or will replace it.</div>
              Remove Device
            </ac-action>
          </v-flex>
        </v-layout>
      </v-card-text>
    </v-card>
  </v-flex>
</template>

<script>
  import QRCode from 'qrcode'
  import AcFormContainer from './ac-form-container'
  import Perms from '../mixins/permissions'
  import Viewer from '../mixins/viewer'
  import AcAction from './ac-action'
  import {EventBus} from '../lib'

  export default {
    name: 'ac-totp-device',
    components: {AcAction, AcFormContainer},
    mixins: [Perms, Viewer],
    props: ['totpDevice'],
    data () {
      return {
        QRCode,
        image: '',
        device: this.totpDevice,
        verifyModel: {
          code: '',
          id: this.totpDevice.id
        },
        verifySchema: {
          fields: [{
            type: 'v-text',
            inputType: 'number',
            model: 'code',
            name: 'code',
            label: 'Verification Code'
          }]
        }
      }
    },
    methods: {
      refreshDevices () {
        EventBus.$emit('refresh-totp')
      },
      renderCode () {
        if (this.device.confirmed) {
          this.image = ''
          return
        }
        QRCode.toString(this.device.config_url, {}, this.saveResult)
      },
      saveResult (err, string) {
        if (err) {
          console.log(err)
        }
        this.image = string
      },
      loadDevice (response) {
        this.device = response
      }
    },
    watch: {
      'device.confirmed' () {
        this.renderCode()
      }
    },
    computed: {
      url () {
        return `/api/profiles/v1/account/${this.username}/settings/two-factor/totp/${this.device.id}/`
      }
    },
    created () {
      this.renderCode()
    }
  }
</script>

<style scoped>
  .qrcode {
    width:160px;
    height:160px;
    margin-top:15px;
    display: inline-block;
  }
</style>