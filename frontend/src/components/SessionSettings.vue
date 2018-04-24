<template>
  <v-container>
    <v-layout row wrap>
      <v-flex v-if="!$root.user.username">
        <form class="mt-3">
          <ac-form-container ref="settingsForm" :schema="settingsSchema" :model="settingsModel"
                             :options="settingsOptions" :success="updateUser"
                             :url="`/api/profiles/v1/session/settings/`"
                             method="PATCH"
                             :reset-after="false"
          >
            <v-btn type="submit" color="primary" @click.prevent="$refs.settingsForm.submit">Update</v-btn>
            <i v-if="$refs.settingsForm && $refs.settingsForm.saved" class="fa fa-check" style="color: green"></i>
          </ac-form-container>
        </form>
      </v-flex>
      <v-flex v-else text-xs-center>
        You are already logged in. Please visit the
        <router-link :to="{name: 'Settings', params: {username: this.$root.user.username}}">settings page</router-link>
        to adjust your rating settings.
      </v-flex>
    </v-layout>
  </v-container>
</template>

<script>
  import {ratings} from '../lib'
  import VueFormGenerator from 'vue-form-generator'
  import AcFormContainer from './ac-form-container'

  export default {
    name: 'VisitorOverride',
    components: {AcFormContainer},
    data () {
      return {
        settingsModel: {
          rating: this.$root.user.rating
        },
        settingsSchema: {
          fields: [{
            type: 'v-select',
            label: 'Max Content Rating',
            model: 'rating',
            required: false,
            validator: VueFormGenerator.validators.boolean,
            hint: 'By setting this value, you are affirming that the content this rating represents is legal to view in your area and you meet all legal qualifications (such as age) to view it.',
            selectOptions: {
              hideNoneSelectedText: true
            },
            values: ratings
          }]
        },
        settingsOptions: {
          validateAfterLoad: false,
          validateAfterChanged: true
        }
      }
    },
    methods: {
      updateUser (response) {
        for (let key of Object.keys(response)) {
          this.$root.user[key] = response[key]
        }
      }
    },
    watch: {
      '$root.user.username': function (oldVal, newVal) {
        if (newVal) {
          this.$router.history.push({name: 'Settings', params: {username: newVal}})
        }
      }
    }
  }
</script>

<style scoped>

</style>