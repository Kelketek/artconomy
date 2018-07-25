<template>
  <div>
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
    <ac-form-dialog v-model="showNewDevice" :model="newDeviceModel" :options="newDeviceOptions" :schema="newDeviceSchema" :success="loadDevices" :url="url" />
  </div>
</template>

<script>
  import Viewer from '../mixins/viewer'
  import Perms from '../mixins/permissions'
  import {artCall, EventBus} from '../lib'
  import AcFormDialog from './ac-form-dialog'
  import AcTotpDevice from './ac-totp-device'
  export default {
    components: {AcTotpDevice, AcFormDialog},
    mixins: [Viewer, Perms],
    name: 'ac-setup-two-factor',
    data () {
      return {
        ttopDevices: null,
        showNewDevice: false,
        newDeviceModel: {
          name: ''
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
      loadDevices () {
        this.showNewDevice = false
        artCall(this.url, 'GET', undefined, this.loadTTOP)
      }
    },
    computed: {
      canCreate () {
        return this.ttopDevices && this.ttopDevices.length < 5
      },
      url () {
        return `/api/profiles/v1/account/${this.username}/settings/two-factor/totp/`
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